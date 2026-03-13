"""steps/03_categories.py — Step 03: Derive categories from seed set."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pipeline.ingestion_loader import IngestionLoader


def run(ctx, step_input: dict, config, prompt_loader):
    domain: str = step_input["domain"]

    loader = IngestionLoader(Path(__file__).resolve().parent.parent.parent)
    curated_categories = loader.load_taxonomy(domain)

    if curated_categories:
        categories = [c.strip() for c in curated_categories if isinstance(c, str) and c.strip()]
        category_source = "ingestion_taxonomy"
    else:
        categories = []
        category_source = "fallback"

    if not categories:
        categories = [
            f"{domain}_foundations",
            f"{domain}_applications",
            f"{domain}_analysis",
        ]
        category_source = "fallback"

    data = {
        "domain": domain,
        "categories": categories,
        "category_source": category_source,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    return {
        "data": data,
        "counts": {"categories": len(categories)},
    }
