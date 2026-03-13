"""Intake stage: create a manifest of input files.

The manifest records SHA-256 checksums for all relevant inputs so that archived runs
remain auditable. We deliberately exclude:
  - logs/ and out/ (runtime artifacts and outputs)
  - matrix_patch/ (engine-produced patch output)
  - decision/validation/metrics files (engine-produced control artifacts)

Output:
  - manifest.json
"""

import time
from pathlib import Path
from engine.utils.hashing import sha256_file
from engine.utils.fs import write_json

def run(run_dir: Path) -> Path:
    raw = run_dir / "raw"
    scripts = run_dir / "scripts"
    files = []
    for base in [raw, scripts, run_dir]:
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file() and p.name not in {"validation_report.json","decision.json","metrics.json"}:
                    rel = p.relative_to(run_dir).as_posix()
                    if rel.startswith("logs/") or rel.startswith("out/") or rel.startswith("matrix_patch/"):
                        continue
                    files.append({"path": rel, "sha256": sha256_file(p)})
    manifest = {"run_id": run_dir.name, "created_at": time.time(), "files": files}
    out = run_dir / "manifest.json"
    write_json(out, manifest)
    return out
