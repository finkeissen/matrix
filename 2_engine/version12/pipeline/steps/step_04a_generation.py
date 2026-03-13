"""
step_04a_generation.py — Generate atomic problems draft (per category).
Type: LLM | Model: 35b (loaded in LM Studio)
Instantiated ×N, once per normalized category.
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
)

STEP = "04a_generation"

PROMPT_TEMPLATE = """You are a precise academic problem designer. Generate atomic problems for a specific category within the subdomain {subdomain_label}.

An atomic problem is:
- Single, self-contained — can be posed and answered independently
- Granular — cannot be meaningfully split further without losing context
- Specific — a correct answer exists or a clear evaluation rubric can be applied
- NOT trivial (e.g. "What is 2+2?") and NOT too broad (e.g. "Explain {subdomain_label}")

Subdomain scope:
{scope_json}

Category to generate problems for:
Name: {category_name}
Description: {category_description}
Estimated problem count: {estimated_count}

{gap_section}

Generate atomic problems for this category. Cover the full range of the description.
Include all difficulty levels: basic, intermediate, advanced, expert.
Include all answer types: factual, procedural, analytical, evaluative.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "category": "{category_name}",
  "category_index": {category_index},
  "problem_count": <integer>,
  "problems": [
    {{
      "title": <string: max 80 chars, English>,
      "problem_statement": <string: full self-contained problem, English>,
      "difficulty": "basic" | "intermediate" | "advanced" | "expert",
      "answer_type": "factual" | "procedural" | "analytical" | "evaluative",
      "canonical_source": <string: authoritative reference>,
      "verifiable": <boolean>,
      "hallucination_risk": "low" | "medium" | "high",
      "requires_context": <boolean>,
      "tags": [<string>]
    }}
  ]
}}"""

GAP_SECTION_TEMPLATE = """Known coverage gaps for this category (from gap analysis — prioritize these):
{gaps_json}"""


def _filter_gaps_for_category(gap_detection: dict, category_name: str) -> list:
    """Return only missing_topics relevant to this category."""
    if not gap_detection:
        return []
    name_lower = category_name.lower()
    relevant = []
    for mt in gap_detection.get("missing_topics", []):
        suggested = mt.get("suggested_category", "").lower()
        if suggested and (suggested in name_lower or name_lower in suggested):
            relevant.append(mt)
    return relevant


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain_id", "category", "problems"]:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if "problems" in obj:
        if not obj["problems"]:
            errors.append("problems array is empty")
        for p in obj["problems"]:
            if not p.get("title") or not p.get("problem_statement"):
                errors.append(f"problem missing title or problem_statement")
    return errors


def run(run_id: str, scope: dict, scope_hash: str,
        category: dict, gap_detection: dict, gap_hash: str,
        kb_snapshot_id: str, retry_context: dict = None) -> dict:
    """
    category: one item from normalized_categories.items
    Returns: {"status": "ok"|"stop", "problems_draft": {...}, "draft_hash": "..."}
    """
    cat_idx  = category["index"]
    cat_name = category["name_normalized"]
    print(f"[{STEP}] category={cat_idx}:{cat_name} run={run_id}")

    cat_hash = sha256_obj({
        "index": cat_idx,
        "name_normalized": cat_name,
        "description": category.get("description", ""),
    })
    inputs = {
        "scope_hash": scope_hash,
        "category_index": cat_idx,
        "category_hash": cat_hash,
        "gap_detection_hash": gap_hash if gap_detection else None,
        "kb_snapshot_id": kb_snapshot_id,
        "retry_context_hash": sha256_obj(retry_context) if retry_context else None,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, f"{STEP}/cat_{cat_idx:02d}")
    out_path = out_dir / "problems_draft.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit cat={cat_idx}")
        draft = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP,
                   {"task_id": task_id, "category_index": cat_idx})
        return {"status": "ok", "problems_draft": draft,
                "draft_hash": sha256_file(out_path), "category_index": cat_idx}

    emit_state(WORK_DIR, run_id, "step.start", STEP,
               {"task_id": task_id, "category_index": cat_idx, "category": cat_name})

    # Build gap section
    relevant_gaps = _filter_gaps_for_category(gap_detection, cat_name)
    if relevant_gaps:
        gap_section = GAP_SECTION_TEMPLATE.format(
            gaps_json=json.dumps(relevant_gaps, indent=2, ensure_ascii=False))
    else:
        gap_section = ""

    # Inject retry context if present
    retry_note = ""
    if retry_context:
        retry_note = f"\nRetry context (rejection reasons from previous attempt):\n{json.dumps(retry_context, indent=2)}\nAddress these issues in this attempt.\n"

    prompt = PROMPT_TEMPLATE.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        category_name=cat_name,
        category_description=category.get("description", ""),
        category_index=cat_idx,
        estimated_count=category.get("estimated_problem_count", 15),
        gap_section=gap_section + retry_note,
    )

    raw   = llm_call(prompt, retries=DEFAULT_RETRIES)
    draft = parse_json_response(raw)

    if draft is None:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "category_index": cat_idx})
        return {"status": "stop", "stop_code": "llm_output_invalid",
                "category_index": cat_idx}

    errors = validate_output(draft)
    if errors:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors),
                    "category_index": cat_idx})
        return {"status": "stop", "stop_code": "llm_output_invalid",
                "errors": errors, "category_index": cat_idx}

    draft["problem_count"] = len(draft["problems"])

    write_json(out_path, draft)
    draft_hash = register_artifact(
        WORK_DIR, run_id, f"{STEP}:cat_{cat_idx:02d}:problems_draft",
        out_path, content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "category_index": cat_idx,
                "problem_count": draft["problem_count"]})

    print(f"  [done] cat={cat_idx} problems={draft['problem_count']}")
    return {"status": "ok", "problems_draft": draft,
            "draft_hash": draft_hash, "category_index": cat_idx}
