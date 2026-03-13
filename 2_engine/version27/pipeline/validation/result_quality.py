"""Quality gates for generated results and run-level distributions."""
from __future__ import annotations

from collections import Counter
from typing import Any


PROBLEM_STEPS = {
    "04_problem_generation",
    "05_validation",
    "06_deduplication",
    "07_ranking",
}

STRICT_DISTRIBUTION_STEPS = {
    "05_validation",
    "06_deduplication",
    "07_ranking",
}


def _statement_limits_for_step(step_name: str) -> tuple[int, int]:
    if step_name == "04_problem_generation":
        return (30, 650)
    return (30, 500)


def check_problem_quality(problem: dict[str, Any], step_name: str) -> list[str]:
    errors: list[str] = []

    min_len, max_len = _statement_limits_for_step(step_name)

    statement = str(problem.get("problem_statement", "") or "")
    if len(statement) < min_len:
        errors.append("statement_too_short")
    if len(statement) > max_len:
        errors.append("statement_too_long")

    if problem.get("difficulty") not in {"easy", "medium", "hard", "expert"}:
        errors.append("invalid_difficulty")

    return errors


def check_distribution_quality(problems: list[dict[str, Any]]) -> list[str]:
    if not problems:
        return ["no_problems"]

    errors: list[str] = []
    counts = Counter(str(p.get("category", "unknown")) for p in problems)
    total = len(problems)

    for category, n in counts.items():
        if n / total > 0.60:
            errors.append(f"category_overrepresented:{category}")

    return errors


def run_quality_checks(step_name: str, data: Any) -> list[str]:
    if step_name not in PROBLEM_STEPS:
        return []

    items = data if isinstance(data, list) else [data]
    errors: list[str] = []

    for i, item in enumerate(items):
        if isinstance(item, dict):
            item_errors = check_problem_quality(item, step_name)
        else:
            item_errors = ["invalid_item_type"]
        errors.extend([f"[{step_name}][{i}] {e}" for e in item_errors])

    if isinstance(data, list) and step_name in STRICT_DISTRIBUTION_STEPS:
        errors.extend([f"[{step_name}] {e}" for e in check_distribution_quality(data)])

    return errors
