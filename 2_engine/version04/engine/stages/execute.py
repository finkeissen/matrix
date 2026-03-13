"""Execute stage: run the job command declared in job.json.

Rules of thumb learned from prior runs:
- write *all* stdout/stderr into logs/ so it is archived with the run
- create outputs only under out/ (so archiving and review are predictable)
- avoid /tmp: systemd services may run with PrivateTmp=true

Output:
  - logs/job.<timestamp>.log
  - logs/job.<timestamp>.status.json
  - (job-defined files under out/)
"""

import json, os, subprocess, time
from pathlib import Path
from engine.utils.fs import read_json

def run(run_dir: Path) -> int:
    job = read_json(run_dir / "job.json")
    cmd = job["cmd"]
    cwd = (run_dir / job.get("cwd", ".")).resolve()
    timeout = int(job.get("timeout_sec", 3600))

    (run_dir / "logs").mkdir(exist_ok=True)
    (run_dir / "out").mkdir(exist_ok=True)

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
    rc = 1
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
    return rc
