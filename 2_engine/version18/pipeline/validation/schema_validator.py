"""
validation/schema_validator.py — Hard schema validation after every step.

Design:
- validate_step_output() is called by orchestrator after EVERY step
- Returns list of error strings (empty = valid)
- Uses jsonschema Draft7 with FormatChecker (enforces date-time, uri, etc.)
- Business rules are checked separately in business_rules.py
"""

import json
from pathlib import Path
from typing import Optional

import jsonschema
from jsonschema import FormatChecker

from ..config import Config
from ..logging_setup import get_logger

logger = get_logger(__name__)

# Map step name → schema file name
STEP_SCHEMA_MAP = {
    "01_scope":             "scope.schema.json",
    "03_categories":        "category.schema.json",
    "04_problem_generation": "atomic_problem.schema.json",
    "05_validation":        "atomic_problem.schema.json",
    "06_deduplication":     "atomic_problem.schema.json",
    "07_ranking":           "atomic_problem.schema.json",
    "08_export":            None,  # Export step — no schema constraint on output
}


class SchemaValidator:
    def __init__(self, config: Config):
        self._schema_dir = config.schema_dir
        self._schema_cache: dict[str, dict] = {}

    def validate_step_output(self, step_name: str, result: dict) -> list[str]:
        """
        Validate step output dict. Returns list of error strings.
        Empty list = valid.

        result dict must contain:
          - "data": the actual output object to validate
          - "output_path": (optional) path where it was written
        """
        schema_file = STEP_SCHEMA_MAP.get(step_name)
        if schema_file is None:
            return []  # Step explicitly has no schema

        data = result.get("data")
        if data is None:
            return [f"Step '{step_name}' returned no 'data' key in result dict"]

        schema = self._load_schema(schema_file)
        if schema is None:
            logger.warning("schema.not_found", step=step_name, schema_file=schema_file)
            return []

        return self._validate(data, schema, step_name)

    def validate_artifact(self, data: dict, schema_name: str) -> list[str]:
        """Validate any artifact directly by schema name."""
        schema = self._load_schema(f"{schema_name}.schema.json")
        if schema is None:
            return [f"Schema file not found: {schema_name}.schema.json"]
        return self._validate(data, schema, schema_name)

    def validate_and_raise(self, data: dict, schema_name: str):
        """Validate and raise ValueError on failure."""
        errors = self.validate_artifact(data, schema_name)
        if errors:
            raise ValueError(f"Schema validation failed ({schema_name}): {errors}")

    # ── Internal ───────────────────────────────────────────────────────────

    def _load_schema(self, schema_file: str) -> Optional[dict]:
        if schema_file in self._schema_cache:
            return self._schema_cache[schema_file]
        path = self._schema_dir / schema_file
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            schema = json.load(f)
        self._schema_cache[schema_file] = schema
        return schema

    def _validate(self, data, schema: dict, context: str) -> list[str]:
        # Handle both single objects and lists
        items = data if isinstance(data, list) else [data]
        errors = []
        validator = jsonschema.Draft7Validator(schema, format_checker=FormatChecker())
        for i, item in enumerate(items):
            for error in validator.iter_errors(item):
                errors.append(f"[{context}][{i}] {error.json_path}: {error.message}")
        return errors
