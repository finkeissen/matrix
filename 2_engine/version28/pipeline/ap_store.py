from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterable


_AP_FILE_RE = re.compile(r"^ap_(\d{6})\.jsonl$")


def normalize_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slugify(value: str) -> str:
    value = normalize_ws(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding=encoding) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def canonical_ap_id(*, domain: str, subdomain: str, problem_group: str, atomic_problem: str) -> str:
    base = " || ".join(
        [
            slugify(domain),
            normalize_ws(subdomain).casefold(),
            normalize_ws(problem_group).casefold(),
            normalize_ws(atomic_problem).casefold(),
        ]
    )
    return "ap_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


@dataclass
class APStore:
    output_dir: Path
    records_per_file: int = 1000
    _records_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._load_existing()

    def _load_existing(self) -> None:
        for path in sorted(self.output_dir.glob("ap_*.jsonl")):
            if not _AP_FILE_RE.match(path.name):
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                ap_id = record.get("ap_id")
                if isinstance(ap_id, str) and ap_id:
                    self._records_by_id[ap_id] = record

    def upsert_many(self, records: Iterable[dict[str, Any]]) -> dict[str, int]:
        inserted = 0
        updated = 0
        unchanged = 0
        for record in records:
            ap_id = record["ap_id"]
            old = self._records_by_id.get(ap_id)
            if old is None:
                self._records_by_id[ap_id] = record
                inserted += 1
            elif self._equivalent(old, record):
                unchanged += 1
            else:
                merged = dict(old)
                merged.update(record)
                merged["created_at"] = old.get("created_at", record.get("created_at"))
                merged["version"] = int(old.get("version", 1)) + 1
                self._records_by_id[ap_id] = merged
                updated += 1
        self._rewrite_all()
        return {"inserted": inserted, "updated": updated, "unchanged": unchanged, "total": len(self._records_by_id)}

    @staticmethod
    def _equivalent(old: dict[str, Any], new: dict[str, Any]) -> bool:
        ignore = {"created_at", "updated_at"}
        old_cmp = {k: v for k, v in old.items() if k not in ignore}
        new_cmp = {k: v for k, v in new.items() if k not in ignore}
        return old_cmp == new_cmp

    def _rewrite_all(self) -> None:
        ordered = [self._records_by_id[k] for k in sorted(self._records_by_id)]
        existing = sorted(self.output_dir.glob("ap_*.jsonl"))
        for path in existing:
            if _AP_FILE_RE.match(path.name):
                path.unlink()
        if not ordered:
            return
        file_count = math.ceil(len(ordered) / self.records_per_file)
        for idx in range(file_count):
            chunk = ordered[idx * self.records_per_file : (idx + 1) * self.records_per_file]
            path = self.output_dir / f"ap_{idx+1:06d}.jsonl"
            atomic_write_text(path, "\n".join(json.dumps(r, ensure_ascii=False) for r in chunk) + "\n")
