from __future__ import annotations

import importlib
from typing import Any


STEP_MODULES = [
    "pipeline.steps.01_scope",
    "pipeline.steps.02_seed_expansion",
    "pipeline.steps.03_categories",
    "pipeline.steps.04_problem_generation",
    "pipeline.steps.05_validation",
    "pipeline.steps.06_deduplication",
    "pipeline.steps.07_ranking",
    "pipeline.steps.08_export",
]


def _check_llm_configured(config) -> bool:
    return bool(getattr(config, "lm_url", None))


def _check_prompt_loading(config) -> bool:
    prompts_dir = config.prompts_dir
    return prompts_dir.exists() and prompts_dir.is_dir()


def _check_schema_registry(config) -> bool:
    schema_dir = config.schema_dir
    return schema_dir.exists() and schema_dir.is_dir()


def _check_dedup_layer() -> bool:
    try:
        import pipeline.dedup  # noqa: F401
        return True
    except Exception:
        return False


def _check_step_imports() -> tuple[bool, list[str]]:
    errors: list[str] = []

    for module_name in STEP_MODULES:
        try:
            mod = importlib.import_module(module_name)

            if not hasattr(mod, "run"):
                errors.append(f"{module_name}: missing run()")
        except Exception as e:
            errors.append(f"{module_name}: {type(e).__name__}: {e}")

    return (len(errors) == 0, errors)


def run_smoke_tests(config) -> dict[str, Any]:
    step_imports_ok, step_import_errors = _check_step_imports()

    results = {
        "llm_configured": _check_llm_configured(config),
        "prompt_loading": _check_prompt_loading(config),
        "schema_registry": _check_schema_registry(config),
        "dedup_layer": _check_dedup_layer(),
        "step_imports": step_imports_ok,
    }

    failures = [name for name, ok in results.items() if not ok]

    payload: dict[str, Any] = {
        "ok": len(failures) == 0,
        "results": results,
        "failures": failures,
    }

    if step_import_errors:
        payload["step_import_errors"] = step_import_errors

    return payload
