"""
tests/test_schema_validation.py — Tests for SchemaValidator.
"""

import json
import pytest
from pathlib import Path

# Minimal valid AtomicProblem fixture
VALID_PROBLEM = {
    "problem_id": "ap_abc123",
    "title": "Heat transfer in a thin rod",
    "problem_statement": "A thin rod of length 1m is heated at one end. Calculate the temperature distribution.",
    "category": "conduction",
    "difficulty": "medium",
    "source_run_id": "run_2026_03_07_001",
    "created_at": "2026-03-07T10:00:00Z",
}

INVALID_PROBLEM_MISSING_FIELD = {
    "problem_id": "ap_abc124",
    "title": "Missing statement",
    # problem_statement is missing — required field
    "category": "conduction",
    "difficulty": "medium",
    "source_run_id": "run_2026_03_07_001",
}

INVALID_PROBLEM_BAD_DIFFICULTY = {
    **VALID_PROBLEM,
    "problem_id": "ap_abc125",
    "difficulty": "super_hard",  # not in enum
}

INVALID_PROBLEM_BAD_DATE = {
    **VALID_PROBLEM,
    "problem_id": "ap_abc126",
    "created_at": "not-a-date",  # format: date-time should be enforced
}


def make_validator():
    from pipeline.config import Config
    from pipeline.validation.schema_validator import SchemaValidator
    config = Config.from_env()
    return SchemaValidator(config)


def test_valid_problem_passes():
    validator = make_validator()
    errors = validator.validate_artifact(VALID_PROBLEM, "atomic_problem")
    assert errors == [], f"Expected no errors, got: {errors}"


def test_missing_required_field_fails():
    validator = make_validator()
    errors = validator.validate_artifact(INVALID_PROBLEM_MISSING_FIELD, "atomic_problem")
    assert any("problem_statement" in e for e in errors), \
        f"Expected error about problem_statement, got: {errors}"


def test_invalid_enum_fails():
    validator = make_validator()
    errors = validator.validate_artifact(INVALID_PROBLEM_BAD_DIFFICULTY, "atomic_problem")
    assert any("difficulty" in e or "super_hard" in e for e in errors), \
        f"Expected error about difficulty enum, got: {errors}"


def test_invalid_date_format_fails():
    """FormatChecker must be active — without it, date-time format is ignored."""
    validator = make_validator()
    errors = validator.validate_artifact(INVALID_PROBLEM_BAD_DATE, "atomic_problem")
    assert any("date" in e.lower() or "created_at" in e for e in errors), \
        f"Expected FormatChecker to catch bad date, got: {errors}"


def test_list_of_problems():
    validator = make_validator()
    problems = [VALID_PROBLEM, {**VALID_PROBLEM, "problem_id": "ap_abc999"}]
    errors = validator._validate(problems, validator._load_schema("atomic_problem.schema.json"), "test")
    assert errors == []
