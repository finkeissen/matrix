"""
step_07_hallucination_scan.py — Flag hallucination risks.
Type: LLM | Model: 122b (loaded in LM Studio)
Sampling: full if <=60 problems, stratified otherwise.
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES, HALLUCINATION_SAMPLE_MAX
from constants import STEP_MODEL_CLASS
from prompt_loader import load_prompt
from common import (
    llm_call, parse_json_response, sha256_file, now_iso,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
)

STEP = "07_examination_01_hallucination_scan"

PROMPT_TEMPLATE = """You are a rigorous academic fact-checker. Scan these atomic problems for hallucination risk.

For each problem, assess:
1. Is the problem statement factually correct as stated?
2. Does the canonical_source reference actually exist and cover this topic?
3. Are any technical terms used in a non-standard way?
4. Is the hallucination_risk assigned by the generator appropriate?

Flag any problem where you have doubt. Assign a corrected hallucination_risk if the original is wrong.

Subdomain: {subdomain_label} ({subdomain_id})

Problems to scan:
{problems_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "total_problems_scanned": <integer>,
  "flagged_count": <integer>,
  "scan_coverage": "{scan_coverage}",
  "flagged": [
    {{
      "category": <string>,
      "title": <string>,
      "issue_type": "factual_error" | "invalid_source" | "non_standard_term" | "risk_underestimated",
      "issue_description": <string>,
      "original_hallucination_risk": "low" | "medium" | "high",
      "corrected_hallucination_risk": "low" | "medium" | "high",
      "severity": "low" | "medium" | "high",
      "suggested_fix": <string or null>
    }}
  ],
  "overall_quality": "high" | "acceptable" | "low",
  "notes": <string or null>
}}"""


def _stratified_sample(all_problems: list, n: int) -> list:
    """Prioritize high/medium hallucination_risk, fill with random."""
    high   = [p for p in all_problems if p[1].get("hallucination_risk") == "high"]
    medium = [p for p in all_problems if p[1].get("hallucination_risk") == "medium"]
    low    = [p for p in all_problems if p[1].get("hallucination_risk") == "low"]

    selected = []
    for pool in [high, medium, low]:
        take = min(len(pool), n - len(selected))
        selected.extend(random.sample(pool, take))
        if len(selected) >= n:
            break
    return selected[:n]


def run(run_id: str, scope: dict, scope_hash: str,
        all_reviewed: list[dict],
        reviewed_hashes: list[str],
        validation_report: dict, report_hash: str,
        kb_snapshot_id: str, tel=None) -> dict:
    """
    Returns: {"status": "ok"|"stop", "hallucination_report": {...}, "hall_hash": "...",
              "routing": "proceed"|"retry_categories"}
    """
    print(f"[{STEP}] run={run_id}")

    inputs = {
        "problems_reviewed_hashes": sorted(reviewed_hashes),
        "validation_report_hash": report_hash,
        "scope_hash": scope_hash,
        "kb_snapshot_id": kb_snapshot_id,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "hallucination_report.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        hall = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        routing = "proceed" if hall.get("overall_quality") in ("high", "acceptable") else "retry_categories"
        return {"status": "ok", "hallucination_report": hall,
                "hall_hash": sha256_file(out_path), "routing": routing}

    emit_state(WORK_DIR, run_id, "step.start", STEP, {"task_id": task_id})

    # Flatten all problems
    all_problems = []
    for rev in all_reviewed:
        cat = rev.get("category", "unknown")
        for p in rev.get("problems", []):
            all_problems.append((cat, p))

    total = len(all_problems)
    if total <= HALLUCINATION_SAMPLE_MAX:
        scan_problems  = all_problems
        scan_coverage  = "full"
    else:
        scan_problems  = _stratified_sample(all_problems, HALLUCINATION_SAMPLE_MAX)
        scan_coverage  = "sampled"

    problems_for_llm = [
        {"category": cat, "title": p["title"],
         "problem_statement": p["problem_statement"],
         "canonical_source": p.get("canonical_source", ""),
         "hallucination_risk": p.get("hallucination_risk", "medium")}
        for cat, p in scan_problems
    ]

    prompt = PROMPT_TEMPLATE.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        scan_coverage=scan_coverage,
        problems_json=json.dumps(problems_for_llm, indent=2, ensure_ascii=False),
    )

    raw  = llm_call(prompt, retries=DEFAULT_RETRIES)
    hall = parse_json_response(raw)

    if hall is None or "overall_quality" not in hall:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid"})
        return {"status": "stop", "stop_code": "llm_output_invalid"}

    hall["total_problems_scanned"] = len(scan_problems)
    hall["flagged_count"]          = len(hall.get("flagged", []))

    write_json(out_path, hall)
    hall_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:hallucination_report",
                                  out_path, content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)

    routing = "proceed" if hall["overall_quality"] in ("high", "acceptable") else "retry_categories"
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "overall_quality": hall["overall_quality"],
                "flagged": hall["flagged_count"], "scan_coverage": scan_coverage,
                "routing": routing})

    print(f"  [done] quality={hall['overall_quality']} "
          f"flagged={hall['flagged_count']}/{len(scan_problems)} "
          f"coverage={scan_coverage}")
    return {"status": "ok", "hallucination_report": hall,
            "hall_hash": hall_hash, "routing": routing}
