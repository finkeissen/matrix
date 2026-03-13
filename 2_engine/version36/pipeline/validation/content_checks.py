"""Content-level checks that go beyond schema and business rules."""
from __future__ import annotations

import re
from typing import Any


MULTI_TASK_PATTERNS = [r"\band\b", r"\bthen\b", r";"]

PROBLEM_STEPS = {
    "04_problem_generation",
    "05_validation",
    "06_deduplication",
    "07_ranking",
}


def check_problem_content(problem: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    statement = (problem.get("problem_statement") or "").strip()
    if not statement:
        return ["problem_statement missing"]

    if sum(bool(re.search(p, statement, flags=re.IGNORECASE)) for p in MULTI_TASK_PATTERNS) >= 2:
        errors.append("problem_statement may not be atomic")

    if len(statement.split()) < 5:
        errors.append("problem_statement too short to be meaningful")

    title = (problem.get("title") or "").strip()
    if title and len(title.split()) < 2:
        errors.append("title too short")

    return errors


def run_content_checks(step_name: str, data: Any) -> list[str]:
    if step_name not in PROBLEM_STEPS:
        return []

    items = data if isinstance(data, list) else [data]
    errors: list[str] = []

    for i, item in enumerate(items):
        errors.extend([f"[{step_name}][{i}] {e}" for e in check_problem_content(item)])

    return errors
