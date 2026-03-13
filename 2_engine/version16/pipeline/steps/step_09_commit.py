"""
step_09_commit.py — Append to registry (append-only). Final snapshot.
Type: deterministic
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, OUTPUT_DIR
from constants import ContentState, COMMIT_MIN_STATE, ArtifactKey, StopCode
from common import (
    sha256_file, now_iso, artifact_dir, write_json, write_jsonl_line,
    register_artifact, emit_state, create_snapshot,
    load_run_record, save_run_record,
)

STEP = "09_commit"

REGISTRY_PROBLEMS = OUTPUT_DIR / "problems.jsonl"
REGISTRY_RUN_LOG  = OUTPUT_DIR / "run_log.jsonl"


def run(run_id: str, final_path: Path, audit: dict, kb_snapshot_id: str, tel=None) -> dict:
    """
    Returns: {"status": "ok"|"stop", "commit_record": {...}}
    """
    print(f"[{STEP}] run={run_id} problems={audit.get('total_problems', 0)}")
    emit_state(WORK_DIR, run_id, "step.start", STEP, {})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Hard schema gate 1: validate run_record.json before commit ────────────
    from common import load_run_record
    from validator import validate_schema as _vschema
    rec_for_validation = load_run_record(WORK_DIR, run_id)
    rec_errors = _vschema(rec_for_validation, "run_record")
    if rec_errors:
        msg = f"run_record.json failed schema validation: {rec_errors}"
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": StopCode.SCHEMA_VALIDATION_FAILED, "reason": msg})
        print(f"  [STOP] {msg}")
        return {"status": "stop", "stop_code": StopCode.SCHEMA_VALIDATION_FAILED}

    # ── Hard schema gate 2: validate every line of final_problems.jsonl ───────
    schema_failures = []
    with open(final_path, "r", encoding="utf-8") as f_check:
        for lineno, line in enumerate(f_check, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                problem = json.loads(line)
                errs = _vschema(problem, "atomic_problem")
                if errs:
                    schema_failures.append({"line": lineno,
                                            "problem_id": problem.get("problem_id", "?"),
                                            "errors": errs})
            except json.JSONDecodeError as e:
                schema_failures.append({"line": lineno, "error": str(e)})

    if schema_failures:
        msg = f"{len(schema_failures)} problems failed atomic_problem schema validation"
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": StopCode.SCHEMA_VALIDATION_FAILED,
                    "reason": msg, "failures": schema_failures[:5]})
        print(f"  [STOP] {msg}")
        for f in schema_failures[:3]:
            print(f"    line {f.get('line')}: {f.get('errors', f.get('error'))}")
        return {"status": "stop", "stop_code": StopCode.SCHEMA_VALIDATION_FAILED}
    # Use problem_uid (content-addressed) as primary identity, fall back to problem_id
    existing_uids: set[str] = set()
    existing_ids:  set[str] = set()
    if REGISTRY_PROBLEMS.exists():
        with open(REGISTRY_PROBLEMS, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    uid = rec.get("problem_uid")
                    pid = rec.get("problem_id", "")
                    if uid:
                        existing_uids.add(uid)
                    if pid:
                        existing_ids.add(pid)
                except Exception:
                    pass

    # ── Append problems — enforce commit policy (fix #7) ─────────────────────
    # Variant B: commit allowed at VERIFIED (content_state_at_commit field records actual state)
    committed = 0
    skipped   = 0
    rejected_state = 0

    try:
        with open(final_path, "r", encoding="utf-8") as f_in, \
             open(REGISTRY_PROBLEMS, "a", encoding="utf-8") as f_out:
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                try:
                    problem = json.loads(line)
                    uid = problem.get("problem_uid")
                    pid = problem.get("problem_id", "")
                    state_at_commit = problem.get("content_state_at_commit",
                                                  ContentState.CANDIDATE)

                    # Enforce commit policy
                    valid_states = {ContentState.VERIFIED, ContentState.ACCEPTED}
                    if state_at_commit not in valid_states:
                        rejected_state += 1
                        print(f"  [policy] rejected — state={state_at_commit}: {pid}")
                        continue

                    # UID-based dedup (primary)
                    if uid and uid in existing_uids:
                        skipped += 1
                        continue
                    # ID-based dedup (fallback)
                    if pid in existing_ids:
                        skipped += 1
                        print(f"  [warn] duplicate problem_id skipped: {pid}")
                        continue

                    f_out.write(line + "\n")
                    if uid:
                        existing_uids.add(uid)
                    existing_ids.add(pid)
                    committed += 1
                except json.JSONDecodeError:
                    print(f"  [warn] skipping malformed line")
    except IOError as e:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": StopCode.DETERMINISTIC_STEP_ERROR, "reason": str(e)})
        return {"status": "stop", "stop_code": StopCode.DETERMINISTIC_STEP_ERROR}

    if committed == 0 and skipped > 0:
        status = "duplicate_skip"
    elif committed == 0 and rejected_state > 0:
        status = "policy_rejected"
    else:
        status = "done"

    # ── Commit record ──────────────────────────────────────────────────────────
    snap_id     = create_snapshot(WORK_DIR, run_id, "post_commit")
    committed_at = now_iso()
    commit_id   = f"COMMIT-{committed_at[:10]}-{run_id[-3:]}"

    commit_record = {
        "commit_id":                commit_id,
        "run_id":                   run_id,
        "subdomain_id":             audit.get("subdomain_id", ""),
        "subdomain_label":          audit.get("subdomain_label", ""),
        "kb_snapshot_id":           kb_snapshot_id,
        "problems_committed":       committed,
        "problems_skipped_duplicate": skipped,
        "problems_rejected_policy": rejected_state,
        "commit_min_state":         COMMIT_MIN_STATE,
        "registry_path":            str(REGISTRY_PROBLEMS),
        "run_log_path":             str(REGISTRY_RUN_LOG),
        "snapshot_after":           snap_id,
        "committed_at":             committed_at,
    }

    out_dir  = artifact_dir(WORK_DIR, run_id, STEP)
    out_path = out_dir / "commit_record.json"
    write_json(out_path, commit_record)
    register_artifact(WORK_DIR, run_id, f"{STEP}:commit_record",
                      out_path, content_state="verified", step=STEP)

    # ── Append to run_log ──────────────────────────────────────────────────────
    run_log_entry = {
        "run_id":           run_id,
        "commit_id":        commit_id,
        "subdomain_id":     audit.get("subdomain_id", ""),
        "subdomain_label":  audit.get("subdomain_label", ""),
        "kb_snapshot_id":   kb_snapshot_id,
        "pipeline_status":  audit.get("pipeline_status", "unknown"),
        "total_problems":   audit.get("total_problems", 0),
        "prior_run_id":     None,
        "committed_at":     committed_at,
    }
    write_jsonl_line(REGISTRY_RUN_LOG, run_log_entry)

    # ── Finalize run_record ────────────────────────────────────────────────────
    rec = load_run_record(WORK_DIR, run_id)
    rec["status"]       = status
    rec["finished_at"]  = committed_at
    rec["commit_id"]    = commit_id
    save_run_record(WORK_DIR, run_id, rec)

    emit_state(WORK_DIR, run_id, "run.done", STEP,
               {"commit_id": commit_id, "committed": committed,
                "skipped": skipped, "snapshot_id": snap_id})

    print(f"  [done] committed={committed} skipped={skipped} "
          f"commit_id={commit_id}")
    return {"status": "ok", "commit_record": commit_record}
