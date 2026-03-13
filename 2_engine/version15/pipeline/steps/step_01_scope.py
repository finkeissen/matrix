"""
step_01_scope.py v14 — Define subdomain scope boundaries.
Type: LLM | Model: 19b | Prompt: prompts/01_scope.md
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES
from constants import STEP_MODEL_CLASS
from common import (
    sha256_file, sha256_str, now_iso, parse_json_response,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
    llm_call,
)
from prompt_loader import load_prompt, get_prompt_hash

STEP = "01_scope"


# ── Output contract (mirrors prompt requirements exactly) ─────────────────────

def validate_output(obj: dict) -> list[str]:
    """
    Validates the same constraints the prompt explicitly requests.
    Asymmetry between prompt and validator is a quality defect — keep in sync.
    """
    errors = []
    for field in ["subdomain", "subdomain_id", "parent_domain", "canonical_source",
                  "boundaries", "exclusions", "ambiguities"]:
        if field not in obj:
            errors.append(f"missing field: {field}")

    if "boundaries" in obj:
        n = len(obj["boundaries"])
        if n < 6:
            errors.append(f"boundaries has {n} items — prompt requires at least 6")

    if "exclusions" in obj:
        n = len(obj.get("exclusions", []))
        if n < 3:
            errors.append(f"exclusions has {n} items — prompt requires at least 3")

    if "ambiguities" in obj:
        if not isinstance(obj["ambiguities"], list):
            errors.append("ambiguities must be a list")
        elif len(obj["ambiguities"]) < 2:
            errors.append(f"ambiguities has {len(obj['ambiguities'])} items — prompt requires at least 2")
        else:
            for a in obj["ambiguities"]:
                if not isinstance(a, dict) or "topic" not in a or "resolution" not in a:
                    errors.append("each ambiguity must have 'topic' and 'resolution' fields")
                    break

    return errors


def _validate_clarification_input(obj: dict) -> list[str]:
    """Re-entry scope from 06_clarification must also pass validation."""
    return validate_output(obj)


# ── Step entrypoint ───────────────────────────────────────────────────────────

def run(run_id: str, subdomain: dict, kb_snapshot_id: str,
        clarification_input: dict = None,
        tel=None) -> dict:
    """
    subdomain: dict with keys subdomain_id, subdomain_label, parent_domain, score, tier
    clarification_input: optional refined scope from 06_clarification (re-entry)
    tel: optional Telemetry instance
    Returns: {"status": "ok"|"stop", "scope": {...}, "scope_hash": "..."}
    """
    print(f"[{STEP}] subdomain={subdomain['subdomain_id']} run={run_id}")

    prompt_text, prompt_meta = load_prompt(STEP)
    prompt_hash = prompt_meta["hash"]

    inputs = {
        "subdomain_id":          subdomain["subdomain_id"],
        "subdomain_label_hash":  sha256_str(subdomain["subdomain_label"]),
        "kb_snapshot_id":        kb_snapshot_id,
        "prompt_hash":           prompt_hash,   # prompt-sensitive cache
        "clarification_hash":    sha256_str(json.dumps(clarification_input, sort_keys=True))
                                 if clarification_input else None,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "scope.json"

    # Novelty Guard (prompt-sensitive)
    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        scope = json.loads(out_path.read_text())
        scope_hash = sha256_file(out_path)
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        if tel:
            tel.record_cache_hit(STEP, task_id)
        return {"status": "ok", "scope": scope, "scope_hash": scope_hash}

    if tel:
        tel.record_cache_miss(STEP, task_id)

    emit_state(WORK_DIR, run_id, "step.start", STEP,
               {"task_id": task_id, "prompt_hash": prompt_hash,
                "prompt_file": prompt_meta["file"]})

    # Re-entry from clarification: validate before accepting
    if clarification_input:
        errors = _validate_clarification_input(clarification_input)
        if errors:
            emit_state(WORK_DIR, run_id, "step.stop", STEP,
                       {"stop_code": "llm_output_invalid",
                        "reason": f"clarification_input failed validation: {errors}"})
            return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}
        scope = clarification_input
        scope.setdefault("subdomain_id", subdomain["subdomain_id"])
    else:
        prompt = prompt_text.format(
            subdomain_label=subdomain["subdomain_label"],
            subdomain_id=subdomain["subdomain_id"],
            parent_domain=subdomain["parent_domain"],
            score=subdomain.get("score", "N/A"),
            tier=subdomain.get("tier", "N/A"),
        )

        raw = llm_call(
            prompt,
            retries=DEFAULT_RETRIES,
            tel=tel,
            step=STEP,
            prompt_hash=prompt_hash,
            model_class=STEP_MODEL_CLASS.get(STEP, "19b"),
        )
        scope = parse_json_response(raw)

        if scope is None:
            if tel:
                tel.record_parse(STEP, prompt_hash, success=False,
                                 errors=["non-JSON response"])
            emit_state(WORK_DIR, run_id, "step.stop", STEP,
                       {"stop_code": "llm_output_invalid", "reason": "non-JSON response"})
            return {"status": "stop", "stop_code": "llm_output_invalid"}

        if tel:
            tel.record_parse(STEP, prompt_hash, success=True)

        errors = validate_output(scope)
        if errors:
            if tel:
                tel.record_parse(STEP, prompt_hash, success=False, errors=errors)
            emit_state(WORK_DIR, run_id, "step.stop", STEP,
                       {"stop_code": "llm_output_invalid", "reason": str(errors)})
            return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    write_json(out_path, scope)
    scope_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:scope", out_path,
                                   content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)

    if tel:
        tel.record_content(STEP, {
            "boundaries_count": len(scope.get("boundaries", [])),
            "exclusions_count":  len(scope.get("exclusions", [])),
            "ambiguities_count": len(scope.get("ambiguities", [])),
        })

    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "scope_hash": scope_hash,
                "prompt_hash": prompt_hash})

    print(f"  [done] scope written → {out_path}")
    return {"status": "ok", "scope": scope, "scope_hash": scope_hash}
