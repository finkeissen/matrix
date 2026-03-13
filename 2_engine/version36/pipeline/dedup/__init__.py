"""
dedup/ — Three-level deduplication for atomic problems.

Level A — Exact match:      identical problem_statement strings
Level B — Normalized match: lowercase, punctuation-stripped, whitespace-normalized
Level C — Semantic match:   embedding cosine similarity (threshold configurable)

All three levels run in sequence. A problem is rejected at the first level
that flags it. The rejected/ directory records why each problem was excluded.

Design decision: Semantic dedup (Level C) is implemented as a stub in v18.
It requires an embedding model endpoint and is activated via SEMANTIC_DEDUP_ENABLED=true.
"""

import hashlib
import re
import unicodedata
from typing import Optional

from ..logging_setup import get_logger

logger = get_logger(__name__)


# ── Level A: Exact match ────────────────────────────────────────────────────

def exact_key(problem: dict) -> str:
    return problem.get("problem_statement", "").strip()


def run_exact_dedup(problems: list[dict], known_hashes: set[str]) -> tuple[list[dict], list[dict]]:
    """
    Returns (accepted, rejected).
    known_hashes: SHA256 hashes of all previously committed problems.
    """
    accepted, rejected = [], []
    seen = set()
    for p in problems:
        key = exact_key(p)
        h = hashlib.sha256(key.encode("utf-8")).hexdigest()
        if h in known_hashes or h in seen:
            p["_dedup_reason"] = "exact_match"
            rejected.append(p)
        else:
            seen.add(h)
            accepted.append(p)
    return accepted, rejected


# ── Level B: Normalized match ────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """
    Normalize for comparison:
    - Unicode NFKC normalization
    - Lowercase
    - Remove punctuation
    - Collapse whitespace
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def run_normalized_dedup(
    problems: list[dict], known_normalized: set[str]
) -> tuple[list[dict], list[dict]]:
    """
    Returns (accepted, rejected).
    known_normalized: normalized forms of all previously committed problems.
    """
    accepted, rejected = [], []
    seen = set()
    for p in problems:
        key = normalize_text(exact_key(p))
        if key in known_normalized or key in seen:
            p["_dedup_reason"] = "normalized_match"
            rejected.append(p)
        else:
            seen.add(key)
            accepted.append(p)
    return accepted, rejected


# ── Level C: Semantic match (stub) ─────────────────────────────────────────

def run_semantic_dedup(
    problems: list[dict],
    threshold: float = 0.92,
    enabled: bool = False,
) -> tuple[list[dict], list[dict]]:
    """
    Semantic dedup via embedding similarity.
    Requires SEMANTIC_DEDUP_ENABLED=true and an embedding endpoint.

    In v18, this is a documented stub. Activate in v19 with:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode([exact_key(p) for p in problems])
        # compare cosine similarity against threshold
    """
    if not enabled:
        logger.info("dedup.semantic_skipped", reason="SEMANTIC_DEDUP_ENABLED=false")
        return problems, []

    # Stub: no semantic dedup in v18
    logger.warning("dedup.semantic_stub", message="Semantic dedup stub — returning all as accepted")
    return problems, []


# ── Combined pipeline ────────────────────────────────────────────────────────

def run_full_dedup(
    problems: list[dict],
    known_hashes: set[str],
    known_normalized: set[str],
    semantic_enabled: bool = False,
    semantic_threshold: float = 0.92,
) -> dict:
    """
    Run all three dedup levels. Returns:
    {
        "accepted": [...],
        "rejected_exact": [...],
        "rejected_normalized": [...],
        "rejected_semantic": [...],
        "counts": {
            "input": N,
            "accepted": N,
            "rejected_exact": N,
            "rejected_normalized": N,
            "rejected_semantic": N,
        }
    }
    """
    after_exact, rej_exact = run_exact_dedup(problems, known_hashes)
    after_norm, rej_norm = run_normalized_dedup(after_exact, known_normalized)
    after_semantic, rej_semantic = run_semantic_dedup(
        after_norm, threshold=semantic_threshold, enabled=semantic_enabled
    )

    counts = {
        "input": len(problems),
        "accepted": len(after_semantic),
        "rejected_exact": len(rej_exact),
        "rejected_normalized": len(rej_norm),
        "rejected_semantic": len(rej_semantic),
    }
    logger.info("dedup.complete", **counts)

    return {
        "accepted": after_semantic,
        "rejected_exact": rej_exact,
        "rejected_normalized": rej_norm,
        "rejected_semantic": rej_semantic,
        "counts": counts,
    }
