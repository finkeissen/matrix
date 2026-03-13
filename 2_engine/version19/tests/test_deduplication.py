"""
tests/test_deduplication.py — Tests for all three dedup levels.
"""

import hashlib
import pytest
from pipeline.dedup import (
    run_exact_dedup,
    run_normalized_dedup,
    run_full_dedup,
    normalize_text,
    exact_key,
)


def make_problem(statement: str, pid: str = "ap_test01") -> dict:
    return {
        "problem_id": pid,
        "problem_statement": statement,
        "category": "test",
        "difficulty": "easy",
    }


def sha256(text: str) -> str:
    return hashlib.sha256(text.strip().encode()).hexdigest()


# ── Level A: Exact match ────────────────────────────────────────────────────

def test_exact_dedup_rejects_known_hash():
    p = make_problem("What is Newton's second law?")
    known = {sha256(exact_key(p))}
    accepted, rejected = run_exact_dedup([p], known)
    assert len(accepted) == 0
    assert len(rejected) == 1
    assert rejected[0]["_dedup_reason"] == "exact_match"


def test_exact_dedup_accepts_new_problem():
    p = make_problem("What is Ohm's law?")
    known = {sha256("Some other problem")}
    accepted, rejected = run_exact_dedup([p], known)
    assert len(accepted) == 1
    assert len(rejected) == 0


def test_exact_dedup_catches_within_batch_duplicate():
    p1 = make_problem("What is the speed of light?", "ap_001")
    p2 = make_problem("What is the speed of light?", "ap_002")
    accepted, rejected = run_exact_dedup([p1, p2], set())
    assert len(accepted) == 1
    assert len(rejected) == 1


# ── Level B: Normalized match ────────────────────────────────────────────────

def test_normalize_text_lowercases():
    assert normalize_text("What Is ENTROPY?") == "what is entropy"


def test_normalize_text_removes_punctuation():
    assert normalize_text("Hello, World!") == "hello world"


def test_normalize_text_collapses_whitespace():
    assert normalize_text("too  many   spaces") == "too many spaces"


def test_normalized_dedup_catches_case_variant():
    p = make_problem("what is entropy?", "ap_001")
    known_norm = {"what is entropy"}  # already known in normalized form
    accepted, rejected = run_normalized_dedup([p], known_norm)
    assert len(accepted) == 0
    assert rejected[0]["_dedup_reason"] == "normalized_match"


def test_normalized_dedup_accepts_genuinely_new():
    p = make_problem("Explain the second law of thermodynamics.")
    known_norm = {"what is entropy"}
    accepted, rejected = run_normalized_dedup([p], known_norm)
    assert len(accepted) == 1


# ── Combined ─────────────────────────────────────────────────────────────────

def test_full_dedup_pipeline():
    problems = [
        make_problem("Newton's second law", "ap_001"),
        make_problem("Newton's second law", "ap_002"),  # exact dup
        make_problem("newtons second law", "ap_003"),   # normalized dup
        make_problem("Conservation of energy", "ap_004"),  # new
    ]
    result = run_full_dedup(problems, known_hashes=set(), known_normalized=set())
    counts = result["counts"]
    assert counts["input"] == 4
    assert counts["accepted"] == 2  # ap_001 and ap_004
    assert counts["rejected_exact"] == 1   # ap_002
    assert counts["rejected_normalized"] == 1  # ap_003
