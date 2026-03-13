"""steps/08_export.py — Step 08: Export ranked problems to JSONL.

Terminal step — no LLM call, no registry mutation.

Reads:  step_input["ranked_problems"]
Writes: exports/atomic_problems.jsonl   (this IS the canonical output artifact)
Returns: export metadata as data dict
"""
from __future__ import annotations

import json


def run(ctx, step_input: dict, config, prompt_loader):
    domain: str = step_input["domain"]
    ranked: list = step_input.get("ranked_problems", [])

    if not ranked:
        raise ValueError("08_export: ranked_problems is empty — nothing to export")

    # exports/atomic_problems.jsonl is the canonical deliverable of this pipeline
    out = ctx.exports_dir() / "atomic_problems.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for item in ranked:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    data = {
        "exported": len(ranked),
        "domain": domain,
        "output_file": str(out),
        "ingestion": {
            "seeds_dir":    str(config.ingestion_seeds_dir),
            "rules_dir":    str(config.ingestion_rules_dir),
            "taxonomy_dir": str(config.ingestion_taxonomy_dir),
        },
    }

    return {
        "data": data,
        "counts": {"exported": len(ranked)},
    }
