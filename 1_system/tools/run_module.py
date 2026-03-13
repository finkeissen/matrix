#!/usr/bin/env python3
from __future__ import annotations

import argparse, os, datetime
from typing import Any, Dict

from lib.config import load_config, resolve_repo_root
from lib.io import read_json, write_json, append_jsonl, sha256_json
from providers.factory import make_provider

from modules.problems.problem_seed import update_problem_seed
from modules.problems.problem_atomize import update_problem_atomize

MODULES = {
    "problems/update_problem_seed": update_problem_seed,
    "problems/update_problem_atomize": update_problem_atomize,
}

def utc_now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def main():
    ap = argparse.ArgumentParser(description="Run a single update module into a run folder.")
    ap.add_argument("--config", required=True, help="Path to config.toml")
    ap.add_argument("--run", required=True, help="Path to run folder (relative to repo root or absolute)")
    ap.add_argument("--module", required=True, help="Module id, e.g. problems/update_problem_seed")
    ap.add_argument("--inputs", default="inputs.json", help="Inputs filename within run")
    ap.add_argument("--params", default="params.json", help="Params filename within run")
    ap.add_argument("--state", default=None, help="Optional state directory path (default from config)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    repo_root = resolve_repo_root(cfg, args.config)

    run_dir = args.run
    if not os.path.isabs(run_dir):
        run_dir = os.path.abspath(os.path.join(repo_root, run_dir))

    if args.module not in MODULES:
        raise SystemExit(f"Unknown module: {args.module}. Known: {sorted(MODULES)}")

    io_cfg = cfg.get("io", {})
    patches_name = io_cfg.get("patches_file", "patches.jsonl")
    report_name = io_cfg.get("report_file", "report.json")

    inputs_path = os.path.join(run_dir, args.inputs)
    params_path = os.path.join(run_dir, args.params)

    if not os.path.exists(inputs_path):
        raise SystemExit(f"Missing inputs file: {inputs_path}")
    if not os.path.exists(params_path):
        write_json(params_path, {})

    inputs = read_json(inputs_path)
    params = read_json(params_path)

    # Optional state loading will come later; keep contract stable now.
    state = {"entities": [], "assertions": [], "evidence": []}

    provider = make_provider(cfg)

    module_fn = MODULES[args.module]
    module_version = getattr(module_fn, "MODULE_VERSION", "v0")

    params_hash = sha256_json(params)
    inputs_fingerprint = sha256_json(inputs)

    patch_events, report = module_fn(state=state, inputs=inputs, params=params, cfg=cfg, provider=provider)

    for ev in patch_events:
        ev.setdefault("created_at", utc_now_iso())
        ev.setdefault("module_id", args.module)
        ev.setdefault("module_version", module_version)
        ev.setdefault("params_hash", params_hash)
        ev.setdefault("inputs_fingerprint", inputs_fingerprint)
        ev.setdefault("provenance", {"provider":"unknown"})

    patches_path = os.path.join(run_dir, patches_name)
    append_jsonl(patches_path, patch_events)

    report.setdefault("module_id", args.module)
    report.setdefault("module_version", module_version)
    report.setdefault("params_hash", params_hash)
    report.setdefault("inputs_fingerprint", inputs_fingerprint)
    report.setdefault("created_at", utc_now_iso())

    report_path = os.path.join(run_dir, report_name)
    write_json(report_path, report)

    print(f"Wrote {len(patch_events)} patch events to {patches_path}")
    print(f"Wrote report to {report_path}")

if __name__ == "__main__":
    main()
