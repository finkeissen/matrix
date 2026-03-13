"""steps/02_seed_expansion.py — Step 02: Expand seeds from scope + domain."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pipeline.ingestion_loader import IngestionLoader


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item.strip())
    return result


def run(ctx, step_input: dict, config, prompt_loader):
    domain: str = step_input["domain"]

    generated_seeds = [
        domain,
        f"{domain} workflows",
        f"{domain} edge cases",
    ]

    loader = IngestionLoader(Path(__file__).resolve().parent.parent.parent)
    curated_seeds = loader.load_domain_seeds(domain)
    final_seeds = _dedupe_keep_order(generated_seeds + curated_seeds)

    data = {
        "domain": domain,
        "seeds": final_seeds,
        "seed_sources": {
            "generated": len(generated_seeds),
            "curated": len(curated_seeds),
            "final": len(final_seeds),
        },
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    return {
        "data": data,
        "counts": {"seeds": len(final_seeds)},
    }
