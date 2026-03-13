"""
step_04b_generation_review.py — Review and refine problems draft (per category).
Type: LLM | Model: 122b (loaded in LM Studio)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES
from common import (
    llm_call, parse_json_response, sha256_file, sha256_obj,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
    supersede_artifact,
)

STEP = "04b_generation_review"

PROMPT_TEMPLATE = """You are a rigorous academic quality reviewer. Review and refine atomic problems for the category {category_name} within {subdomain_label} (ID: {subdomain_id}).

For each problem in the draft, apply these checks:
1. ATOMICITY: Can this problem be split further without losing context? If yes, split or flag it.
2. SELF-CONTAINMENT: Is it fully solvable without external data? If not, set requires_context: true.
3. HALLUCINATION RISK: Is this a well-established fact with a stable, verifiable answer?
4. DIFFICULTY: Is the assigned difficulty appropriate?
5. CANONICAL SOURCE: Is canonical_source specific and authoritative? Improve vague references.
6. DUPLICATION: Are any two problems asking essentially the same thing? Merge or remove duplicates.

Then check the gap detection report: are important topics missing? Add problems for missing topics.

Input scope:
{scope_json}

Input draft problems:
{draft_json}

Input gap detection report:
{gap_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "category": "{category_name}",
  "category_index": {category_index},
  "problem_count": <integer>,
  "problems_added": <integer>,
  "problems_removed": <integer>,
  "problems_modified": <integer>,
  "changes_made": [
    {{
      "action": "added" | "removed" | "modified" | "split",
      "title": <string>,
      "reason": <string>
    }}
  ],
  "problems": [
    {{
      "title": <string: max 80 chars, English>,
      "problem_statement": <string: full self-contained problem, English>,
      "difficulty": "basic" | "intermediate" | "advanced" | "expert",
      "answer_type": "factual" | "procedural" | "analytical" | "evaluative",
      "canonical_source": <string>,
      "verifiable": <boolean>,
      "hallucination_risk": "low" | "medium" | "high",
      "requires_context": <boolean>,
      "tags": [<string>]
    }}
  ]
}}"""


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain_id", "category", "problems"]:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if "problems" in obj and not obj["problems"]:
        errors.append("problems array is empty")
    return errors


def run(run_id: str, scope: dict, scope_hash: str,
        draft: dict, draft_hash: str,
        category: dict,
        gap_detection: dict, gap_hash: str,
        kb_snapshot_id: str,
        prior_reviewed_key: str = None) -> dict:
    """
    Returns: {"status": "ok"|"stop", "problems_reviewed": {...}, "reviewed_hash": "..."}
    """
    cat_idx  = category["index"]
    cat_name = category["name_normalized"]
    print(f"[{STEP}] category={cat_idx}:{cat_name} run={run_id}")

    if prior_reviewed_key:
        supersede_artifact(WORK_DIR, run_id, prior_reviewed_key)

    cat_hash = sha256_obj({
        "index": cat_idx,
        "name_normalized": cat_name,
        "description": category.get("description", ""),
    })
    inputs = {
        "problems_draft_hash": draft_hash,
        "scope_hash": scope_hash,
        "gap_detection_hash": gap_hash if gap_detection else None,
        "category_index": cat_idx,
        "category_hash": cat_hash,
        "kb_snapshot_id": kb_snapshot_id,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, f"{STEP}/cat_{cat_idx:02d}")
    out_path = out_dir / "problems_reviewed.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit cat={cat_idx}")
        reviewed = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP,
                   {"task_id": task_id, "category_index": cat_idx})
        return {"status": "ok", "problems_reviewed": reviewed,
                "reviewed_hash": sha256_file(out_path), "category_index": cat_idx}

    emit_state(WORK_DIR, run_id, "step.start", STEP,
               {"task_id": task_id, "category_index": cat_idx})

    prompt = PROMPT_TEMPLATE.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        category_name=cat_name,
        category_index=cat_idx,
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        draft_json=json.dumps(draft, indent=2, ensure_ascii=False),
        gap_json=json.dumps(gap_detection or {}, indent=2, ensure_ascii=False),
    )

    raw      = llm_call(prompt, retries=DEFAULT_RETRIES)
    reviewed = parse_json_response(raw)

    if reviewed is None:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "category_index": cat_idx})
        return {"status": "stop", "stop_code": "llm_output_invalid",
                "category_index": cat_idx}

    errors = validate_output(reviewed)
    if errors:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors),
                    "category_index": cat_idx})
        return {"status": "stop", "stop_code": "llm_output_invalid",
                "errors": errors, "category_index": cat_idx}

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
                "problems_removed": reviewed.get("problems_removed", 0)})

    print(f"  [done] cat={cat_idx} problems={reviewed['problem_count']} "
          f"+{reviewed.get('problems_added',0)}/-{reviewed.get('problems_removed',0)}")
    return {"status": "ok", "problems_reviewed": reviewed,
            "reviewed_hash": reviewed_hash, "reviewed_key": reviewed_key,
            "category_index": cat_idx}
