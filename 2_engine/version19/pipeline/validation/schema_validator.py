"""Hard schema validation after every step."""
from __future__ import annotations
import json
from typing import Optional
import jsonschema
from jsonschema import FormatChecker
from ..config import Config
from ..logging_setup import get_logger

logger = get_logger(__name__)

STEP_SCHEMA_MAP = {
    '01_scope': 'scope.schema.json',
    '02_seed_expansion': None,
    '03_categories': 'category.schema.json',
    '04_problem_generation': 'atomic_problem.schema.json',
    '05_validation': 'atomic_problem.schema.json',
    '06_deduplication': 'atomic_problem.schema.json',
    '07_ranking': 'atomic_problem.schema.json',
    '08_export': None,
}

class SchemaValidator:
    def __init__(self, config: Config):
        self._schema_dir = config.schema_dir
        self._schema_cache: dict[str, dict] = {}

    def validate_step_output(self, step_name: str, result: dict) -> list[str]:
        schema_file = STEP_SCHEMA_MAP.get(step_name)
        if schema_file is None:
            return []
        data = result.get('data')
        if data is None:
            return [f"Step '{step_name}' returned no 'data' key in result dict"]
        schema = self._load_schema(schema_file)
        if schema is None:
            logger.warning('schema.not_found', step=step_name, schema_file=schema_file)
            return []
        return self._validate(data, schema, step_name)

    def validate_artifact(self, data: dict, schema_name: str) -> list[str]:
        schema = self._load_schema(f'{schema_name}.schema.json')
        if schema is None:
            return [f'Schema file not found: {schema_name}.schema.json']
        return self._validate(data, schema, schema_name)

    def _load_schema(self, schema_file: str) -> Optional[dict]:
        if schema_file in self._schema_cache:
            return self._schema_cache[schema_file]
        path = self._schema_dir / schema_file
        if not path.exists():
            return None
        schema = json.loads(path.read_text(encoding='utf-8'))
        self._schema_cache[schema_file] = schema
        return schema

    def _validate(self, data, schema: dict, context: str) -> list[str]:
        items = data if isinstance(data, list) else [data]
        validator = jsonschema.Draft7Validator(schema, format_checker=FormatChecker())
        errors = []
        for i, item in enumerate(items):
            for error in validator.iter_errors(item):
                errors.append(f'[{context}][{i}] {error.json_path}: {error.message}')
        return errors
