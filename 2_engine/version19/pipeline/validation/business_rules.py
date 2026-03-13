"""Business-rule validation for pipeline artifacts."""
from __future__ import annotations
from typing import Any

def check_problem_business_rules(problem: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ['problem_id','title','problem_statement','category','difficulty','source_run_id','created_at']:
        if not problem.get(field):
            errors.append(f"{field} must be present and non-empty")
    if problem.get('difficulty') and problem['difficulty'] not in {'easy','medium','hard'}:
        errors.append(f"difficulty must be one of easy|medium|hard, got {problem['difficulty']}")
    statement = problem.get('problem_statement','')
    if statement and statement.strip().endswith('?') and statement.count('?') > 1:
        errors.append('problem_statement appears to contain multiple questions')
    return errors

def check_scope_business_rules(scope: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not scope.get('boundaries'):
        errors.append('scope.boundaries must not be empty')
    if 'confidence_score' in scope:
        score = scope.get('confidence_score')
        if not isinstance(score, (int, float)) or not (0 <= score <= 1):
            errors.append('scope.confidence_score must be between 0 and 1')
    return errors

def validate_business_rules(step_name: str, data: Any) -> list[str]:
    items = data if isinstance(data, list) else [data]
    errors: list[str] = []
    for i, item in enumerate(items):
        errs = check_scope_business_rules(item) if step_name == '01_scope' else check_problem_business_rules(item)
        errors.extend([f'[{step_name}][{i}] {e}' for e in errs])
    return errors
