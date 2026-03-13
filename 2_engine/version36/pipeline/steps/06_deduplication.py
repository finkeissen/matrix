"""steps/06_deduplication.py — Step 06: Three-level deduplication.

Deterministic step — no LLM call.

Reads:  step_input["validated_problems"]
Writes: rejected/duplicates.json   (diagnostic side-channel, not primary output)
Returns: accepted + rejected counts as data dict
"""
from __future__ import annotations

import json

from ..dedup import run_full_dedup
from ..logging_setup import get_logger

logger = get_logger(__name__)


def run(ctx, step_input: dict, config, prompt_loader) -> dict:
    domain: str = step_input["domain"]
    problems: list = step_input.get("validated_problems", [])

    if not problems:
        raise ValueError("06_deduplication: validated_problems is empty — nothing to deduplicate")

    known_hashes, known_normalized = _load_known(config)

    import os
    semantic_enabled = os.getenv("SEMANTIC_DEDUP_ENABLED", "false").lower() == "true"
    result = run_full_dedup(problems, known_hashes, known_normalized, semantic_enabled)

    # Write duplicates as diagnostic side-channel
    duplicates = result["rejected_exact"] + result["rejected_normalized"] + result["rejected_semantic"]
    rej_path = ctx.rejected_dir() / "duplicates.json"
    rej_path.write_text(json.dumps(duplicates, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "data": result["accepted"],
        "counts": result["counts"],
    }


def _load_known(config) -> tuple[set, set]:
    index_path = config.registry_dir / "problems" / "index.json"
    if not index_path.exists():
        return set(), set()
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)
    return set(index.get("hashes", [])), set(index.get("normalized", []))
