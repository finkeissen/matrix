"""
steps/06_deduplication.py — Step 06: Three-level deduplication.

Deterministic step — no LLM call, no prompt file.

Reads:  intermediate/05_validation.json  (validated problems)
Reads:  data/registry/problems/index.json (known problem hashes)
Writes: intermediate/06_deduplication.json
Writes: rejected/duplicates.json
"""

import json
from pathlib import Path

from ..dedup import run_full_dedup
from ..logging_setup import get_logger

logger = get_logger(__name__)


def run(ctx, domain: str, config, prompt_loader) -> dict:
    step_name = "06_deduplication"
    int_dir = ctx.intermediate_dir()
    rej_dir = ctx.rejected_dir()

    # Load validated problems from previous step
    validated_path = int_dir / "05_validation.json"
    if not validated_path.exists():
        raise FileNotFoundError(f"Required input not found: {validated_path}")

    validated = json.loads(validated_path.read_text())
    problems = validated if isinstance(validated, list) else validated.get("problems", [])

    # Load known hashes from global registry
    known_hashes, known_normalized = _load_known(config)

    # Run dedup
    import os
    semantic_enabled = os.getenv("SEMANTIC_DEDUP_ENABLED", "false").lower() == "true"
    result = run_full_dedup(problems, known_hashes, known_normalized, semantic_enabled)

    # Write accepted
    out_path = int_dir / f"{step_name}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write rejected to rejected/
    rej_path = rej_dir / "duplicates.json"
    duplicates = result["rejected_exact"] + result["rejected_normalized"] + result["rejected_semantic"]
    rej_path.write_text(json.dumps(duplicates, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "data": result["accepted"],
        "output_path": str(out_path),
        "counts": result["counts"],
    }


def _load_known(config) -> tuple[set, set]:
    """Load known problem hashes and normalized forms from registry."""
    import hashlib, unicodedata, re

    index_path = config.registry_dir / "problems" / "index.json"
    if not index_path.exists():
        return set(), set()

    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    known_hashes = set(index.get("hashes", []))
    known_normalized = set(index.get("normalized", []))
    return known_hashes, known_normalized
