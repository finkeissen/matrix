import time
from pathlib import Path
from engine.utils.fs import write_json

def run(run_dir: Path) -> Path:
    ok = (run_dir / "job.json").exists()
    report = {"run_id": run_dir.name, "ts": time.time(), "approved": bool(ok),
              "reasons": [] if ok else ["missing job.json"]}
    write_json(run_dir / "validation_report.json", report)
    write_json(run_dir / "decision.json", {"approved": bool(ok)})
    return run_dir / "validation_report.json"
