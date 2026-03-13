from __future__ import annotations

import json
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


def run(ctx, domain, config, prompt_loader):
    """
    Step 02 — expand seeds using ingestion knowledge base.
    """

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

    out = ctx.intermediate_dir() / "02_seed_expansion.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "data": data,
        "output_path": str(out),
        "counts": {"seeds": len(final_seeds)},
    }
