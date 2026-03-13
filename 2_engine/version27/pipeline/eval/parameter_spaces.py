from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Profile:
    name: str
    temperature: float
    top_p: float
    max_tokens: int | None = None


STEP_BASELINES: dict[str, list[Profile]] = {
    "01_scope": [
        Profile("conservative", 0.1, 0.80, 800),
        Profile("balanced", 0.2, 0.90, 900),
        Profile("exploratory", 0.4, 0.95, 1000),
    ],
    "02_seed_expansion": [
        Profile("conservative", 0.3, 0.85, 1200),
        Profile("balanced", 0.6, 0.92, 1400),
        Profile("exploratory", 0.8, 0.97, 1600),
    ],
    "03_categories": [
        Profile("conservative", 0.1, 0.80, 700),
        Profile("balanced", 0.2, 0.90, 800),
        Profile("exploratory", 0.4, 0.95, 900),
    ],
    "04_problem_generation": [
        Profile("conservative", 0.2, 0.85, 1400),
        Profile("balanced", 0.5, 0.92, 1800),
        Profile("exploratory", 0.8, 0.97, 2200),
    ],
    "05_validation": [
        Profile("conservative", 0.0, 0.80, 900),
        Profile("balanced", 0.1, 0.90, 1000),
        Profile("exploratory", 0.2, 0.95, 1100),
    ],
}


STEP_SEARCH_SPACES: dict[str, dict[str, list[Any]]] = {
    "01_scope": {
        "temperature": [0.0, 0.1, 0.2, 0.3],
        "top_p": [0.80, 0.90, 0.95],
        "max_tokens": [700, 900, 1100],
    },
    "02_seed_expansion": {
        "temperature": [0.3, 0.5, 0.7, 0.9],
        "top_p": [0.85, 0.92, 0.97],
        "max_tokens": [1000, 1400, 1800],
    },
    "03_categories": {
        "temperature": [0.0, 0.1, 0.2, 0.3],
        "top_p": [0.80, 0.90, 0.95],
        "max_tokens": [600, 800, 1000],
    },
    "04_problem_generation": {
        "temperature": [0.2, 0.4, 0.6, 0.8],
        "top_p": [0.85, 0.92, 0.97],
        "max_tokens": [1200, 1800, 2400],
    },
    "05_validation": {
        "temperature": [0.0, 0.1, 0.2],
        "top_p": [0.80, 0.90, 0.95],
        "max_tokens": [800, 1000, 1200],
    },
}


SUITABILITY_THRESHOLDS: dict[str, float] = {
    "01_scope": 0.60,
    "02_seed_expansion": 0.55,
    "03_categories": 0.65,
    "04_problem_generation": 0.65,
    "05_validation": 0.75,
}
