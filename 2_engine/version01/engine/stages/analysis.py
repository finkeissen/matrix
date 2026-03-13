import time
from pathlib import Path
from engine.utils.fs import write_json

def run(run_dir: Path) -> Path:
    out = run_dir / "analysis.json"
    write_json(out, {"run_id": run_dir.name, "ts": time.time(), "notes": "analysis stub v0.1.0"})
    return out
