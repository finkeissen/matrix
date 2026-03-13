#!/usr/bin/env python3
from __future__ import annotations

import argparse, os, glob

from lib.config import load_config, resolve_repo_root
from lib.io import iter_jsonl, append_jsonl

def main():
    ap = argparse.ArgumentParser(description="Materialize state by replaying patch events from runs.")
    ap.add_argument("--config", required=True, help="Path to config.toml")
    ap.add_argument("--runs_glob", default="2.runs/**/patches.jsonl", help="Glob for patches.jsonl")
    ap.add_argument("--out", default=None, help="State output dir (default from config)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    repo_root = resolve_repo_root(cfg, args.config)

    runs_glob = args.runs_glob
    if not os.path.isabs(runs_glob):
        runs_glob = os.path.join(repo_root, runs_glob)

    state_cfg = cfg.get("state", {})
    out_dir = args.out or state_cfg.get("path", "4.state/current")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(repo_root, out_dir)

    entities = {}
    assertions = {}
    evidence = {}
    events_out = []

    for patches_path in sorted(glob.glob(runs_glob, recursive=True)):
        for ev in iter_jsonl(patches_path):
            events_out.append(ev)
            for op in ev.get("ops", []):
                typ = op.get("op")
                rec = op.get("record")
                if typ == "upsert_entity" and isinstance(rec, dict):
                    entities[rec["entity_id"]] = rec
                elif typ in ("upsert_assertion", "upsert_relation") and isinstance(rec, dict):
                    assertions[rec["assertion_id"]] = rec
                elif typ == "attach_evidence" and isinstance(rec, dict) and "evidence_id" in rec:
                    evidence[rec["evidence_id"]] = rec
                elif typ == "deprecate":
                    target = op.get("target_ref")
                    if target and target in entities:
                        ent = dict(entities[target])
                        ent["status"] = "deprecated"
                        ent.setdefault("deprecation_reason", op.get("reason",""))
                        entities[target] = ent

    os.makedirs(out_dir, exist_ok=True)
    ent_path = os.path.join(out_dir, state_cfg.get("entities_file","entities.jsonl"))
    asrt_path = os.path.join(out_dir, state_cfg.get("assertions_file","assertions.jsonl"))
    ev_path = os.path.join(out_dir, state_cfg.get("evidence_file","evidence.jsonl"))
    events_path = os.path.join(out_dir, state_cfg.get("events_file","events.jsonl"))

    for p in (ent_path, asrt_path, ev_path, events_path):
        if os.path.exists(p):
            os.remove(p)

    append_jsonl(ent_path, list(entities.values()))
    append_jsonl(asrt_path, list(assertions.values()))
    append_jsonl(ev_path, list(evidence.values()))
    append_jsonl(events_path, events_out)

    print(f"Materialized state to {out_dir}")
    print(f"- entities: {len(entities)}")
    print(f"- assertions: {len(assertions)}")
    print(f"- evidence: {len(evidence)}")
    print(f"- events: {len(events_out)}")

if __name__ == "__main__":
    main()
