"""
step_05_validation.py — Schema, duplicate, atomicity validation.
Type: deterministic + LLM (atomicity sample)
Snapshot after: yes
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES, ATOMICITY_FAILURE_THRESHOLD
from common import (
    llm_call, parse_json_response, sha256_file,
    artifact_dir, write_json, register_artifact,
    emit_state, promote_artifact, create_snapshot, now_iso,
)

STEP = "05_validation"

VALID_DIFFICULTIES  = {"basic", "intermediate", "advanced", "expert"}
VALID_ANSWER_TYPES  = {"factual", "procedural", "analytical", "evaluative"}
VALID_HALLIB_RISKS  = {"low", "medium", "high"}
ATOMICITY_SAMPLE_N  = 20

ATOMICITY_PROMPT = """You are an academic quality reviewer. Check whether each of the following problems is truly atomic — i.e., it cannot be meaningfully split into two or more independent problems without losing context.

For each problem, return:
- is_atomic: true/false
- issue: null or a short description of why it is not atomic

Problems to check:
{problems_json}

Return ONLY a JSON array (no object wrapper). One entry per problem, in the same order.

[
  {{
    "title": <string>,
    "is_atomic": <boolean>,
    "self_contained": <boolean>,
    "issue": <string or null>
  }}
]"""


def _check_schema(problem: dict, category: str) -> list[dict]:
    errors = []
    required = ["title", "problem_statement", "difficulty", "answer_type",
                "canonical_source", "verifiable", "hallucination_risk",
                "requires_context", "tags"]
    for field in required:
        if field not in problem:
            errors.append({"category": category, "problem_title": problem.get("title", "?"),
                           "field": field, "issue": "missing field"})
    if problem.get("difficulty") not in VALID_DIFFICULTIES:
        errors.append({"category": category, "problem_title": problem.get("title", "?"),
                       "field": "difficulty", "issue": f"invalid: {problem.get('difficulty')}"})
    if problem.get("answer_type") not in VALID_ANSWER_TYPES:
        errors.append({"category": category, "problem_title": problem.get("title", "?"),
                       "field": "answer_type", "issue": f"invalid: {problem.get('answer_type')}"})
    if problem.get("hallucination_risk") not in VALID_HALLIB_RISKS:
        errors.append({"category": category, "problem_title": problem.get("title", "?"),
                       "field": "hallucination_risk",
                       "issue": f"invalid: {problem.get('hallucination_risk')}"})
    if len(problem.get("title", "")) > 80:
        errors.append({"category": category, "problem_title": problem.get("title", "?"),
                       "field": "title", "issue": "exceeds 80 chars"})
    return errors


def _detect_duplicates(all_problems: list[tuple]) -> list[dict]:
    """all_problems: list of (category, problem_dict)"""
    dupes = []
    titles = [(cat, p["title"].lower().strip()) for cat, p in all_problems]
    seen   = {}
    for i, (cat, title) in enumerate(titles):
        if title in seen:
            prev_cat, prev_title_orig = seen[title]
            dupes.append({
                "title_a": all_problems[seen[title][2]]["title"],
                "title_b": all_problems[i][1]["title"],
                "category_a": prev_cat,
                "category_b": cat,
                "similarity": "exact",
            })
        else:
            seen[title] = (cat, title, i)
    return dupes


def _check_scope_violations(all_problems: list[tuple], scope: dict) -> list[dict]:
    exclusions = [e.lower() for e in scope.get("exclusions", [])]
    violations = []
    for cat, p in all_problems:
        stmt = p.get("problem_statement", "").lower()
        for excl in exclusions:
            # simple keyword check on first significant word of exclusion
            keyword = excl.split()[0] if excl.split() else ""
            if keyword and keyword in stmt:
                violations.append({
                    "problem_title": p.get("title", "?"),
                    "violation": f"Possible scope violation: '{excl}'"
                })
                break
    return violations


def run(run_id: str, scope: dict, scope_hash: str,
        all_reviewed: list[dict],   # list of problems_reviewed dicts (one per category)
        reviewed_keys: list[str],   # manifest keys for promote
        kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "validation_report": {...}, "report_hash": "...",
              "routing": "proceed"|"clarify"|"retry_categories"|"insufficient"}
    """
    print(f"[{STEP}] run={run_id} categories={len(all_reviewed)}")
    emit_state(WORK_DIR, run_id, "step.start", STEP, {})

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "validation_report.json"

    # ── Phase 1: Deterministic ─────────────────────────────────────────────────
    all_problems: list[tuple] = []   # (category_name, problem_dict)
    for rev in all_reviewed:
        cat = rev.get("category", "unknown")
        for p in rev.get("problems", []):
            all_problems.append((cat, p))

    schema_errors    = []
    for cat, p in all_problems:
        schema_errors.extend(_check_schema(p, cat))

    duplicates       = _detect_duplicates(all_problems)
    scope_violations = _check_scope_violations(all_problems, scope)

    total = len(all_problems)
    valid_phase1 = (len(schema_errors) == 0 and len(duplicates) == 0 and total > 0)

    # ── Phase 2: LLM atomicity sample ─────────────────────────────────────────
    atomicity_failures     = []
    atomicity_failure_rate = 0.0
    sample_size            = 0

    if valid_phase1 and total > 0:
        sample = random.sample(all_problems, min(ATOMICITY_SAMPLE_N, total))
        sample_size = len(sample)
        sample_for_llm = [{"title": p["title"],
                           "problem_statement": p["problem_statement"],
                           "requires_context": p.get("requires_context", False)}
                          for _, p in sample]

        prompt = ATOMICITY_PROMPT.format(
            problems_json=json.dumps(sample_for_llm, indent=2, ensure_ascii=False))
        raw    = llm_call(prompt, retries=DEFAULT_RETRIES)
        result = parse_json_response(raw)

        if result and isinstance(result, list):
            for entry in result:
                if not entry.get("is_atomic", True) or not entry.get("self_contained", True):
                    atomicity_failures.append({
                        "problem_title": entry.get("title", "?"),
                        "issue": entry.get("issue", "not atomic or not self-contained"),
                        "severity": "medium",
                    })
            atomicity_failure_rate = (len(atomicity_failures) / sample_size
                                      if sample_size > 0 else 0.0)

    scope_unclear = (len(scope_violations) > 0 or
                     (len(schema_errors) == 0 and len(scope_violations) > 0))

    valid = (valid_phase1
             and atomicity_failure_rate <= ATOMICITY_FAILURE_THRESHOLD
             and len(scope_violations) == 0)

    report = {
        "subdomain_id":            scope.get("subdomain_id", ""),
        "total_problems":          total,
        "valid":                   valid,
        "schema_errors":           schema_errors,
        "duplicates":              duplicates,
        "scope_violations":        scope_violations,
        "atomicity_failures":      atomicity_failures,
        "atomicity_sample_size":   sample_size,
        "atomicity_failure_rate":  round(atomicity_failure_rate, 4),
        "scope_unclear":           scope_unclear,
        "notes":                   None,
        "validated_at":            now_iso(),
    }

    write_json(out_path, report)
    report_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:validation_report",
                                    out_path, content_state="candidate", step=STEP)

    # ── Promote reviewed artifacts if valid ────────────────────────────────────
    if valid:
        for key in reviewed_keys:
            promote_artifact(WORK_DIR, run_id, key, "verified")
        print(f"  [promote] {len(reviewed_keys)} reviewed artifacts → verified")

    # ── Routing decision ───────────────────────────────────────────────────────
    if valid and not scope_unclear:
        routing = "proceed"
    elif scope_unclear or scope_violations:
        routing = "clarify"
    elif not valid and (schema_errors or atomicity_failure_rate > ATOMICITY_FAILURE_THRESHOLD):
        routing = "retry_categories"
    else:
        routing = "insufficient"

    snap_id = create_snapshot(WORK_DIR, run_id, "post_validation")
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"valid": valid, "routing": routing,
                "total_problems": total,
                "schema_errors": len(schema_errors),
                "duplicates": len(duplicates),
                "atomicity_failure_rate": round(atomicity_failure_rate, 4),
                "snapshot_id": snap_id})

    print(f"  [done] valid={valid} routing={routing} "
          f"problems={total} schema_err={len(schema_errors)} "
          f"atomicity_fail_rate={atomicity_failure_rate:.2%}")
    return {"status": "ok", "validation_report": report,
            "report_hash": report_hash, "routing": routing}
