from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _collect_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            s = item.strip()
            if s:
                out.append(s)
    return out


def _collect_seed_like_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            s = item.strip()
            if s:
                out.append(s)
        elif isinstance(item, dict):
            for key in ("seed", "name", "label", "title", "pattern"):
                raw = item.get(key)
                if isinstance(raw, str) and raw.strip():
                    out.append(raw.strip())
                    break
    return out


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
    return out


class IngestionLoader:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.ingestion_dir = project_root / "ingestion"
        self.seeds_dir = self.ingestion_dir / "seeds"
        self.rules_dir = self.ingestion_dir / "rules"
        self.taxonomy_dir = self.ingestion_dir / "taxonomy"
        self.imports_dir = self.ingestion_dir / "imports"

    def domain_seed_path(self, domain: str) -> Path:
        return self.seeds_dir / f"{_slugify(domain)}.json"

    def domain_taxonomy_path(self, domain: str) -> Path:
        return self.taxonomy_dir / f"{_slugify(domain)}.json"

    def load_domain_seeds(self, domain: str) -> list[str]:
        seeds: list[str] = []

        # 1) domain-specific overlay
        domain_payload = _read_json(self.domain_seed_path(domain), {})
        seeds.extend(_collect_strings(domain_payload.get("seeds")))

        # 2) global normalized seed libraries already present in ingestion/seeds/
        for filename in (
            "global_atomic_patterns.v1.json",
            "global_meta_patterns.v1.json",
            "global_structural_patterns.v1.json",
        ):
            payload = _read_json(self.seeds_dir / filename, {})
            for key in ("seeds", "patterns", "items", "entries"):
                seeds.extend(_collect_seed_like_strings(payload.get(key)))

        return _dedupe_keep_order(seeds)

    def load_taxonomy(self, domain: str) -> list[str]:
        categories: list[str] = []

        domain_payload = _read_json(self.domain_taxonomy_path(domain), {})
        categories.extend(_collect_strings(domain_payload.get("categories")))

        if not categories:
            payload = _read_json(self.taxonomy_dir / "global_information_taxonomy.v1.json", {})
            for key in ("categories", "taxonomy", "items"):
                categories.extend(_collect_seed_like_strings(payload.get(key)))

        return _dedupe_keep_order(categories)

    def load_failure_patterns(self) -> list[dict[str, Any]]:
        payload = _read_json(self.rules_dir / "failure_patterns.json", {})
        items = payload.get("patterns", [])
        return items if isinstance(items, list) else []

    def load_case_gates(self) -> list[dict[str, Any]]:
        payload = _read_json(self.rules_dir / "case_gates.json", {})
        items = payload.get("gates", [])
        return items if isinstance(items, list) else []

    def load_rules(self) -> dict[str, Any]:
        return {
            "failure_patterns": self.load_failure_patterns(),
            "case_gates": self.load_case_gates(),
        }
