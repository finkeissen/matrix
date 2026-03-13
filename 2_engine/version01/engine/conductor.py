import json, os, shutil, subprocess, time
from pathlib import Path
from engine.utils.fs import read_json
from engine.stages import intake, analysis, extract, canonicalize, validate, update, self_control

def _ensure_dirs(runs_root: Path):
    for p in ["incoming","active","done","failed",".state"]:
        (runs_root / p).mkdir(parents=True, exist_ok=True)

def _incoming(runs_root: Path):
    inc = runs_root / "incoming"
    runs = [p for p in inc.iterdir() if p.is_dir() and not p.name.startswith(".")]
    return sorted(runs, key=lambda p: p.stat().st_mtime)

def _claim(runs_root: Path, run_dir: Path):
    dest = runs_root / "active" / run_dir.name
    try:
        run_dir.rename(dest)
        return dest
    except Exception:
        return None

def _finalize(runs_root: Path, run_dir: Path, ok: bool):
    target = runs_root / ("done" if ok else "failed") / run_dir.name
    try:
        run_dir.rename(target)
    except Exception:
        shutil.copytree(run_dir, target, dirs_exist_ok=True)
        shutil.rmtree(run_dir, ignore_errors=True)

def run_single(run_dir: Path) -> int:
    started = time.time()
    (run_dir / "logs").mkdir(exist_ok=True)

    intake.run(run_dir)
    analysis.run(run_dir)
    extract.run(run_dir)
    canonicalize.run(run_dir)
    validate.run(run_dir)

    approved = bool(read_json(run_dir / "decision.json").get("approved"))
    rc = 1

    if approved:
        job = read_json(run_dir / "job.json")
        cmd = job["cmd"]
        cwd = (run_dir / job.get("cwd", ".")).resolve()
        timeout = int(job.get("timeout_sec", 3600))

        ts = time.strftime("%Y%m%d-%H%M%S")
        log_path = run_dir / "logs" / f"job.{ts}.log"
        status_path = run_dir / "logs" / f"job.{ts}.status.json"

        env = os.environ.copy()
        env_file = run_dir / "config.env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

        err = None
        start = time.time()
        with open(log_path, "w", encoding="utf-8") as log:
            log.write(f"[engine] cmd={cmd}\n")
            log.write(f"[engine] cwd={cwd}\n")
            log.flush()
            try:
                p = subprocess.Popen(cmd, cwd=str(cwd), env=env, stdout=log, stderr=subprocess.STDOUT, text=True)
                try:
                    rc = p.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    err = f"timeout after {timeout}s"
                    log.write(f"[engine] {err}\n")
                    log.flush()
                    try:
                        p.terminate(); p.wait(timeout=10)
                    except Exception:
                        try: p.kill()
                        except Exception: pass
                    rc = 124
            except Exception as e:
                err = repr(e); rc = 1
        end = time.time()
        status_path.write_text(json.dumps({
            "started_at": start, "finished_at": end, "duration_sec": round(end-start,3),
            "returncode": rc, "error": err
        }, indent=2) + "\n", encoding="utf-8")

        update.run(run_dir)

    self_control.run(run_dir, started_at=started)
    return 0 if rc == 0 else 1

def daemon_loop(runs_root: Path, poll_sec: float = 1.0) -> int:
    _ensure_dirs(runs_root)
    hb = runs_root / ".state" / "engine.heartbeat"
    while True:
        hb.write_text(json.dumps({"ts": time.time(), "status": "idle"}) + "\n", encoding="utf-8")
        inc = _incoming(runs_root)
        if not inc:
            time.sleep(poll_sec); continue
        claimed = _claim(runs_root, inc[0])
        if not claimed:
            time.sleep(poll_sec); continue
        hb.write_text(json.dumps({"ts": time.time(), "status": f"running:{claimed.name}"}) + "\n", encoding="utf-8")
        rc = run_single(claimed)
        _finalize(runs_root, claimed, ok=(rc == 0))
