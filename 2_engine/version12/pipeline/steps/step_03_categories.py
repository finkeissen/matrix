"""
step_03_categories.py — Identify thematic clusters within subdomain.
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

STEP = "03_enrichment_01_categories"

PROMPT_TEMPLATE = """You are a precise academic knowledge engineer. Your task is to identify the thematic categories within a subdomain for an atomic problem generation pipeline.

You will receive:
1. A scope definition for the subdomain {subdomain_label}
2. A canonical structure (authoritative table of contents or topic index)

Produce a flat list of thematic categories. Each category will be a generation unit — one LLM call per category generates all atomic problems for that category.

Input scope:
{scope_json}

Input canonical structure:
{structure_json}

Rules:
- Categories must be mutually exclusive and collectively exhaustive
- Category names in English, Title Case
- Specific enough to guide problem generation (no "Miscellaneous" or "Other")
- estimated_problem_count per category: 5–40; split larger topics, merge smaller ones
- Base categories on canonical structure; add categories for important gaps

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "category_count": <integer>,
  "items": [
    {{
      "name": <string: Title Case English>,
      "description": <string: one sentence — what problems belong here>,
      "canonical_chapter_ref": <integer or null>,
      "estimated_problem_count": <integer>
    }}
  ]
}}"""


def validate_output(obj: dict) -> list[str]:
    errors = []
    for field in ["subdomain_id", "items"]:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if "items" in obj:
        if not obj["items"]:
            errors.append("items array is empty")
        for item in obj["items"]:
            if "name" not in item or "description" not in item:
                errors.append(f"item missing name or description: {item}")
    return errors


def run(run_id: str, scope: dict, scope_hash: str,
        structure: dict, structure_hash: str, kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "categories": {...}, "categories_hash": "..."}
    """
    print(f"[{STEP}] run={run_id}")

    inputs = {"scope_hash": scope_hash, "canonical_structure_hash": structure_hash,
              "kb_snapshot_id": kb_snapshot_id}
    task_id = make_task_id(STEP, inputs)

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "categories.json"

    if novelty_guard_check(WORK_DIR, run_id, task_id) and out_path.exists():
        print(f"  [novelty] cache hit")
        cats = json.loads(out_path.read_text())
        emit_state(WORK_DIR, run_id, "step.cache_hit", STEP, {"task_id": task_id})
        return {"status": "ok", "categories": cats,
                "categories_hash": sha256_file(out_path)}

    emit_state(WORK_DIR, run_id, "step.start", STEP, {"task_id": task_id})

    prompt = PROMPT_TEMPLATE.format(
        subdomain_label=scope.get("subdomain", ""),
        subdomain_id=scope.get("subdomain_id", ""),
        scope_json=json.dumps(scope, indent=2, ensure_ascii=False),
        structure_json=json.dumps(structure, indent=2, ensure_ascii=False),
    )
    raw  = llm_call(prompt, retries=DEFAULT_RETRIES)
    cats = parse_json_response(raw)

    if cats is None:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": "non-JSON"})
        return {"status": "stop", "stop_code": "llm_output_invalid"}

    errors = validate_output(cats)
    if errors:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "llm_output_invalid", "reason": str(errors)})
        return {"status": "stop", "stop_code": "llm_output_invalid", "errors": errors}

    cats["category_count"] = len(cats["items"])

    write_json(out_path, cats)
    cats_hash = register_artifact(WORK_DIR, run_id, f"{STEP}:categories", out_path,
                                  content_state="candidate", step=STEP)
    novelty_guard_record(WORK_DIR, run_id, task_id, STEP)
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"task_id": task_id, "category_count": cats["category_count"]})

    print(f"  [done] {cats['category_count']} categories")
    return {"status": "ok", "categories": cats, "categories_hash": cats_hash}
