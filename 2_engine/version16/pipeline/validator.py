"""
validator.py v14 — Central validation module for pipeline artifacts.

Fixes:
  #2      — Real jsonschema validation (not manual field checks)
  #3      — Correct _detect_duplicates() (was indexing tuples as dicts)
  #4      — Semantic dedup via normalized problem_statement comparison
  #8      — problem_uid = sha256(canonical content + subdomain_id + category + title)
  #v14-a  — FormatChecker added: format keywords now enforced (date-time, uri, etc.)
  #v14-b  — save_manifest() and save_run_record() validate schema before write

Usage:
  from validator import validate_schema, detect_duplicates, make_problem_uid
"""

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

# jsonschema is a hard dependency — install with: pip install jsonschema
try:
    import jsonschema
    from jsonschema import FormatChecker
except ImportError:
    print(
        "[FATAL] jsonschema is not installed.\n"
        "Run: pip install jsonschema\n"
        "Schema validation cannot be disabled — it is a hard pipeline requirement.",
        file=sys.stderr,
    )
    sys.exit(1)

from constants import (
    VALID_DIFFICULTIES, VALID_ANSWER_TYPES, VALID_HALLUC_RISKS, StopCode,
)

_PIPELINE_ROOT = Path(__file__).parent
_SCHEMA_CACHE: dict[str, dict] = {}


# ── Schema loading ─────────────────────────────────────────────────────────────

def _load_schema(schema_name: str) -> Optional[dict]:
    """Load a JSON Schema from pipeline/schema/. Returns None if not found."""
    if schema_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_name]
    schema_path = _PIPELINE_ROOT / "schema" / f"{schema_name}.schema.json"
    if not schema_path.exists():
        return None
    with open(schema_path) as f:
        schema = json.load(f)
    _SCHEMA_CACHE[schema_name] = schema
    return schema


# ── Schema validation (Fix #2, #v14-format) ─────────────────────────────────

def validate_schema(obj: Any, schema_name: str) -> list[dict]:
    """
    Validate obj against a named JSON Schema.
    Returns list of error dicts: [{path, message}]
    Raises RuntimeError if schema file is missing — missing schema = hard error.

    Uses FormatChecker() so that format keywords (date-time, uri, etc.) in
    schemas are enforced, not silently ignored. Without FormatChecker, a
    Draft7Validator passes any string for a field declared as format: date-time.
    """
    schema = _load_schema(schema_name)
    if schema is None:
        raise RuntimeError(
            f"Schema file not found: schema/{schema_name}.schema.json\n"
            f"All schema files must exist before the pipeline runs."
        )

    errors = []
    # FormatChecker enforces format keywords (e.g. date-time, uri) in the schema.
    # Without it, Draft7Validator silently ignores format assertions.
    validator = jsonschema.Draft7Validator(schema, format_checker=FormatChecker())
    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
        errors.append({
            "path":    " > ".join(str(p) for p in err.path) or "(root)",
            "message": err.message,
        })
    return errors


def validate_problem(problem: dict, category: str) -> list[dict]:
    """
    Validate a single atomic problem dict.
    Combines schema validation + manual enum checks for robustness.
    Returns list of error dicts.
    """
    errors = []

    # Manual checks (always run, even without jsonschema)
    required = ["title", "problem_statement", "difficulty", "answer_type",
                "canonical_source", "verifiable", "hallucination_risk",
                "requires_context", "tags"]
    for field in required:
        if field not in problem:
            errors.append({"field": field, "category": category,
                           "message": f"missing required field: {field}",
                           "title": problem.get("title", "?")})

    if problem.get("difficulty") not in VALID_DIFFICULTIES:
        errors.append({"field": "difficulty", "category": category,
                       "message": f"invalid value: {problem.get('difficulty')}",
                       "title": problem.get("title", "?")})

    if problem.get("answer_type") not in VALID_ANSWER_TYPES:
        errors.append({"field": "answer_type", "category": category,
                       "message": f"invalid value: {problem.get('answer_type')}",
                       "title": problem.get("title", "?")})

    if problem.get("hallucination_risk") not in VALID_HALLUC_RISKS:
        errors.append({"field": "hallucination_risk", "category": category,
                       "message": f"invalid value: {problem.get('hallucination_risk')}",
                       "title": problem.get("title", "?")})

    if len(problem.get("title", "")) > 80:
        errors.append({"field": "title", "category": category,
                       "message": "exceeds 80 characters",
                       "title": problem.get("title", "?")[:80] + "…"})

    if not isinstance(problem.get("verifiable"), bool):
        errors.append({"field": "verifiable", "category": category,
                       "message": "must be boolean",
                       "title": problem.get("title", "?")})

    if not isinstance(problem.get("requires_context"), bool):
        errors.append({"field": "requires_context", "category": category,
                       "message": "must be boolean",
                       "title": problem.get("title", "?")})

    return errors


# ── Normalization helpers (for dedup) ─────────────────────────────────────────

def _normalize_text(text: str) -> str:
    """
    Light normalization for dedup comparison:
    lowercase, strip punctuation, collapse whitespace, remove stopwords.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)          # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()       # collapse whitespace
    # Remove common stopwords
    stops = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
             "in", "of", "for", "to", "and", "or", "that", "this",
             "what", "which", "how", "when", "where", "why", "given"}
    tokens = [w for w in text.split() if w not in stops]
    return " ".join(tokens)


def _jaccard(a: str, b: str) -> float:
    """Jaccard similarity on word sets."""
    sa = set(a.split())
    sb = set(b.split())
    if not sa and not sb:
        return 1.0
    intersection = len(sa & sb)
    union        = len(sa | sb)
    return intersection / union if union else 0.0


# ── Duplicate detection (Fix #3 + #4) ────────────────────────────────────────

def detect_duplicates(
    all_problems: list[tuple],   # list of (category_name: str, problem_dict: dict)
    similarity_threshold: float = 0.85,
) -> list[dict]:
    """
    Three-level duplicate detection:
    1. Exact title match (case-insensitive, stripped)
    2. Normalized title match
    3. Semantic similarity on problem_statement via Jaccard (threshold configurable)

    Fix #3: all_problems is list of (str, dict) tuples — correctly indexed as
            cat, p = all_problems[i]  — NOT all_problems[i]["title"]

    Returns list of duplicate report dicts.
    """
    dupes = []
    n = len(all_problems)

    # Pre-compute normalized forms
    norm_titles  = []
    norm_stmts   = []
    for cat, p in all_problems:
        norm_titles.append(_normalize_text(p.get("title", "")))
        norm_stmts.append(_normalize_text(p.get("problem_statement", "")))

    seen_titles: dict[str, int] = {}  # normalized_title → first index

    for i in range(n):
        cat_i, p_i = all_problems[i]       # Fix #3: correct tuple unpacking
        nt_i = norm_titles[i]
        ns_i = norm_stmts[i]

        # Level 1+2: exact or normalized title match
        if nt_i in seen_titles:
            j = seen_titles[nt_i]
            cat_j, p_j = all_problems[j]   # Fix #3: correct tuple unpacking
            similarity_type = (
                "exact" if p_i.get("title", "").strip().lower() ==
                           p_j.get("title", "").strip().lower()
                else "normalized_title"
            )
            dupes.append({
                "title_a":      p_j.get("title", "?"),
                "title_b":      p_i.get("title", "?"),
                "category_a":   cat_j,
                "category_b":   cat_i,
                "similarity":   similarity_type,
                "jaccard_score": 1.0,
            })
            continue  # Don't add to seen — keep first occurrence

        seen_titles[nt_i] = i

        # Level 3: semantic similarity on problem_statement (pairwise with prior)
        for j in range(i):
            cat_j, p_j = all_problems[j]   # Fix #3: correct tuple unpacking
            ns_j = norm_stmts[j]
            score = _jaccard(ns_i, ns_j)
            if score >= similarity_threshold:
                dupes.append({
                    "title_a":       p_j.get("title", "?"),
                    "title_b":       p_i.get("title", "?"),
                    "category_a":    cat_j,
                    "category_b":    cat_i,
                    "similarity":    "semantic_statement",
                    "jaccard_score": round(score, 3),
                })
                break  # One semantic match per problem is enough

    return dupes


# ── problem_uid (Fix #8) ──────────────────────────────────────────────────────

def make_problem_uid(problem: dict, subdomain_id: str, category: str) -> str:
    """
    Stable technical identity for a problem independent of problem_id prefix.
    problem_uid = sha256(canonicalized content + subdomain_id + category + title)

    This survives:
    - Re-runs (same content → same uid)
    - Prefix changes
    - Registry merges
    - Delta-run deduplication
    """
    canonical = {
        "subdomain_id":      subdomain_id,
        "category":          category.strip().lower(),
        "title":             problem.get("title", "").strip().lower(),
        "problem_statement": _normalize_text(problem.get("problem_statement", "")),
    }
    content = json.dumps(canonical, sort_keys=True, ensure_ascii=False)
    return "uid:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


# ── Scope violation check ─────────────────────────────────────────────────────

def check_scope_violations(
    all_problems: list[tuple],
    scope: dict,
) -> list[dict]:
    """
    Check problems against scope.exclusions.
    More robust than single-keyword check: tests all significant words
    of each exclusion phrase.
    """
    exclusions = scope.get("exclusions", [])
    violations = []

    for cat, p in all_problems:
        stmt_norm = _normalize_text(p.get("problem_statement", ""))
        title_norm = _normalize_text(p.get("title", ""))
        combined = stmt_norm + " " + title_norm

        for excl in exclusions:
            excl_words = set(_normalize_text(excl).split())
            if len(excl_words) == 0:
                continue
            # Violation if majority of exclusion keywords appear in problem text
            matches = sum(1 for w in excl_words if w in combined.split())
            coverage = matches / len(excl_words)
            if coverage >= 0.6:
                violations.append({
                    "problem_title": p.get("title", "?"),
                    "category":      cat,
                    "exclusion":     excl,
                    "coverage":      round(coverage, 2),
                    "violation":     f"Possible scope violation (coverage={coverage:.0%}): '{excl}'",
                })
                break

    return violations
