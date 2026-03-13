"""step_registry.py — Canonical step specifications for the pipeline."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StepSpec:
    name: str
    module_path: str
    input_label: str
    output_label: str

    @property
    def slug(self) -> str:
        return self.name


STEP_SPECS: tuple[StepSpec, ...] = (
    StepSpec("01_scope",             "pipeline.steps.01_scope",             "domain",               "scope"),
    StepSpec("02_seed_expansion",    "pipeline.steps.02_seed_expansion",    "scope+domain",         "seed_set"),
    StepSpec("03_categories",        "pipeline.steps.03_categories",        "scope+seed_set",       "categories"),
    StepSpec("04_problem_generation","pipeline.steps.04_problem_generation","categories",           "generated_problems"),
    StepSpec("05_validation",        "pipeline.steps.05_validation",        "generated_problems",   "validated_problems"),
    StepSpec("06_deduplication",     "pipeline.steps.06_deduplication",     "validated_problems",   "deduplicated_problems"),
    StepSpec("07_ranking",           "pipeline.steps.07_ranking",           "deduplicated_problems","ranked_problems"),
    StepSpec("08_export",            "pipeline.steps.08_export",            "ranked_problems",      "export_bundle"),
)

STEP_MAP: dict[str, StepSpec] = {spec.name: spec for spec in STEP_SPECS}


def all_step_names() -> list[str]:
    return [spec.name for spec in STEP_SPECS]


def get_step_spec(step_name: str) -> StepSpec:
    try:
        return STEP_MAP[step_name]
    except KeyError:
        raise KeyError(f"Unknown step: '{step_name}'. Valid steps: {list(STEP_MAP)}")
