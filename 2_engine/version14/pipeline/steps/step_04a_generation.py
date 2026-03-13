"""
step_04a_generation.py v14 — Generate atomic problems draft (per category).
Type: LLM | Model: 35b | Prompt: prompts/04a_generation.md
Instantiated ×N, once per normalized category.
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
    llm_call,
)
from prompt_loader import load_prompt

STEP = "04a_generation"

GAP_SECTION_TEMPLATE = """Known coverage gaps for this category (from gap analysis — prioritize these):
{gaps_json}"""


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain_id", "category", "problems", "problem_count"]:
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
            errors.append(f"problem_count={obj['problem_count']} != len(problems)={len(obj['problems'])}")
    return errors


def _filter_gaps(gap_detection: dict, category_name: str) -> list:
    if not gap_detection:
        return []
    name_lower = category_name.lower()
    return [
        mt for mt in gap_detection.get("missing_topics", [])
        if name_lower in mt.get("suggested_category", "").lower()
        or mt.get("suggested_category", "").lower() in name_lower
    ]


def run(run_id: str, scope: dict, scope_hash: str,
        category: dict, gap_detection: dict, gap_hash: str,
        kb_snapshot_id: str, tel=None) -> dict:
    cat_idx  = category["index"]
    cat_name = category["name_normalized"]
    print(f"[{STEP}] category={cat_idx}:{cat_name} run={run_id}")

    prompt_text, prompt_meta = load_prompt(STEP)
    prompt_hash = prompt_meta["hash"]

    cat_hash = sha256_obj({
        "index": cat_idx,
        "name_normalized": cat_name,
        "description": category.get("description", ""),
    })
    inputs = {
        "scope_hash":      scope_hash,
        "category_hash":   cat_hash,
        "gap_hash":        gap_hash if gap_detection else None,
        "kb_snapshot_id":  kb_snapshot_id,
        "prompt_hash":     prompt_hash,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, f"{STEP}/cat_{cat_idx:02d}")
    out_path = out_dir / "problems_draft.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit cat={cat_idx}")
        draft = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP,
                   {"task_id": task_id, "category_index": cat_idx})
        if tel:
            tel.record_cache_hit(STEP, task_id)
        return {"status": "ok", "problems_draft": draft,
                "draft_hash": sha256_file(out_path), "category_index": cat_idx}

    if tel:
        tel.record_cache_miss(STEP, task_id)
    emit_state(WORK_DIR, run_id, "step.start", STEP,
               {"task_id": task_id, "category_index": cat_idx, "prompt_hash": prompt_hash})

    relevant_gaps = _filter_gaps(gap_detection, cat_name)
    gap_section   = GAP_SECTION_TEMPLATE.format(
        gaps_json=json.dumps(relevant_gaps, indent=2, ensure_ascii=False)
    ) if relevant_gaps else ""

    prompt = prompt_text.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        category_name=cat_name,
        category_description=category.get("description", ""),
        estimated_count=category.get("estimated_problem_count", 10),
        category_index=cat_idx,
        gap_section=gap_section,
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
    )

    raw   = llm_call(prompt, retries=DEFAULT_RETRIES, tel=tel, step=STEP,
                     prompt_hash=prompt_hash, model_class=STEP_MODEL_CLASS.get(STEP, "35b"))
    draft = parse_json_response(raw)

    if draft is None:
        if tel:
            tel.record_parse(STEP, prompt_hash, success=False,
                             errors=["non-JSON"], )
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "category_index": cat_idx})
        return {"status": "stop", "stop_code": "llm_output_invalid",
                "category_index": cat_idx}

    errors = validate_output(draft)
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
        tel.record_content(STEP, {
            "category_index":     cat_idx,
            "problem_count":      len(draft.get("problems", [])),
            "estimated_count":    category.get("estimated_problem_count", 10),
        })

    draft["problem_count"] = len(draft["problems"])
    write_json(out_path, draft)
    draft_key  = f"{STEP}:cat_{cat_idx:02d}:problems_draft"
    draft_hash = register_artifact(WORK_DIR, run_id, draft_key,
                                   out_path, content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "category_index": cat_idx,
                "problem_count": draft["problem_count"], "prompt_hash": prompt_hash})

    print(f"  [done] cat={cat_idx} problems_draft={draft['problem_count']}")
    return {"status": "ok", "problems_draft": draft,
            "draft_hash": draft_hash, "category_index": cat_idx}
