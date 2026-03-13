"""step_chain.py — Explicit step-to-step input assembly.

Each step receives exactly its declared input — nothing more, nothing less.
The chain reads from the upstream step's output.json and assembles the
declared input payload for the next step.

This replaces the generic {"domain": "...", "step": "..."} placeholder
with a fachlich correct input contract per step.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .run_context import RunContext


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_step_input(ctx: RunContext, step_name: str, domain: str) -> dict[str, Any]:
    """Return the declared input payload for *step_name*.

    Each assembler reads only from upstream step-local output.json files
    (or falls back to intermediate/ for backward compatibility).
    No assembler may access the output of a downstream step.
    """
    assemblers = {
        "01_scope":             _input_01_scope,
        "02_seed_expansion":    _input_02_seed_expansion,
        "03_categories":        _input_03_categories,
        "04_problem_generation": _input_04_problem_generation,
        "05_validation":        _input_05_validation,
        "06_deduplication":     _input_06_deduplication,
        "07_ranking":           _input_07_ranking,
        "08_export":            _input_08_export,
    }
    fn = assemblers.get(step_name)
    if fn is None:
        raise KeyError(f"No input assembler for step: {step_name!r}")
    return fn(ctx, domain)


# ---------------------------------------------------------------------------
# Helper: read upstream step output
# ---------------------------------------------------------------------------

def _read_step_output(ctx: RunContext, step_name: str) -> Any:
    """Read the step-local output.json for a completed upstream step.

    Primary:  runs/<run-id>/steps/<step>/run/output.json   (v29+)
    Fallback: runs/<run-id>/intermediate/<step>.json        (legacy v28 and earlier)

    The fallback exists only for backward-compatible resume of old run directories.
    New runs always write to the primary path first.
    """
    step_out = ctx.step_output_path(step_name)
    if step_out.exists():
        return json.loads(step_out.read_text(encoding="utf-8"))

    # Legacy fallback — only for runs produced before v29
    legacy = ctx.intermediate_dir() / f"{step_name}.json"
    if legacy.exists():
        import warnings
        warnings.warn(
            f"step_chain: reading from legacy path {legacy}. "
            "Re-run from scratch to use the canonical step-local layout.",
            DeprecationWarning,
            stacklevel=3,
        )
        return json.loads(legacy.read_text(encoding="utf-8"))

    raise FileNotFoundError(
        f"Upstream output not found for step '{step_name}'. "
        f"Checked primary: {step_out} and legacy: {legacy}"
    )


# ---------------------------------------------------------------------------
# Input assemblers — one per step
# Invariant: each assembler reads ONLY from steps that precede it.
# ---------------------------------------------------------------------------

def _input_01_scope(ctx: RunContext, domain: str) -> dict:
    """01_scope input: domain string only."""
    return {"domain": domain}


def _input_02_seed_expansion(ctx: RunContext, domain: str) -> dict:
    """02_seed_expansion input: domain + scope from 01_scope."""
    scope = _read_step_output(ctx, "01_scope")
    return {
        "domain": domain,
        "scope": scope,
    }


def _input_03_categories(ctx: RunContext, domain: str) -> dict:
    """03_categories input: domain + seed_set from 02_seed_expansion."""
    seed_expansion = _read_step_output(ctx, "02_seed_expansion")
    return {
        "domain": domain,
        "seeds": seed_expansion.get("seeds", []),
        "seed_sources": seed_expansion.get("seed_sources", {}),
    }


def _input_04_problem_generation(ctx: RunContext, domain: str) -> dict:
    """04_problem_generation input: domain + categories from 03_categories."""
    cats = _read_step_output(ctx, "03_categories")
    return {
        "domain": domain,
        "categories": cats.get("categories", []),
        "category_source": cats.get("category_source", "unknown"),
    }


def _input_05_validation(ctx: RunContext, domain: str) -> dict:
    """05_validation input: generated_problems from 04_problem_generation."""
    generated = _read_step_output(ctx, "04_problem_generation")
    # 04 may return a list directly or wrapped in {"problems": [...]}
    if isinstance(generated, list):
        problems = generated
    else:
        problems = generated.get("problems", generated.get("data", []))
    return {
        "domain": domain,
        "generated_problems": problems,
        "problem_count": len(problems),
    }


def _input_06_deduplication(ctx: RunContext, domain: str) -> dict:
    """06_deduplication input: validated_problems from 05_validation."""
    validated = _read_step_output(ctx, "05_validation")
    # 05 returns list of accepted problems or {"problems": [...]}
    if isinstance(validated, list):
        problems = validated
    else:
        problems = validated.get("problems", validated.get("data", []))
    return {
        "domain": domain,
        "validated_problems": problems,
        "problem_count": len(problems),
    }


def _input_07_ranking(ctx: RunContext, domain: str) -> dict:
    """07_ranking input: deduplicated accepted problems from 06_deduplication."""
    deduped = _read_step_output(ctx, "06_deduplication")
    if isinstance(deduped, list):
        accepted = deduped
    else:
        accepted = deduped.get("accepted", deduped.get("data", []))
    return {
        "domain": domain,
        "deduplicated_problems": accepted,
        "problem_count": len(accepted),
    }


def _input_08_export(ctx: RunContext, domain: str) -> dict:
    """08_export input: ranked problems from 07_ranking."""
    ranked = _read_step_output(ctx, "07_ranking")
    if isinstance(ranked, list):
        problems = ranked
    else:
        problems = ranked.get("data", ranked.get("problems", []))
    return {
        "domain": domain,
        "ranked_problems": problems,
        "problem_count": len(problems),
    }
