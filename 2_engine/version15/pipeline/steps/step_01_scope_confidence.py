"""
step_01_scope_confidence.py v14 — Score scope clarity; flag ambiguities.
Type: LLM | Model: 19b | Prompt: prompts/01_scope_confidence.md
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES, SCOPE_CONFIDENCE_THRESHOLD
from constants import STEP_MODEL_CLASS
from common import (
    sha256_file, parse_json_response, now_iso,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
    llm_call,
)
from prompt_loader import load_prompt

STEP = "01_scope_confidence"


def validate_output(obj: dict) -> list[str]:
    """Mirrors prompt requirements exactly."""
    errors = []
    for field in ["subdomain_id", "scores", "overall_score", "recommendation",
                  "flagged_ambiguities"]:
        if field not in obj:
            errors.append(f"missing field: {field}")

    if "recommendation" in obj and obj["recommendation"] not in ("proceed", "clarify"):
        errors.append("recommendation must be 'proceed' or 'clarify'")

    if "scores" in obj:
        for dim in ("boundary_clarity", "exclusion_coverage", "ambiguity_resolution"):
            if dim not in obj["scores"]:
                errors.append(f"scores.{dim} missing")
            else:
                v = obj["scores"][dim]
                if not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
                    errors.append(f"scores.{dim} must be float 0.0–1.0, got {v}")

    if "flagged_ambiguities" in obj and not isinstance(obj["flagged_ambiguities"], list):
        errors.append("flagged_ambiguities must be a list")

    return errors


def _clamp(val, lo=0.0, hi=1.0):
    try:
        return max(lo, min(hi, float(val)))
    except Exception:
        return lo


def run(run_id: str, scope: dict, scope_hash: str, kb_snapshot_id: str,
        tel=None) -> dict:
    """
    Returns: {"status": "ok", "recommendation": "proceed"|"clarify",
              "confidence": {...}, "confidence_hash": "..."}
    """
    print(f"[{STEP}] run={run_id}")

    prompt_text, prompt_meta = load_prompt(STEP)
    prompt_hash = prompt_meta["hash"]

    inputs = {
        "scope_hash":    scope_hash,
        "kb_snapshot_id": kb_snapshot_id,
        "prompt_hash":   prompt_hash,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "scope_confidence.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        conf = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        if tel:
            tel.record_cache_hit(STEP, task_id)
        return {"status": "ok", "recommendation": conf["recommendation"],
                "confidence": conf, "confidence_hash": sha256_file(out_path)}

    if tel:
        tel.record_cache_miss(STEP, task_id)

    emit_state(WORK_DIR, run_id, "step.start", STEP,
               {"task_id": task_id, "prompt_hash": prompt_hash,
                "prompt_file": prompt_meta["file"]})

    prompt = prompt_text.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        threshold=SCOPE_CONFIDENCE_THRESHOLD,
    )

    raw = llm_call(
        prompt,
        retries=DEFAULT_RETRIES,
        tel=tel,
        step=STEP,
        prompt_hash=prompt_hash,
        model_class=STEP_MODEL_CLASS.get(STEP, "19b"),
    )
    conf = parse_json_response(raw)

    if conf is None:
        if tel:
            tel.record_parse(STEP, prompt_hash, success=False,
                             errors=["non-JSON response"])
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": "non-JSON"})
        return {"status": "stop", "stop_code": "llm_output_invalid"}

    errors = validate_output(conf)
    if errors:
        if tel:
            tel.record_parse(STEP, prompt_hash, success=False, errors=errors)
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors)})
        return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    if tel:
        tel.record_parse(STEP, prompt_hash, success=True)

    # Clamp scores
    for k in ("boundary_clarity", "exclusion_coverage", "ambiguity_resolution"):
        if k in conf.get("scores", {}):
            conf["scores"][k] = _clamp(conf["scores"][k])
    if "overall_score" in conf:
        conf["overall_score"] = _clamp(conf["overall_score"])

    write_json(out_path, conf)
    conf_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:scope_confidence", out_path,
                                  content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)

    rec = conf["recommendation"]

    if tel:
        tel.record_content(STEP, {
            "overall_score":        conf.get("overall_score", 0),
            "boundary_clarity":     conf.get("scores", {}).get("boundary_clarity", 0),
            "exclusion_coverage":   conf.get("scores", {}).get("exclusion_coverage", 0),
            "ambiguity_resolution": conf.get("scores", {}).get("ambiguity_resolution", 0),
            "flagged_count":        len(conf.get("flagged_ambiguities", [])),
        })
        tel.record_routing(STEP, rec, {"overall_score": conf.get("overall_score")})

    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "recommendation": rec,
                "overall_score": conf.get("overall_score"),
                "prompt_hash": prompt_hash})

    print(f"  [done] recommendation={rec} score={conf.get('overall_score')}")
    return {"status": "ok", "recommendation": rec,
            "confidence": conf, "confidence_hash": conf_hash}
