"""
step_03_normalize.py — Soft-normalize category names (deterministic, no LLM).
Type: deterministic
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR
from common import (
    sha256_file, artifact_dir, write_json, register_artifact, emit_state,
)

STEP = "03_enrichment_02_normalize"

# Words preserved as-is (fully uppercase in original = acronyms)
def _is_acronym(word: str) -> bool:
    return len(word) > 1 and word.isupper()

def _title_case_preserve_acronyms(text: str) -> str:
    words = text.split(" ")
    result = []
    for w in words:
        if _is_acronym(w):
            result.append(w)
        else:
            result.append(w.capitalize())
    return " ".join(result)

def normalize_name(name: str) -> str:
    # 1. Strip
    n = name.strip()
    # 2. Collapse internal whitespace
    n = re.sub(r"\s+", " ", n)
    # 3. Normalize special chars before title case
    n = n.replace("&", "and").replace("/", "-")
    # 4. Title Case, preserve acronyms
    n = _title_case_preserve_acronyms(n)
    return n


def run(run_id: str, categories: dict, categories_hash: str, kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "normalized_categories": {...}, "normalized_hash": "..."}
    """
    print(f"[{STEP}] run={run_id}")
    emit_state(WORK_DIR, run_id, "step.start", STEP, {})

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "normalized_categories.json"

    items_in = categories.get("items", [])
    if not items_in:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "deterministic_step_error", "reason": "items empty"})
        return {"status": "stop", "stop_code": "deterministic_step_error"}

    seen       = {}   # normalized_name → first index
    normalized = []
    duplicates_removed = 0

    for raw_item in items_in:
        name_orig = raw_item.get("name", "")
        name_norm = normalize_name(name_orig)
        key       = name_norm.lower()

        if key in seen:
            duplicates_removed += 1
            continue

        seen[key] = True
        normalized.append({
            "index":                  len(normalized) + 1,
            "name_normalized":        name_norm,
            "name_original":          name_orig,
            "description":            raw_item.get("description", ""),
            "canonical_chapter_ref":  raw_item.get("canonical_chapter_ref"),
            "estimated_problem_count": raw_item.get("estimated_problem_count", 0),
        })

    result = {
        "subdomain":           categories.get("subdomain", ""),
        "subdomain_id":        categories.get("subdomain_id", ""),
        "category_count":      len(normalized),
        "duplicates_removed":  duplicates_removed,
        "items":               normalized,
    }

    write_json(out_path, result)
    norm_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:normalized_categories",
                                  out_path, content_state="candidate", step=STEP)

    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"category_count": len(normalized),
                "duplicates_removed": duplicates_removed})

    print(f"  [done] {len(normalized)} categories ({duplicates_removed} dupes removed)")
    return {"status": "ok", "normalized_categories": result, "normalized_hash": norm_hash}
