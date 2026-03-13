"""
step_09_commit.py — Append to registry (append-only). Final snapshot.
Type: deterministic
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, OUTPUT_DIR
from common import (
    sha256_file, now_iso, artifact_dir, write_json, write_jsonl_line,
    register_artifact, emit_state, create_snapshot,
    load_run_record, save_run_record,
)

STEP = "09_commit"

REGISTRY_PROBLEMS = OUTPUT_DIR / "problems.jsonl"
REGISTRY_RUN_LOG  = OUTPUT_DIR / "run_log.jsonl"


def run(run_id: str, final_path: Path, audit: dict, kb_snapshot_id: str) -> dict:
    """
    Returns: {"status": "ok"|"stop", "commit_record": {...}}
    """
    print(f"[{STEP}] run={run_id} problems={audit.get('total_problems', 0)}")
    emit_state(WORK_DIR, run_id, "step.start", STEP, {})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load existing problem IDs to detect duplicates ─────────────────────────
    existing_ids: set[str] = set()
    if REGISTRY_PROBLEMS.exists():
        with open(REGISTRY_PROBLEMS, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    existing_ids.add(rec.get("problem_id", ""))
                except Exception:
                    pass

    # ── Append problems ────────────────────────────────────────────────────────
    committed = 0
    skipped   = 0

    try:
        with open(final_path, "r", encoding="utf-8") as f_in, \
             open(REGISTRY_PROBLEMS, "a", encoding="utf-8") as f_out:
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                try:
                    problem = json.loads(line)
                    pid = problem.get("problem_id", "")
                    if pid in existing_ids:
                        skipped += 1
                        print(f"  [warn] duplicate problem_id skipped: {pid}")
                    else:
                        f_out.write(line + "\n")
                        existing_ids.add(pid)
                        committed += 1
                except json.JSONDecodeError:
                    print(f"  [warn] skipping malformed line in final_problems.jsonl")
    except IOError as e:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "deterministic_step_error", "reason": str(e)})
        return {"status": "stop", "stop_code": "deterministic_step_error"}

    if committed == 0 and skipped > 0:
        status = "duplicate_skip"
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
