"""
step_02_retrieval.py — Load canonical structure for subdomain (deterministic).
Falls back to scope.boundaries if source file is unavailable.
Type: deterministic
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR
from common import (
    sha256_file, now_iso, artifact_dir, write_json, register_artifact,
    emit_state, read_json,
)

STEP = "02_retrieval"


def run(run_id: str, scope: dict, scope_hash: str, kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "canonical_structure": {...}, "structure_hash": "..."}
    """
    print(f"[{STEP}] run={run_id}")
    emit_state(WORK_DIR, run_id, "step.start", STEP, {})

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "canonical_structure.json"

    canonical_source = scope.get("canonical_source", "unknown")
    boundaries       = scope.get("boundaries", [])

    if not boundaries:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "retrieval_empty",
                    "reason": "scope.boundaries empty and no source file"})
        return {"status": "stop", "stop_code": "retrieval_empty"}

    # Build chapters from scope.boundaries (fallback strategy)
    chapters = []
    for i, boundary in enumerate(boundaries, start=1):
        # Split "Title: description" pattern if present
        if ":" in boundary:
            parts = boundary.split(":", 1)
            title = parts[0].strip()
            desc  = parts[1].strip()
        else:
            title = boundary.strip()
            desc  = None
        chapters.append({"index": i, "title": title, "description": desc})

    structure = {
        "subdomain_id":     scope.get("subdomain_id", ""),
        "subdomain":        scope.get("subdomain", ""),
        "canonical_source": canonical_source,
        "retrieval_method": "fallback_from_scope",
        "source_available": False,
        "chapters":         chapters,
        "chapter_count":    len(chapters),
        "retrieved_at":     now_iso(),
    }

    write_json(out_path, structure)
    structure_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:canonical_structure",
                                       out_path, content_state="candidate", step=STEP)

    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"chapter_count": len(chapters),
                "retrieval_method": "fallback_from_scope",
                "warning": "retrieval_fallback_used"})

    print(f"  [done] {len(chapters)} chapters (fallback from scope.boundaries)")
    return {"status": "ok", "canonical_structure": structure,
            "structure_hash": structure_hash}
