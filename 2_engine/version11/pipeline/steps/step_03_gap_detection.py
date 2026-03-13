"""
step_03_gap_detection.py — Detect missing/underrepresented categories.
Type: LLM | Model: 35b (loaded in LM Studio)
Snapshot after: yes
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES
from common import (
    llm_call, parse_json_response, sha256_file,
    artifact_dir, write_json, register_artifact,
    emit_state, novelty_guard_check, novelty_guard_record, make_task_id,
    create_snapshot,
)

STEP = "03_enrichment_03_gap_detection"

PROMPT_TEMPLATE = """You are a precise academic knowledge engineer. Identify gaps and underrepresented areas in the category list for {subdomain_label} (SD: {subdomain_id}).

You will receive:
1. Scope definition
2. Canonical structure (authoritative table of contents)
3. Normalized category list

Identify:
- Topics from scope.boundaries NOT covered by any category
- Topics from canonical structure NOT covered by any category
- Categories with estimated_problem_count < 5 (underrepresented)
- Categories with estimated_problem_count > 40 (too broad — suggest split)

Input scope:
{scope_json}

Input canonical structure:
{structure_json}

Input normalized categories:
{categories_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "covered_topics": [<string>],
  "missing_topics": [
    {{
      "topic": <string>,
      "source": "scope_boundary" | "canonical_structure" | "domain_knowledge",
      "suggested_category": <string>,
      "action": "add_category" | "merge_into_existing" | "expand_existing"
    }}
  ],
  "underrepresented_categories": [
    {{
      "category_index": <integer>,
      "category_name": <string>,
      "issue": <string>,
      "suggestion": <string>
    }}
  ],
  "oversized_categories": [
    {{
      "category_index": <integer>,
      "category_name": <string>,
      "suggestion": <string>
    }}
  ],
  "overall_coverage": "good" | "acceptable" | "poor",
  "notes": <string or null>
}}"""


def validate_output(obj: dict) -> list[str]:
    errors = []
    if "overall_coverage" not in obj:
        errors.append("missing field: overall_coverage")
    if obj.get("overall_coverage") not in ("good", "acceptable", "poor", None):
        errors.append("overall_coverage must be good|acceptable|poor")
    return errors


def run(run_id: str, scope: dict, scope_hash: str,
        structure: dict, structure_hash: str,
        normalized: dict, normalized_hash: str,
        kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "gap_detection": {...}, "gap_hash": "..."}
    Snapshot created after completion.
    """
    print(f"[{STEP}] run={run_id}")

    inputs = {
        "normalized_categories_hash": normalized_hash,
        "scope_hash": scope_hash,
        "canonical_structure_hash": structure_hash,
        "kb_snapshot_id": kb_snapshot_id,
    }
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "gap_detection.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        gap = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        return {"status": "ok", "gap_detection": gap,
                "gap_hash": sha256_file(out_path)}

    emit_state(WORK_DIR, run_id, "step.start", STEP, {"task_id": task_id})

    prompt = PROMPT_TEMPLATE.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        structure_json=json.dumps(structure, indent=2, ensure_ascii=False),
        categories_json=json.dumps(normalized, indent=2, ensure_ascii=False),
    )
    raw = llm_call(prompt, retries=DEFAULT_RETRIES)
    gap = parse_json_response(raw)

    if gap is None:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": "non-JSON"})
        return {"status": "stop", "stop_code": "llm_output_invalid"}

    errors = validate_output(gap)
    if errors:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors)})
        return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    write_json(out_path, gap)
    gap_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:gap_detection", out_path,
                                 content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)

    snap_id = create_snapshot(WORK_DIR, run_id, "pre_generation")
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "overall_coverage": gap.get("overall_coverage"),
                "snapshot_id": snap_id})

    print(f"  [done] coverage={gap.get('overall_coverage')} "
          f"missing={len(gap.get('missing_topics', []))}")
    return {"status": "ok", "gap_detection": gap, "gap_hash": gap_hash}
