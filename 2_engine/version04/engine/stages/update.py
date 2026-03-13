"""Update stage: produce a patch proposal (currently empty scaffold).

The engine does not apply changes directly to upstream knowledge bases.
Instead it emits a patch artifact under matrix_patch/ that a human (or an
external, policy-governed process) can review and apply.
"""

import time
from pathlib import Path
from engine.utils.fs import write_json

def run(run_dir: Path) -> Path:
    patch_dir = run_dir / "matrix_patch"
    patch_dir.mkdir(exist_ok=True)
    out = patch_dir / "patch.json"
    write_json(out, {"run_id": run_dir.name, "ts": time.time(), "ops": []})
    return out
