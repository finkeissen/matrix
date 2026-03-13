"""Quality gates for generated results and run-level distributions."""
from __future__ import annotations
from collections import Counter
from typing import Any

def check_problem_quality(problem: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    statement = problem.get('problem_statement', '')
    if len(statement) < 30:
        errors.append('statement_too_short')
    if len(statement) > 500:
        errors.append('statement_too_long')
    if problem.get('difficulty') not in {'easy','medium','hard'}:
        errors.append('invalid_difficulty')
    return errors

def check_distribution_quality(problems: list[dict[str, Any]]) -> list[str]:
    if not problems:
        return ['no_problems']
    errors: list[str] = []
    counts = Counter(p.get('category', 'unknown') for p in problems)
    total = len(problems)
    for category, n in counts.items():
        if n / total > 0.60:
            errors.append(f'category_overrepresented:{category}')
    return errors

def run_quality_checks(step_name: str, data: Any) -> list[str]:
    if step_name == '01_scope':
        return []
    items = data if isinstance(data, list) else [data]
    errors: list[str] = []
    for i, item in enumerate(items):
        errors.extend([f'[{step_name}][{i}] {e}' for e in check_problem_quality(item)])
    if isinstance(data, list):
        errors.extend([f'[{step_name}] {e}' for e in check_distribution_quality(data)])
    return errors
