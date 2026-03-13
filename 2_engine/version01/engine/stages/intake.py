import time
from pathlib import Path
from engine.utils.hashing import sha256_file
from engine.utils.fs import write_json

def run(run_dir: Path) -> Path:
    raw = run_dir / "raw"
    scripts = run_dir / "scripts"
    files = []
    for base in [raw, scripts]:
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file():
                    files.append({"path": p.relative_to(run_dir).as_posix(), "sha256": sha256_file(p)})
    manifest = {"run_id": run_dir.name, "created_at": time.time(), "files": files}
    out = run_dir / "manifest.json"
    write_json(out, manifest)
    return out
