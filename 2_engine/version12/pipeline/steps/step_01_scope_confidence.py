"""
step_01_scope_confidence.py — Score scope clarity; flag ambiguities.
Type: LLM | Model: 19b (loaded in LM Studio)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES, SCOPE_CONFIDENCE_THRESHOLD
from common import (
    llm_call, parse_json_response, sha256_file, now_iso,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
)

STEP = "01_scope_confidence"

PROMPT_TEMPLATE = """You are a precise academic knowledge engineer. Your task is to assess the quality and clarity of a scope definition for an atomic problem generation pipeline.

Evaluate the following scope object for the subdomain {subdomain_label}. Rate it on three dimensions (0.0–1.0 each).

Input scope:
{scope_json}

1. boundary_clarity (0.0–1.0): Are boundaries specific enough to decide unambiguously whether a problem belongs here?
2. exclusion_coverage (0.0–1.0): Do exclusions cover the most likely confusion areas?
3. ambiguity_resolution (0.0–1.0): Are ambiguity resolutions clear and actionable?

Compute overall_score as arithmetic mean, rounded to 2 decimal places.
recommendation: "proceed" if overall_score >= {threshold}, otherwise "clarify"

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "scores": {{
    "boundary_clarity": <float 0.0–1.0>,
    "exclusion_coverage": <float 0.0–1.0>,
    "ambiguity_resolution": <float 0.0–1.0>
  }},
  "overall_score": <float 0.0–1.0>,
  "recommendation": "proceed" | "clarify",
  "flagged_ambiguities": [
    {{
      "topic": <string>,
      "issue": <string>,
      "severity": "low" | "medium" | "high"
    }}
  ],
  "notes": <string or null>
}}"""


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain_id", "scores", "overall_score", "recommendation"]:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if "recommendation" in obj and obj["recommendation"] not in ("proceed", "clarify"):
        errors.append("recommendation must be 'proceed' or 'clarify'")
    return errors


def clamp(val, lo=0.0, hi=1.0):
    try:
        return max(lo, min(hi, float(val)))
    except Exception:
        return lo


def run(run_id: str, scope: dict, scope_hash: str, kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok", "recommendation": "proceed"|"clarify",
              "confidence": {...}, "confidence_hash": "..."}
    """
    print(f"[{STEP}] run={run_id}")

    inputs = {"scope_hash": scope_hash, "kb_snapshot_id": kb_snapshot_id}
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "scope_confidence.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        conf = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        return {"status": "ok",
                "recommendation": conf["recommendation"],
                "confidence": conf,
                "confidence_hash": sha256_file(out_path)}

    emit_state(WORK_DIR, run_id, "step.start", STEP, {"task_id": task_id})

    prompt = PROMPT_TEMPLATE.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        threshold=SCOPE_CONFIDENCE_THRESHOLD,
    )
    raw  = llm_call(prompt, retries=DEFAULT_RETRIES)
    conf = parse_json_response(raw)

    if conf is None:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": "non-JSON"})
        return {"status": "stop", "stop_code": "llm_output_invalid"}

    errors = validate_output(conf)
    if errors:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors)})
        return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    # Clamp scores
    for k in ("boundary_clarity", "exclusion_coverage", "ambiguity_resolution"):
        if k in conf.get("scores", {}):
            conf["scores"][k] = clamp(conf["scores"][k])
    if "overall_score" in conf:
        conf["overall_score"] = clamp(conf["overall_score"])

    write_json(out_path, conf)
    conf_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:scope_confidence", out_path,
                                  content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)

    rec = conf["recommendation"]
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "recommendation": rec,
                "overall_score": conf.get("overall_score")})

    print(f"  [done] recommendation={rec} score={conf.get('overall_score')}")
    return {"status": "ok", "recommendation": rec,
            "confidence": conf, "confidence_hash": conf_hash}
