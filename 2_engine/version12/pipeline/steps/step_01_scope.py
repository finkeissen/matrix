"""
step_01_scope.py — Define subdomain scope boundaries.
Type: LLM | Model: 19b (loaded in LM Studio)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES
from common import (
    llm_call, parse_json_response, sha256_file, sha256_str, now_iso,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
)


STEP = "01_scope"

PROMPT_TEMPLATE = """You are a precise academic knowledge engineer. Your task is to define the exact scope of a subdomain for an atomic problem generation pipeline.

Subdomain: {subdomain_label}
Parent domain: {parent_domain}
Subdomain ID: {subdomain_id}
Score: {score} (Tier {tier})

Define the scope of {subdomain_label} as a knowledge domain for the purpose of generating atomic problems. An atomic problem is a single, self-contained question or task that can be posed and answered independently, is granular enough that it cannot be meaningfully split further, and has a correct answer or a clear evaluation rubric.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "parent_domain": "{parent_domain}",
  "canonical_source": <string: the single most authoritative reference for {subdomain_label} as a whole>,
  "boundaries": <array of strings: what IS in scope — list at least 6 specific topic areas>,
  "exclusions": <array of strings: what is explicitly OUT of scope — list at least 3 areas>,
  "ambiguities": <array of objects with fields "topic" and "resolution": at least 2 boundary cases>
}}

Requirements:
- boundaries must list at least 6 specific topic areas
- exclusions must list at least 3 areas that could be confused with {subdomain_label}
- ambiguities must address at least 2 boundary cases
- All values in English
- Be precise: boundaries and exclusions will be used to validate generated problems"""


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain", "subdomain_id", "parent_domain", "canonical_source",
                  "boundaries", "exclusions", "ambiguities"]:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if "boundaries" in obj and len(obj["boundaries"]) < 3:
        errors.append("boundaries must have at least 3 items")
    if "exclusions" in obj and len(obj.get("exclusions", [])) < 1:
        errors.append("exclusions must be non-empty")
    if "ambiguities" in obj and not isinstance(obj["ambiguities"], list):
        errors.append("ambiguities must be a list")
    return errors


def run(run_id: str, subdomain: dict, kb_snapshot_id: str,
        clarification_input: dict = None) -> dict:
    """
    subdomain: dict with keys subdomain_id, subdomain_label, parent_domain, score, tier
    clarification_input: optional refined scope from 06_clarification (re-entry)
    Returns: {"status": "ok"|"stop", "scope": {...}, "scope_hash": "..."}
    """
    print(f"[{STEP}] subdomain={subdomain['subdomain_id']} run={run_id}")

    inputs = {
        "subdomain_id": subdomain["subdomain_id"],
        "subdomain_label_hash": sha256_str(subdomain["subdomain_label"]),
        "kb_snapshot_id": kb_snapshot_id,
        "clarification_hash": sha256_str(json.dumps(clarification_input, sort_keys=True))
                              if clarification_input else None,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir   = artifact_dir(WORK_DIR, run_id, STEP)
    out_path  = out_dir / "scope.json"

    # Novelty Guard
    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit — skipping LLM call")
        scope = json.loads(out_path.read_text())
        scope_hash = sha256_file(out_path)
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        return {"status": "ok", "scope": scope, "scope_hash": scope_hash}

    emit_state(WORK_DIR, run_id, "step.start", STEP, {"task_id": task_id})

    # If re-entry from clarification, use refined scope directly
    if clarification_input:
        scope = clarification_input
        scope.setdefault("subdomain_id", subdomain["subdomain_id"])
    else:
        prompt = PROMPT_TEMPLATE.format(
            subdomain_label=subdomain["subdomain_label"],
            subdomain_id=subdomain["subdomain_id"],
            parent_domain=subdomain["parent_domain"],
            score=subdomain.get("score", "N/A"),
            tier=subdomain.get("tier", "N/A"),
        )
        raw = llm_call(prompt, retries=DEFAULT_RETRIES)
        scope = parse_json_response(raw)

        if scope is None:
            emit_state(WORK_DIR, run_id, "step.stop", STEP,
                       {"stop_code": "llm_output_invalid", "reason": "non-JSON response"})
            return {"status": "stop", "stop_code": "llm_output_invalid"}

        errors = validate_output(scope)
        if errors:
            emit_state(WORK_DIR, run_id, "step.stop", STEP,
                       {"stop_code": "llm_output_invalid", "reason": str(errors)})
            return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    write_json(out_path, scope)
    scope_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:scope", out_path,
                                   content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "scope_hash": scope_hash})

    print(f"  [done] scope written → {out_path}")
    return {"status": "ok", "scope": scope, "scope_hash": scope_hash}
