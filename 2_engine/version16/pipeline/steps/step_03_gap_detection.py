"""
step_03_gap_detection.py v14 — Detect missing/underrepresented categories.
Type: LLM | Model: 35b | Prompt: prompts/03_gap_detection.md
Snapshot after: yes
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES
from constants import STEP_MODEL_CLASS
from common import (
    sha256_file, parse_json_response,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
    create_snapshot, llm_call,
)
from prompt_loader import load_prompt

STEP     = "03_enrichment_03_gap_detection"
STEP_KEY = "03_gap_detection"


def validate_output(obj: dict) -> list[str]:
    errors = []
    if "overall_coverage" not in obj:
        errors.append("missing field: overall_coverage")
    if obj.get("overall_coverage") not in ("good", "acceptable", "poor"):
        errors.append("overall_coverage must be good|acceptable|poor")
    if "missing_topics" not in obj:
        errors.append("missing field: missing_topics")
    if "covered_topics" not in obj:
        errors.append("missing field: covered_topics")
    return errors


def run(run_id: str, scope: dict, scope_hash: str,
        structure: dict, structure_hash: str,
        normalized: dict, normalized_hash: str,
        kb_snapshot_id: str, tel=None) -> dict:
    print(f"[{STEP_KEY}] run={run_id}")

    prompt_text, prompt_meta = load_prompt(STEP_KEY)
    prompt_hash = prompt_meta["hash"]

    inputs = {
        "normalized_categories_hash": normalized_hash,
        "scope_hash":                 scope_hash,
        "canonical_structure_hash":   structure_hash,
        "kb_snapshot_id":             kb_snapshot_id,
        "prompt_hash":                prompt_hash,
    }
    task_id = make_task_id(STEP_KEY, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "gap_detection.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        gap = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP_KEY, {"task_id": task_id})
        if tel:
            tel.record_cache_hit(STEP_KEY, task_id)
        return {"status": "ok", "gap_detection": gap, "gap_hash": sha256_file(out_path)}

    if tel:
        tel.record_cache_miss(STEP_KEY, task_id)
    emit_state(WORK_DIR, run_id, "step.start", STEP_KEY,
               {"task_id": task_id, "prompt_hash": prompt_hash})

    prompt = prompt_text.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        structure_json=json.dumps(structure, indent=2, ensure_ascii=False),
        categories_json=json.dumps(normalized, indent=2, ensure_ascii=False),
    )

    raw = llm_call(prompt, retries=DEFAULT_RETRIES, tel=tel, step=STEP_KEY,
                   prompt_hash=prompt_hash, model_class=STEP_MODEL_CLASS.get(STEP_KEY, "35b"))
    gap = parse_json_response(raw)

    if gap is None:
        if tel:
            tel.record_parse(STEP_KEY, prompt_hash, success=False, errors=["non-JSON"])
        emit_state(WORK_DIR, run_id, "step.stop", STEP_KEY,
                   {"stop_code": "llm_output_invalid", "reason": "non-JSON"})
        return {"status": "stop", "stop_code": "llm_output_invalid"}

    errors = validate_output(gap)
    if errors:
        if tel:
            tel.record_parse(STEP_KEY, prompt_hash, success=False, errors=errors)
        emit_state(WORK_DIR, run_id, "step.stop", STEP_KEY,
                   {"stop_code": "llm_output_invalid", "reason": str(errors)})
        return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    if tel:
        tel.record_parse(STEP_KEY, prompt_hash, success=True)
        tel.record_content(STEP_KEY, {
            "missing_topics_count":           len(gap.get("missing_topics", [])),
            "covered_topics_count":           len(gap.get("covered_topics", [])),
            "underrepresented_categories":    len(gap.get("underrepresented_categories", [])),
            "oversized_categories":           len(gap.get("oversized_categories", [])),
            "overall_coverage_score":         {"good": 1.0, "acceptable": 0.5, "poor": 0.0}
                                              .get(gap.get("overall_coverage", "poor"), 0.0),
        })

    write_json(out_path, gap)
    gap_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:gap_detection",
                                 out_path, content_state="candidate", step=STEP_KEY)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP_KEY)

    snap_id = create_snapshot(WORK_DIR, run_id, "pre_generation")
    emit_state(WORK_DIR, run_id, "step.done", STEP_KEY,
               {"task_id": task_id, "overall_coverage": gap.get("overall_coverage"),
                "snapshot_id": snap_id, "prompt_hash": prompt_hash})

    print(f"  [done] coverage={gap.get('overall_coverage')} "
          f"missing={len(gap.get('missing_topics', []))}")
    return {"status": "ok", "gap_detection": gap, "gap_hash": gap_hash}
