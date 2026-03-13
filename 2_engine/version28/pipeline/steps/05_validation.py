from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.ingestion_loader import IngestionLoader
from pipeline.validation.business_rules import validate_business_rules
from pipeline.validation.content_checks import run_content_checks
from pipeline.validation.result_quality import run_quality_checks


def _text_blob(problem: dict[str, Any]) -> str:
    parts = [
        str(problem.get("title", "")),
        str(problem.get("problem_statement", "")),
        str(problem.get("category", "")),
    ]
    return " ".join(parts).lower()


def _apply_ingestion_rules(problem: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    text = _text_blob(problem)

    for pattern in rules.get("failure_patterns", []):
        name = str(pattern.get("name", "")).strip()
        triggers = pattern.get("triggers", [])
        if not name or not isinstance(triggers, list):
            continue
        for trigger in triggers:
            if isinstance(trigger, str) and trigger.lower() in text:
                errors.append(f"matched_failure_pattern:{name}")
                break

    for gate in rules.get("case_gates", []):
        gate_id = str(gate.get("id", "")).strip()
        status = str(gate.get("status", "")).strip().upper()
        terms = gate.get("trigger_terms", [])
        if status != "STOP" or not gate_id or not isinstance(terms, list):
            continue
        for term in terms:
            if isinstance(term, str) and term.lower() in text:
                errors.append(f"blocked_by_case_gate:{gate_id}")
                break

    return errors


def _safe_list(result: Any) -> list[str]:
    if result is None:
        return []
    if isinstance(result, list):
        return [str(x) for x in result]
    return [str(result)]


def run(ctx, domain, config, prompt_loader):
    in_path = ctx.intermediate_dir() / "04_problem_generation.json"
    payload = json.loads(in_path.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        problems = payload
    elif isinstance(payload, dict):
        problems = payload.get("problems", payload.get("data", []))
    else:
        problems = []

    loader = IngestionLoader(Path(__file__).resolve().parent.parent.parent)
    rules = loader.load_rules()

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for item in problems:
        errors: list[str] = []
        errors.extend(_safe_list(validate_business_rules("05_validation", item)))
        errors.extend(_safe_list(run_content_checks("05_validation", item)))
        errors.extend(_safe_list(run_quality_checks("05_validation", item)))
        errors.extend(_apply_ingestion_rules(item, rules))

        if errors:
            rejected.append({"item": item, "errors": errors})
        else:
            accepted.append(item)

    out = ctx.intermediate_dir() / "05_validation.json"

    run_dir = getattr(ctx, "run_dir", None)
    if run_dir is None:
        raise RuntimeError("RunContext has no run_dir attribute")

    rejected_dir = run_dir / "rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)

    rej = rejected_dir / "content_failures.json"

    out.write_text(json.dumps(accepted, indent=2, ensure_ascii=False), encoding="utf-8")
    rej.write_text(json.dumps(rejected, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "data": accepted,
        "output_path": str(out),
        "counts": {
            "input": len(problems),
            "accepted": len(accepted),
            "rejected": len(rejected),
        },
    }
