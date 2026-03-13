"""
step_06_clarification.py — Scope refinement loop (max 2 rounds).
Type: LLM | Model: 19b (loaded in LM Studio)
Snapshot after: yes
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES, MAX_CLARIFICATION_ROUNDS
from constants import STEP_MODEL_CLASS
from prompt_loader import load_prompt
from common import (
    llm_call, parse_json_response, sha256_file,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
    create_snapshot, load_run_record, save_run_record,
)

STEP = "06_clarification"

PROMPT_TEMPLATE = """You are a precise academic knowledge engineer. A scope definition has produced validation issues. Generate a refined scope that resolves these issues.

This is clarification round {round_num} of maximum {max_rounds}.

Current scope:
{scope_json}

Validation issues that triggered this clarification:
{issues_json}

Produce a refined scope object that resolves these issues. Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": <string>,
  "subdomain_id": <string>,
  "parent_domain": <string>,
  "canonical_source": <string>,
  "boundaries": [<string>],
  "exclusions": [<string>],
  "ambiguities": [{{"topic": <string>, "resolution": <string>}}],
  "refinement_round": {round_num},
  "changes_made": [
    {{
      "field": "boundaries" | "exclusions" | "ambiguities",
      "change": <string>
    }}
  ]
}}"""


def _build_issues(validation_report: dict = None,
                  confidence: dict = None) -> dict:
    """Compile issue summary from either validation_report or scope_confidence."""
    issues = {}
    if validation_report:
        issues["scope_violations"]  = validation_report.get("scope_violations", [])
        issues["schema_errors"]     = validation_report.get("schema_errors", [])
        issues["scope_unclear"]     = validation_report.get("scope_unclear", False)
    if confidence:
        issues["flagged_ambiguities"] = confidence.get("flagged_ambiguities", [])
        issues["overall_score"]       = confidence.get("overall_score")
        issues["recommendation"]      = confidence.get("recommendation")
    return issues


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain", "subdomain_id", "boundaries", "exclusions"]:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if not obj.get("boundaries"):
        errors.append("boundaries must be non-empty")
    return errors


def run(run_id: str, scope: dict, scope_hash: str,
        kb_snapshot_id: str,
        validation_report: dict = None, report_hash: str = None,
        confidence: dict = None, confidence_hash: str = None,
        tel=None) -> dict:
    """
    Returns: {"status": "ok"|"stop", "refined_scope": {...}}
    On stop: stop_code = "scope_clarification_exhausted" or "llm_output_invalid"
    """
    rec = load_run_record(WORK_DIR, run_id)
    current_rounds = rec.get("clarification_rounds", 0)

    if current_rounds >= MAX_CLARIFICATION_ROUNDS:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "scope_clarification_exhausted",
                    "clarification_rounds": current_rounds})
        print(f"  [STOP] scope_clarification_exhausted after {current_rounds} rounds")
        return {"status": "stop", "stop_code": "scope_clarification_exhausted"}

    round_num = current_rounds + 1
    print(f"[{STEP}] round={round_num}/{MAX_CLARIFICATION_ROUNDS} run={run_id}")

    issues = _build_issues(validation_report, confidence)
    inputs = {
        "scope_hash": scope_hash,
        "round": round_num,
        "kb_snapshot_id": kb_snapshot_id,
        "issues_hash": sha256_file.__module__,  # just use obj hash
    }
    from common import sha256_obj
    inputs["issues_hash"] = sha256_obj(issues)
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / f"clarification_request_round_{round_num}.json"

    emit_state(WORK_DIR, run_id, "step.start", STEP,
               {"task_id": task_id, "round": round_num})

    prompt = PROMPT_TEMPLATE.format(
        round_num=round_num,
        max_rounds=MAX_CLARIFICATION_ROUNDS,
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        issues_json=json.dumps(issues, indent=2, ensure_ascii=False),
    )
    raw      = llm_call(prompt, retries=DEFAULT_RETRIES)
    refined  = parse_json_response(raw)

    if refined is None:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid"})
        return {"status": "stop", "stop_code": "llm_output_invalid"}

    errors = validate_output(refined)
    if errors:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors)})
        return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    write_json(out_path, refined)
    register_artifact(WORK_DIR, run_id, f"{STEP}:round_{round_num}",
                      out_path, content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)

    # Increment clarification_rounds in run_record
    rec["clarification_rounds"] = round_num
    save_run_record(WORK_DIR, run_id, rec)

    snap_id = create_snapshot(WORK_DIR, run_id, f"clarification_round_{round_num}")
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "round": round_num, "snapshot_id": snap_id})

    print(f"  [done] clarification round {round_num} complete")
    return {"status": "ok", "refined_scope": refined, "round": round_num}
