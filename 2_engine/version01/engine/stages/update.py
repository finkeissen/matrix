import time
from pathlib import Path
from engine.utils.fs import write_json

def run(run_dir: Path) -> Path:
    patch_dir = run_dir / "matrix_patch"
    patch_dir.mkdir(exist_ok=True)
    out = patch_dir / "patch.json"
    write_json(out, {"run_id": run_dir.name, "ts": time.time(), "ops": []})
    return out
