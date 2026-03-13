"""
step_05_validation.py — Schema, duplicate, atomicity, scope validation.
v2.1: Uses central validator.py (fixes #2 jsonschema, #3 dedup bug,
      #4 semantic dedup, #5 scope check, #7 commit policy).
Type: deterministic + LLM (atomicity sample)
Snapshot after: yes
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES, ATOMICITY_FAILURE_THRESHOLD
from constants import ContentState, StopCode, ArtifactKey
from common import (
    llm_call, parse_json_response, sha256_file,
    artifact_dir, write_json, register_artifact,
    emit_state, promote_artifact, create_snapshot, now_iso,
)
from validator import (
    validate_problem, detect_duplicates,
    check_scope_violations, make_problem_uid, validate_schema,
)

STEP = "05_validation"
ATOMICITY_SAMPLE_N = 20

ATOMICITY_PROMPT = """You are an academic quality reviewer. Check whether each problem is truly atomic — it cannot be meaningfully split into two or more independent problems without losing context.

For each problem return:
- is_atomic: true/false
- self_contained: true/false (solvable without external data not in the problem text)
- issue: null or a short description

Problems:
{problems_json}

Return ONLY a JSON array. One entry per problem, same order. No preamble, no markdown.

[
  {{
    "title": <string>,
    "is_atomic": <boolean>,
    "self_contained": <boolean>,
    "issue": <string or null>
  }}
]"""


def run(run_id: str, scope: dict, scope_hash: str,
        all_reviewed: list[dict],
        reviewed_keys: list[str],
        kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "validation_report": {...},
              "report_hash": "...", "routing": str}
    """
    print(f"[{STEP}] run={run_id} categories={len(all_reviewed)}")
    emit_state(WORK_DIR, run_id, "step.start", STEP, {})

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "validation_report.json"

    # ── Build flat problem list as (category, problem_dict) tuples ─────────────
    all_problems: list[tuple] = []
    for rev in all_reviewed:
        cat = rev.get("category", "unknown")
        for p in rev.get("problems", []):
            all_problems.append((cat, p))   # always tuples, never bare dicts

    total = len(all_problems)

    # ── Phase 1a: Per-problem schema + enum validation ─────────────────────────
    schema_errors = []
    for cat, p in all_problems:
        errs = validate_problem(p, cat)
        schema_errors.extend(errs)

    # ── Phase 1b: Full problems_reviewed jsonschema (per category) ─────────────
    jsonschema_errors = []
    for rev in all_reviewed:
        errs = validate_schema(rev, "problems_reviewed")
        jsonschema_errors.extend(errs)

    # ── Phase 1c: Duplicate detection (fix #3 + #4) ────────────────────────────
    duplicates = detect_duplicates(all_problems, similarity_threshold=0.85)

    # ── Phase 1d: Scope violation check (fix #5) ──────────────────────────────
    scope_violations = check_scope_violations(all_problems, scope)

    valid_phase1 = (
        len(schema_errors) == 0
        and len(jsonschema_errors) == 0
        and len(duplicates) == 0
        and total > 0
    )

    # ── Phase 2: LLM atomicity sample ─────────────────────────────────────────
    atomicity_failures     = []
    atomicity_failure_rate = 0.0
    sample_size            = 0

    if total > 0:
        sample = random.sample(all_problems, min(ATOMICITY_SAMPLE_N, total))
        sample_size = len(sample)
        sample_for_llm = [
            {
                "title":            p["title"],
                "problem_statement": p["problem_statement"],
                "requires_context": p.get("requires_context", False),
            }
            for _, p in sample   # correct tuple unpacking
        ]
        prompt = ATOMICITY_PROMPT.format(
            problems_json=json.dumps(sample_for_llm, indent=2, ensure_ascii=False))
        raw    = llm_call(prompt, retries=DEFAULT_RETRIES)
        result = parse_json_response(raw)

        if result and isinstance(result, list):
            for entry in result:
                if not entry.get("is_atomic", True) or not entry.get("self_contained", True):
                    atomicity_failures.append({
                        "problem_title": entry.get("title", "?"),
                        "issue":  entry.get("issue", "not atomic or not self-contained"),
                        "severity": "medium",
                    })
            atomicity_failure_rate = (len(atomicity_failures) / sample_size
                                      if sample_size > 0 else 0.0)

    # ── Routing decision ───────────────────────────────────────────────────────
    scope_unclear = len(scope_violations) > 0

    valid = (
        valid_phase1
        and atomicity_failure_rate <= ATOMICITY_FAILURE_THRESHOLD
        and not scope_unclear
    )

    if valid and not scope_unclear:
        routing = "proceed"
    elif scope_unclear or scope_violations:
        routing = "clarify"
    elif not valid and (schema_errors or jsonschema_errors or
                        atomicity_failure_rate > ATOMICITY_FAILURE_THRESHOLD):
        routing = "retry_categories"
    else:
        routing = "insufficient"

    # ── Assemble report ────────────────────────────────────────────────────────
    report = {
        "subdomain_id":            scope.get("subdomain_id", ""),
        "total_problems":          total,
        "valid":                   valid,
        "schema_errors":           schema_errors,
        "jsonschema_errors":       jsonschema_errors,
        "duplicates":              duplicates,
        "scope_violations":        scope_violations,
        "atomicity_failures":      atomicity_failures,
        "atomicity_sample_size":   sample_size,
        "atomicity_failure_rate":  round(atomicity_failure_rate, 4),
        "scope_unclear":           scope_unclear,
        "routing":                 routing,
        "notes":                   None,
        "validated_at":            now_iso(),
    }

    write_json(out_path, report)
    report_hash = register_artifact(
        WORK_DIR, run_id, ArtifactKey.VALIDATION_REPORT,
        out_path, content_state=ContentState.CANDIDATE, step=STEP)

    # ── Promote reviewed artifacts to VERIFIED if valid ────────────────────────
    # Fix #7: verified is the commit-eligible state (Variant B commit policy)
    if valid:
        for key in reviewed_keys:
            promote_artifact(WORK_DIR, run_id, key, ContentState.VERIFIED)
        print(f"  [state] {len(reviewed_keys)} artifacts → {ContentState.VERIFIED}")

    snap_id = create_snapshot(WORK_DIR, run_id, "post_validation")
    emit_state(WORK_DIR, run_id, "step.done", STEP, {
        "valid":                   valid,
        "routing":                 routing,
        "total_problems":          total,
        "schema_errors":           len(schema_errors),
        "jsonschema_errors":       len(jsonschema_errors),
        "duplicates":              len(duplicates),
        "scope_violations":        len(scope_violations),
        "atomicity_failure_rate":  round(atomicity_failure_rate, 4),
        "snapshot_id":             snap_id,
    })

    print(f"  [done] valid={valid} routing={routing} problems={total} "
          f"schema_err={len(schema_errors)+len(jsonschema_errors)} "
          f"dupes={len(duplicates)} scope_v={len(scope_violations)} "
          f"atomicity_fail={atomicity_failure_rate:.1%}")
    return {
        "status":            "ok",
        "validation_report": report,
        "report_hash":       report_hash,
        "routing":           routing,
    }
