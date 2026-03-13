import json, shutil, time
from pathlib import Path
from engine.utils.fs import read_json
from engine.stages import intake, validate, execute, update, self_control

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
    validate.run(run_dir)
    decision = read_json(run_dir / "decision.json")
    approved = bool(decision.get("approved"))
    outcome = decision.get("outcome", "inadmissible")

    rc = 1
    if approved and outcome == "admissible":
        rc = execute.run(run_dir)
        if rc == 0:
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
