from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any


PROBLEM_STYLES = [
    {
        "verb": "analyze",
        "title": "Analyze",
        "task": "identify the governing principle",
        "deliverable": "justify the conclusion briefly",
    },
    {
        "verb": "derive",
        "title": "Derive",
        "task": "derive the controlling relationship",
        "deliverable": "show the key steps clearly",
    },
    {
        "verb": "compare",
        "title": "Compare",
        "task": "compare two plausible interpretations",
        "deliverable": "decide which one is physically consistent",
    },
    {
        "verb": "estimate",
        "title": "Estimate",
        "task": "estimate the dominant magnitude",
        "deliverable": "explain why smaller effects can be neglected",
    },
    {
        "verb": "predict",
        "title": "Predict",
        "task": "predict the state change after a controlled intervention",
        "deliverable": "explain the direction of change",
    },
    {
        "verb": "explain",
        "title": "Explain",
        "task": "explain an apparently counterintuitive result",
        "deliverable": "resolve the tension with a physical argument",
    },
    {
        "verb": "evaluate",
        "title": "Evaluate",
        "task": "evaluate whether a proposed interpretation is valid",
        "deliverable": "identify the decisive criterion",
    },
    {
        "verb": "identify",
        "title": "Identify",
        "task": "identify the limiting constraint",
        "deliverable": "show how the bottleneck controls the outcome",
    },
]

GENERIC_CONTEXTS = [
    {
        "scenario": "a controlled physical system with a measurable state change",
        "goal": "determine the dominant mechanism",
        "variables": "the initial state, the imposed change, and the key material properties",
        "check": "State the main assumption and include one physical consistency check.",
        "difficulty_bias": "easy",
    },
    {
        "scenario": "an engineering situation with competing effects",
        "goal": "separate the dominant contribution from weaker corrections",
        "variables": "the main state variables and the control parameter",
        "check": "Explain which quantity sets the scale of the result.",
        "difficulty_bias": "medium",
    },
    {
        "scenario": "a limiting-case approximation of a real system",
        "goal": "test whether the approximation remains defensible",
        "variables": "the simplifications, the driving variables, and the implied response",
        "check": "State where the approximation is useful and where it may fail.",
        "difficulty_bias": "hard",
    },
]

THERMO_CONTEXTS = [
    {
        "scenario": "a piston-cylinder compression of an ideal gas",
        "goal": "determine the final temperature and boundary work",
        "variables": "the initial pressure, temperature, gas mass, and process exponent",
        "check": "State whether the process is best treated as isothermal, adiabatic, or polytropic.",
        "difficulty_bias": "easy",
    },
    {
        "scenario": "a rigid insulated tank briefly connected to a high-pressure line",
        "goal": "determine the final state inside the tank",
        "variables": "the tank volume, inlet state, initial state, and added mass",
        "check": "Use a control-volume energy balance and identify the dominant storage term.",
        "difficulty_bias": "medium",
    },
    {
        "scenario": "a throttling valve in a refrigeration loop",
        "goal": "predict the outlet condition",
        "variables": "the inlet pressure, inlet enthalpy, and downstream pressure",
        "check": "Explain why enthalpy is the key quantity across the valve.",
        "difficulty_bias": "medium",
    },
    {
        "scenario": "a counterflow heat exchanger at steady state",
        "goal": "estimate the outlet temperatures and the thermal bottleneck",
        "variables": "the inlet temperatures, mass flow rates, and heat-capacity rates",
        "check": "Identify which stream limits the temperature approach.",
        "difficulty_bias": "medium",
    },
    {
        "scenario": "a turbine stage with measurable irreversibility",
        "goal": "estimate the work output and entropy generation trend",
        "variables": "the inlet state, outlet pressure, reference isentropic state, and mass flow rate",
        "check": "Use the isentropic case as the reference for the real process.",
        "difficulty_bias": "hard",
    },
    {
        "scenario": "a compressor with non-negligible shaft work input",
        "goal": "estimate the outlet temperature and assess the efficiency interpretation",
        "variables": "the inlet state, pressure ratio, mass flow rate, and isentropic efficiency",
        "check": "State clearly how the real compressor departs from the ideal baseline.",
        "difficulty_bias": "hard",
    },
    {
        "scenario": "a mixing chamber with two inlet streams at different temperatures",
        "goal": "determine the mixed outlet state",
        "variables": "the inlet enthalpies, mass flow rates, and possible heat loss",
        "check": "Explain why conserved flow quantities govern the outlet state.",
        "difficulty_bias": "easy",
    },
    {
        "scenario": "a closed container undergoing phase change during heating",
        "goal": "identify which property relation controls the final state",
        "variables": "the initial phase condition, heat input, and container constraint",
        "check": "Clarify when saturation data is required.",
        "difficulty_bias": "hard",
    },
    {
        "scenario": "a nozzle accelerating a compressible fluid",
        "goal": "predict the velocity change and the dominant energy conversion",
        "variables": "the inlet enthalpy, exit pressure, and inlet velocity",
        "check": "Explain why kinetic energy cannot be neglected.",
        "difficulty_bias": "medium",
    },
    {
        "scenario": "a sealed vessel heated from a known initial equilibrium state",
        "goal": "determine how pressure and temperature evolve",
        "variables": "the vessel volume, initial state, heat input, and fluid model",
        "check": "State why the constant-volume constraint matters.",
        "difficulty_bias": "easy",
    },
]

CATEGORY_CONTEXT_HINTS = {
    "foundations": [
        "Focus on first-law reasoning.",
        "Emphasize state variables and system boundaries.",
        "Make the modeling choice explicit.",
    ],
    "applications": [
        "Connect the result to an engineering device.",
        "Interpret the result in practical terms.",
        "Frame the task around design or operation.",
    ],
    "analysis": [
        "Highlight the tradeoff between two interpretations.",
        "Test whether the simplification is defensible.",
        "Emphasize sensitivity to assumptions.",
    ],
}

CATEGORY_DIFFICULTY_OVERRIDES = {
    "foundations": ["easy", "easy", "medium", "easy", "medium", "easy", "medium", "easy"],
    "applications": ["medium", "medium", "hard", "medium", "hard", "medium", "hard", "medium"],
    "analysis": ["medium", "hard", "hard", "medium", "expert", "hard", "expert", "hard"],
}

STATEMENT_PATTERNS = [
    (
        "Consider {scenario} in {domain}. For {category_label}, ask the solver to {task} "
        "and {goal}. Use {variables}. {check} {hint} The solution should {deliverable}."
    ),
    (
        "In {domain}, frame a {category_label} problem using {scenario}. The solver should {task} "
        "while trying to {goal}. Base the reasoning on {variables}. {check} {hint} "
        "The response should {deliverable}."
    ),
    (
        "Create a {category_label} task in {domain} built around {scenario}. Require the solver to {task}. "
        "The scenario should provide {variables}. {check} {hint} The final write-up should {deliverable}."
    ),
]


def _normalize_categories(raw_categories: list[Any]) -> list[str]:
    categories: list[str] = []
    for item in raw_categories:
        if isinstance(item, str) and item.strip():
            categories.append(item.strip())
        elif isinstance(item, dict):
            category = item.get("category")
            if isinstance(category, str) and category.strip():
                categories.append(category.strip())
    return categories


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return slug.strip("_") or "item"


def _read_positive_int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"Environment variable {name} must be greater than zero, got {value}")
    return value


def _category_kind(category: str) -> str:
    slug = _slugify(category)
    if slug.endswith("foundations") or "foundation" in slug:
        return "foundations"
    if slug.endswith("applications") or "application" in slug:
        return "applications"
    if slug.endswith("analysis") or "analysis" in slug:
        return "analysis"
    return "generic"


def _context_pool_for_domain(domain: str) -> list[dict[str, str]]:
    domain_slug = _slugify(domain)
    if "thermodynamics" in domain_slug:
        return THERMO_CONTEXTS
    return GENERIC_CONTEXTS


def _hint_for_category(category: str, variant_index: int) -> str:
    kind = _category_kind(category)
    hints = CATEGORY_CONTEXT_HINTS.get(kind, [])
    if not hints:
        return "Keep the reasoning physically grounded."
    return hints[variant_index % len(hints)]


def _difficulty_for(category: str, context: dict[str, str], variant_index: int) -> str:
    kind = _category_kind(category)
    overrides = CATEGORY_DIFFICULTY_OVERRIDES.get(kind)
    if overrides:
        return overrides[variant_index % len(overrides)]
    return context.get("difficulty_bias", "medium")


def _clean_spaces(text: str) -> str:
    return " ".join(text.split()).strip()


def _fit_statement(pattern: str, **kwargs: str) -> str:
    statement = _clean_spaces(pattern.format(**kwargs))
    if len(statement) <= 495:
        return statement

    compact = dict(kwargs)
    compact["hint"] = ""
    statement = _clean_spaces(pattern.format(**compact))
    if len(statement) <= 495:
        return statement

    compact["check"] = ""
    statement = _clean_spaces(pattern.format(**compact))
    if len(statement) <= 495:
        return statement

    compact["deliverable"] = "answer briefly"
    statement = _clean_spaces(pattern.format(**compact))
    if len(statement) <= 495:
        return statement

    compact["variables"] = compact["variables"].split(", and ")[0]
    statement = _clean_spaces(pattern.format(**compact))
    if len(statement) <= 495:
        return statement

    return statement[:492].rstrip(" ,.;") + "..."


def _build_problem(domain: str, category: str, index: int, variant_index: int, run_id: str, now: str) -> dict[str, Any]:
    style = PROBLEM_STYLES[variant_index % len(PROBLEM_STYLES)]
    context_pool = _context_pool_for_domain(domain)
    context = context_pool[(index + variant_index) % len(context_pool)]
    difficulty = _difficulty_for(category, context, variant_index)
    pattern = STATEMENT_PATTERNS[(index + variant_index) % len(STATEMENT_PATTERNS)]

    category_label = category.replace("_", " ").title()
    category_slug = _slugify(category)
    hint = _hint_for_category(category, variant_index)

    title = f"{style['title']} {category_label} case {variant_index + 1}"
    statement = _fit_statement(
        pattern,
        domain=domain,
        scenario=context["scenario"],
        category_label=category_label,
        task=style["task"],
        goal=context["goal"],
        variables=context["variables"],
        check=context["check"],
        hint=hint,
        deliverable=style["deliverable"],
    )

    problem_key = (
        f"{run_id}:{category_slug}:{variant_index + 1}:{style['verb']}:"
        f"{context['scenario']}:{context['goal']}:{difficulty}"
    )
    problem_suffix = sha1(problem_key.encode("utf-8")).hexdigest()[:10]

    return {
        "problem_id": f"ap_{category_slug}_{variant_index + 1:02d}_{problem_suffix}",
        "title": title,
        "problem_statement": statement,
        "category": category,
        "difficulty": difficulty,
        "source_run_id": run_id,
        "created_at": now,
        "tags": [
            domain,
            category,
            style["verb"],
            _slugify(context["scenario"]),
            difficulty,
        ],
        "content_state": "candidate",
    }


def run(ctx, step_input: dict, config, prompt_loader):
    domain: str = step_input["domain"]
    raw_categories: list = step_input.get("categories", [domain])
    categories = _normalize_categories(raw_categories) or [domain]

    eval_mode = os.getenv("PIPELINE_EVAL_MODE", "0") == "1"
    problems_per_category = _read_positive_int_env("PROBLEMS_PER_CATEGORY", 10 if eval_mode else 1)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    problems: list[dict[str, Any]] = []

    for category_index, category in enumerate(categories, start=1):
        for variant_index in range(problems_per_category):
            problems.append(
                _build_problem(
                    domain=domain,
                    category=category,
                    index=category_index,
                    variant_index=variant_index,
                    run_id=ctx.manifest.run_id,
                    now=now,
                )
            )

    return {
        "data": problems,
        "counts": {
            "generated": len(problems),
            "categories": len(categories),
            "problems_per_category": problems_per_category,
        },
    }
