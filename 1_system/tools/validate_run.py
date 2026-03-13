#!/usr/bin/env python3
from __future__ import annotations
import argparse, os
from lib.io import iter_jsonl, read_json

REQUIRED_EVENT_FIELDS = ["event_id","created_at","module_id","module_version","params_hash","inputs_fingerprint","ops","provenance"]

def main():
    ap = argparse.ArgumentParser(description="Validate a run folder (json/jsonl structure).")
    ap.add_argument("--run", required=True, help="Run folder path")
    ap.add_argument("--patches", default="patches.jsonl", help="Patches filename within run")
    ap.add_argument("--report", default="report.json", help="Report filename within run")
    args = ap.parse_args()

    patches_path = os.path.join(args.run, args.patches)
    report_path = os.path.join(args.run, args.report)

    if not os.path.exists(patches_path):
        raise SystemExit(f"Missing {patches_path}")
    if not os.path.exists(report_path):
        raise SystemExit(f"Missing {report_path}")

    _ = read_json(report_path)

    errors = []
    count = 0
    for ev in iter_jsonl(patches_path):
        count += 1
        for f in REQUIRED_EVENT_FIELDS:
            if f not in ev:
                errors.append(f"Event missing field {f}: {ev.get('event_id','(no id)')}")
        ops = ev.get("ops", [])
        if not isinstance(ops, list) or not ops:
            errors.append(f"Event ops must be non-empty list: {ev.get('event_id')}")
        for op in ops:
            if "op" not in op:
                errors.append(f"Op missing 'op' field in event {ev.get('event_id')}")
            if op.get("op") in ("upsert_entity","upsert_assertion","upsert_relation","attach_evidence"):
                rec = op.get("record")
                if not isinstance(rec, dict):
                    errors.append(f"Op record must be object in event {ev.get('event_id')}")
    if errors:
        print("VALIDATION FAILED")
        for e in errors[:200]:
            print("-", e)
        raise SystemExit(1)
    print(f"OK: {count} patch events; report JSON valid.")

if __name__ == "__main__":
    main()
