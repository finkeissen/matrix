import time
from pathlib import Path
from engine.utils.fs import write_json

def run(run_dir: Path, started_at: float) -> Path:
    finished = time.time()
    metrics = {"run_id": run_dir.name, "started_at": started_at, "finished_at": finished,
               "duration_sec": round(finished - started_at, 3)}
    write_json(run_dir / "metrics.json", metrics)
    (run_dir / "run_report.md").write_text(
        f"# Run Report\n\n- run_id: {run_dir.name}\n- outcome: see decision.json\n- duration_sec: {metrics['duration_sec']}\n",
        encoding="utf-8"
    )
    return run_dir / "metrics.json"
