from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pipeline.ingestion_loader import IngestionLoader


def run(ctx, domain, config, prompt_loader):
    loader = IngestionLoader(Path(__file__).resolve().parent.parent.parent)
    curated_categories = loader.load_taxonomy(domain)

    if curated_categories:
        categories = [
            c.strip()
            for c in curated_categories
            if isinstance(c, str) and c.strip()
        ]
        category_source = "ingestion_taxonomy"
    else:
        categories = [
            f"{domain}_foundations",
            f"{domain}_applications",
            f"{domain}_analysis",
        ]
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

    out = ctx.intermediate_dir() / "03_categories.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "data": data,
        "output_path": str(out),
        "counts": {"categories": len(categories)},
    }
