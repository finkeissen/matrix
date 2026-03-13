#!/usr/bin/env python3
"""steps/01_atomic_problem_merge.py — Step 01-pre: Merge AP candidate batches into shared store.

Engine step:  run(ctx, step_input, config, prompt_loader)
CLI wrapper:  python 01_atomic_problem_merge.py --domain X --input Y --output-dir Z

Input contract:
    step_input["domain"]          — domain name
    step_input["input_files"]     — list of JSONL file paths to merge
    step_input["output_dir"]      — target APStore directory
    step_input["records_per_file"] — int, max records per output file (default 1000)

Output (data dict):
    domain, inserted, updated, unchanged, total, output_dir, output_files
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.ap_store import APStore, canonical_ap_id, normalize_ws, slugify


def load_records(paths: Sequence[Path], domain: str) -> list[dict[str, Any]]:
    """Load and normalize AP records from JSONL files.

    Compatible with both sources:
    - 00_atomic_problem_curation output: subdomain + atomic_problem (no problem_group)
    - Manual JSONL: may have subdomain + problem_group + atomic_problem

    When problem_group is absent, it is derived from subdomain so no records are
    silently discarded. This closes the 00→01 data contract gap.
    """
    out: list[dict[str, Any]] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            subdomain = normalize_ws(str(record.get("subdomain", "")))
            atomic_problem = normalize_ws(str(record.get("atomic_problem", "")))

            # Only skip records that are fundamentally incomplete
            if not subdomain or not atomic_problem:
                continue

            # Derive problem_group from subdomain when not explicitly provided
            problem_group = normalize_ws(str(record.get("problem_group", ""))) or subdomain

            record.setdefault("domain", slugify(domain))
            record.setdefault("problem_group", problem_group)
            record.setdefault(
                "ap_id",
                canonical_ap_id(
                    domain=domain, subdomain=subdomain,
                    problem_group=problem_group, atomic_problem=atomic_problem,
                ),
            )
            record.setdefault("status", "candidate")
            record.setdefault("version", 1)
            record.setdefault("parent_ap_id", None)
            record.setdefault("children_ap_ids", [])
            out.append(record)
    return out


# ── Engine step ───────────────────────────────────────────────────────────────

def run(ctx, step_input: dict, config, prompt_loader) -> dict:
    """Engine entry point — contract-driven, no CLI args needed.

    Reads from step_input:
        domain, input_files, output_dir, records_per_file
    Returns:
        {"data": {...summary...}, "counts": {...}}
    """
    domain: str = step_input["domain"]

    # input_files may come from 00_atomic_problem_curation output_files
    raw_inputs = step_input.get("input_files", [])
    if not raw_inputs:
        raise ValueError("01_atomic_problem_merge: input_files is empty — nothing to merge")

    input_paths = [Path(p) for p in raw_inputs]
    missing = [str(p) for p in input_paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"01_atomic_problem_merge: input files not found: {missing}")

    output_dir = Path(
        step_input.get("output_dir")
        or str(ctx.run_dir / "ap_store" / slugify(domain))
    )
    records_per_file = int(step_input.get("records_per_file", 1000))

    store = APStore(output_dir.resolve(), records_per_file=max(1, records_per_file))
    records = load_records(input_paths, domain)
    stats = store.upsert_many(records)

    output_files = sorted(str(p) for p in output_dir.glob("ap_*.jsonl"))

    data = {
        "domain": domain,
        "inserted": stats["inserted"],
        "updated": stats["updated"],
        "unchanged": stats["unchanged"],
        "total": stats["total"],
        "output_dir": str(output_dir),
        "output_files": output_files,
    }
    return {
        "data": data,
        "counts": {
            "total": stats["total"],
            "inserted": stats["inserted"],
            "updated": stats["updated"],
            "unchanged": stats["unchanged"],
        },
    }


# ── CLI wrapper ───────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge AP records into a shared ap_*.jsonl store")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--input", dest="inputs", action="append", required=True,
                        help="Input JSONL file (repeat for multiple)")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--records-per-file", type=int, default=1000)
    return parser


def main(argv=None) -> int:
    """CLI entry point — thin wrapper around run()."""
    args = _build_parser().parse_args(argv)

    step_input = {
        "domain": args.domain,
        "input_files": [str(Path(p).resolve()) for p in args.inputs],
        "output_dir": args.output_dir,
        "records_per_file": args.records_per_file,
    }

    class _NullCtx:
        run_dir = Path(args.output_dir).parent

    result = run(_NullCtx(), step_input, None, None)
    print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
