"""
step_07_alternative_check.py — Coverage and categorization review.
Type: LLM | Model: 35b (loaded in LM Studio)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES
from common import (
    llm_call, parse_json_response, sha256_file, now_iso,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
)

STEP = "07_examination_02_alternative_check"

PROMPT_TEMPLATE = """You are a precise academic knowledge engineer. Review the overall coverage and categorization quality of the generated problem set for {subdomain_label} ({subdomain_id}).

Assess:
1. COVERAGE GAPS: Important topic areas from the gap report still missing after generation?
2. RECATEGORIZATION: Problems that would be better placed in a different category?
3. CATEGORY BALANCE: Over- or under-represented categories?
4. DECISION: Proceed to finalization, or regenerate specific categories?

Input — hallucination report summary:
{hall_json}

Input — normalized categories:
{categories_json}

Input — gap detection report:
{gap_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "coverage_gaps": [
    {{
      "topic": <string>,
      "severity": "low" | "medium" | "high",
      "suggested_action": <string>
    }}
  ],
  "recategorization_suggestions": [
    {{
      "problem_title": <string>,
      "current_category": <string>,
      "suggested_category": <string>,
      "reason": <string>
    }}
  ],
  "category_balance": [
    {{
      "category": <string>,
      "problem_count": <integer>,
      "assessment": "balanced" | "over_represented" | "under_represented"
    }}
  ],
  "decision": "proceed" | "regenerate_categories",
  "regenerate_category_indices": [<integer>],
  "decision_rationale": <string>,
  "examined_at": "{now}"
}}"""


def run(run_id: str, scope: dict, scope_hash: str,
        normalized: dict, normalized_hash: str,
        gap_detection: dict, gap_hash: str,
        hallucination_report: dict, hall_hash: str,
        kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "alternative_check": {...}, "alt_hash": "...",
              "routing": "proceed"|"regenerate_categories"}
    """
    print(f"[{STEP}] run={run_id}")

    inputs = {
        "hallucination_report_hash": hall_hash,
        "normalized_categories_hash": normalized_hash,
        "gap_detection_hash": gap_hash,
        "scope_hash": scope_hash,
        "kb_snapshot_id": kb_snapshot_id,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "alternative_check.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        alt = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        return {"status": "ok", "alternative_check": alt,
                "alt_hash": sha256_file(out_path),
                "routing": alt.get("decision", "proceed")}

    emit_state(WORK_DIR, run_id, "step.start", STEP, {"task_id": task_id})

    prompt = PROMPT_TEMPLATE.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        hall_json=json.dumps(hallucination_report, indent=2, ensure_ascii=False),
        categories_json=json.dumps(normalized, indent=2, ensure_ascii=False),
        gap_json=json.dumps(gap_detection, indent=2, ensure_ascii=False),
        now=now_iso(),
    )

    raw = llm_call(prompt, retries=DEFAULT_RETRIES)
    alt = parse_json_response(raw)

    # Non-critical step: default to proceed on failure
    if alt is None or "decision" not in alt:
        print(f"  [warn] LLM output invalid — defaulting to proceed")
        alt = {
            "subdomain_id": scope.get("subdomain_id", ""),
            "coverage_gaps": [], "recategorization_suggestions": [],
            "category_balance": [],
            "decision": "proceed",
            "regenerate_category_indices": [],
            "decision_rationale": "Defaulted to proceed due to LLM output failure.",
            "examined_at": now_iso(),
        }
        emit_state(WORK_DIR, run_id, "step.warn", STEP,
                   {"warn": "llm_output_invalid_defaulted_to_proceed"})

    write_json(out_path, alt)
    alt_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:alternative_check",
                                 out_path, content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)

    routing = alt.get("decision", "proceed")
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "decision": routing,
                "regenerate_indices": alt.get("regenerate_category_indices", [])})

    print(f"  [done] decision={routing} "
          f"gaps={len(alt.get('coverage_gaps',[]))} "
          f"regen={alt.get('regenerate_category_indices', [])}")
    return {"status": "ok", "alternative_check": alt,
            "alt_hash": alt_hash, "routing": routing}
