"""
step_04b_generation_review.py v14 — Review and refine problems draft (per category).
Type: LLM | Model: 122b | Prompt: prompts/04b_generation_review.md
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES
from constants import STEP_MODEL_CLASS
from common import (
    sha256_file, sha256_obj, parse_json_response,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
    supersede_artifact, llm_call,
)
from prompt_loader import load_prompt

STEP = "04b_generation_review"


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain_id", "category", "problems", "problem_count",
                  "problems_added", "problems_removed", "problems_modified",
                  "changes_made"]:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if "problems" in obj:
        if not obj["problems"]:
            errors.append("problems array is empty")
        for p in obj["problems"]:
            for f in ["title", "problem_statement", "difficulty", "answer_type",
                      "canonical_source", "verifiable", "hallucination_risk",
                      "requires_context", "tags"]:
                if f not in p:
                    errors.append(f"problem missing field '{f}': {p.get('title','?')}")
            if len(p.get("title", "")) > 80:
                errors.append(f"title exceeds 80 chars: {p.get('title','?')[:60]}…")
    if "problems" in obj and "problem_count" in obj:
        if obj["problem_count"] != len(obj["problems"]):
            errors.append(f"problem_count mismatch")
    return errors


def run(run_id: str, scope: dict, scope_hash: str,
        draft: dict, draft_hash: str,
        category: dict,
        gap_detection: dict, gap_hash: str,
        kb_snapshot_id: str,
        prior_reviewed_key: str = None,
        tel=None) -> dict:

    cat_idx  = category["index"]
    cat_name = category["name_normalized"]
    print(f"[{STEP}] category={cat_idx}:{cat_name} run={run_id}")

    if prior_reviewed_key:
        supersede_artifact(WORK_DIR, run_id, prior_reviewed_key)

    prompt_text, prompt_meta = load_prompt(STEP)
    prompt_hash = prompt_meta["hash"]

    cat_hash = sha256_obj({
        "index": cat_idx, "name_normalized": cat_name,
        "description": category.get("description", ""),
    })
    inputs = {
        "problems_draft_hash": draft_hash,
        "scope_hash":          scope_hash,
        "gap_detection_hash":  gap_hash if gap_detection else None,
        "category_index":      cat_idx,
        "category_hash":       cat_hash,
        "kb_snapshot_id":      kb_snapshot_id,
        "prompt_hash":         prompt_hash,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, f"{STEP}/cat_{cat_idx:02d}")
    out_path = out_dir / "problems_reviewed.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit cat={cat_idx}")
        reviewed = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP,
                   {"task_id": task_id, "category_index": cat_idx})
        if tel:
            tel.record_cache_hit(STEP, task_id)
        return {"status": "ok", "problems_reviewed": reviewed,
                "reviewed_hash": sha256_file(out_path), "category_index": cat_idx}

    if tel:
        tel.record_cache_miss(STEP, task_id)
    emit_state(WORK_DIR, run_id, "step.start", STEP,
               {"task_id": task_id, "category_index": cat_idx, "prompt_hash": prompt_hash})

    prompt = prompt_text.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        category_name=cat_name,
        category_index=cat_idx,
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        draft_json=json.dumps(draft, indent=2, ensure_ascii=False),
        gap_json=json.dumps(gap_detection or {}, indent=2, ensure_ascii=False),
    )

    raw      = llm_call(prompt, retries=DEFAULT_RETRIES, tel=tel, step=STEP,
                        prompt_hash=prompt_hash, model_class=STEP_MODEL_CLASS.get(STEP, "122b"))
    reviewed = parse_json_response(raw)

    if reviewed is None:
        if tel:
            tel.record_parse(STEP, prompt_hash, success=False, errors=["non-JSON"])
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "category_index": cat_idx})
        return {"status": "stop", "stop_code": "llm_output_invalid",
                "category_index": cat_idx}

    errors = validate_output(reviewed)
    if errors:
        if tel:
            tel.record_parse(STEP, prompt_hash, success=False, errors=errors)
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors),
                    "category_index": cat_idx})
        return {"status": "stop", "stop_code": "llm_output_invalid",
                "errors": errors, "category_index": cat_idx}

    if tel:
        tel.record_parse(STEP, prompt_hash, success=True)
        draft_count    = len(draft.get("problems", []))
        reviewed_count = len(reviewed.get("problems", []))
        tel.record_content(STEP, {
            "category_index":    cat_idx,
            "problems_in_draft": draft_count,
            "problems_reviewed": reviewed_count,
            "problems_added":    reviewed.get("problems_added", 0),
            "problems_removed":  reviewed.get("problems_removed", 0),
            "problems_modified": reviewed.get("problems_modified", 0),
            "net_change":        reviewed_count - draft_count,
        })

    reviewed["problem_count"] = len(reviewed["problems"])
    write_json(out_path, reviewed)
    reviewed_key  = f"{STEP}:cat_{cat_idx:02d}:problems_reviewed"
    reviewed_hash = register_artifact(WORK_DIR, run_id, reviewed_key,
                                      out_path, content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "category_index": cat_idx,
                "problem_count": reviewed["problem_count"],
                "problems_added": reviewed.get("problems_added", 0),
                "problems_removed": reviewed.get("problems_removed", 0),
                "prompt_hash": prompt_hash})

    print(f"  [done] cat={cat_idx} problems={reviewed['problem_count']} "
          f"+{reviewed.get('problems_added',0)}/-{reviewed.get('problems_removed',0)}")
    return {"status": "ok", "problems_reviewed": reviewed,
            "reviewed_hash": reviewed_hash, "reviewed_key": reviewed_key,
            "category_index": cat_idx}
