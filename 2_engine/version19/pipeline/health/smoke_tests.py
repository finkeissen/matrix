"""Fast smoke tests for environment, prompts, schemas, and step loading."""
from __future__ import annotations
import importlib
from ..prompts.loader import PromptLoader
from ..validation.schema_validator import SchemaValidator
from ..dedup import run_full_dedup

def _test_llm_config(config) -> bool:
    return bool(config.lm_url and config.lm_model and config.request_timeout > 0)

def _test_prompt_loader(config) -> bool:
    loader = PromptLoader(config)
    try:
        loader.resolve_versions(['01_scope'])
        return True
    except Exception:
        return False

def _test_schema_registry(config) -> bool:
    validator = SchemaValidator(config)
    return validator._load_schema('atomic_problem.schema.json') is not None

def _test_dedup_layer() -> bool:
    result = run_full_dedup([], known_hashes=set(), known_normalized=set())
    return result['counts']['input'] == 0 and result['counts']['accepted'] == 0

def _test_step_imports() -> bool:
    try:
        for name in ['01_scope','02_seed_expansion','03_categories','04_problem_generation','05_validation','06_deduplication','07_ranking','08_export']:
            mod = importlib.import_module(f'pipeline.steps.{name}')
            assert hasattr(mod, 'run')
        return True
    except Exception:
        return False

def run_smoke_tests(config) -> dict:
    results = {
        'llm_configured': _test_llm_config(config),
        'prompt_loading': _test_prompt_loader(config),
        'schema_registry': _test_schema_registry(config),
        'dedup_layer': _test_dedup_layer(),
        'step_imports': _test_step_imports(),
    }
    failures = [k for k, v in results.items() if not v]
    return {'ok': not failures, 'results': results, 'failures': failures}
