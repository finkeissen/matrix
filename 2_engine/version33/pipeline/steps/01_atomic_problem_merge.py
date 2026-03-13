#!/usr/bin/env python3
"""Merge one or more AP JSONL files into a shared ap_*.jsonl store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ap_store import APStore, canonical_ap_id, normalize_ws, slugify


def load_records(paths: Sequence[Path], domain: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            subdomain = normalize_ws(str(record.get("subdomain", "")))
            problem_group = normalize_ws(str(record.get("problem_group", "")))
            atomic_problem = normalize_ws(str(record.get("atomic_problem", "")))
            if not (subdomain and problem_group and atomic_problem):
                continue
            record.setdefault("domain", slugify(domain))
            record.setdefault(
                "ap_id",
                canonical_ap_id(domain=domain, subdomain=subdomain, problem_group=problem_group, atomic_problem=atomic_problem),
            )
            record.setdefault("status", "candidate")
            record.setdefault("version", 1)
            record.setdefault("parent_ap_id", None)
            record.setdefault("children_ap_ids", [])
            out.append(record)
    return out


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge AP records into a shared ap_*.jsonl store")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--input", dest="inputs", action="append", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--records-per-file", type=int, default=1000)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    inputs = [Path(p).resolve() for p in args.inputs]
    store = APStore(Path(args.output_dir).resolve(), records_per_file=max(1, args.records_per_file))
    stats = store.upsert_many(load_records(inputs, args.domain))
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
