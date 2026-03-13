# Envelope: 09_commit

**Parent step:** `09_commit`
**Type:** `deterministic`
**Model:** —
**Upstream:** `08_finalization` → `final_problems.jsonl`, `run_audit.json`
**Downstream:** `registry/problems.jsonl` (append-only), `registry/run_log.jsonl` (append-only)
**Snapshot after:** yes (always — final state of run)

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "09_commit",
  "parent_step": "09_commit",
  "type": "deterministic",
  "inputs": {
    "final_problems_hash": "<sha256 of final_problems.jsonl>",
    "run_audit_hash": "<sha256 of run_audit.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "commit_record",
      "path": "runs/<run_id>/artifacts/09_commit/commit_record.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 0,
    "timeout_sec": 15,
    "priority": "normal",
    "novelty_guard": false
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "append_to_registry"
  }
}
```

---

## What This Step Does

**1. Append to `registry/problems.jsonl`**
All problems from `final_problems.jsonl` are appended line-by-line. Registry is append-only — no existing line is ever modified or deleted. Duplicate `problem_id` check before append: if a `problem_id` already exists in the registry, log warning and skip (should not occur — ID is content-addressed).

**2. Append to `registry/run_log.jsonl`**
One JSON line recording this run's summary for traceability and re-run delta computation.

**3. Update subdomain status**
Mark `SD-001` (Algebra) as `committed` in the subdomain registry index (if maintained). Non-blocking: if index file is absent, log warning and continue.

**4. Promote content state**
All `final_problems` artifacts in manifest: `candidate` → `verified`.

---

## Output Schema: commit_record.json

```json
{
  "commit_id": "COMMIT-<YYYY-MM-DD>-<NNN>",
  "run_id": "string",
  "subdomain_id": "SD-001",
  "subdomain_label": "Algebra",
  "kb_snapshot_id": "string",
  "problems_committed": "integer",
  "problems_skipped_duplicate": "integer",
  "registry_path": "registry/problems.jsonl",
  "run_log_path": "registry/run_log.jsonl",
  "snapshot_after": "<snapshot_id>",
  "committed_at": "ISO 8601 timestamp"
}
```

## run_log.jsonl entry

```json
{
  "run_id": "string",
  "commit_id": "string",
  "subdomain_id": "SD-001",
  "subdomain_label": "Algebra",
  "kb_snapshot_id": "string",
  "pipeline_status": "validated | partial | insufficient",
  "total_problems": "integer",
  "prior_run_id": "string | null",
  "committed_at": "ISO 8601 timestamp"
}
```

`prior_run_id` enables re-run delta computation (E-07): compare `total_problems` and `hallucination_risk` distributions between runs.

---

## Run Completion

After `09_commit` succeeds:
1. Orchestrator writes `run_record.json` with `status: done`
2. Final snapshot created
3. `state.jsonl` event: `run.done`
4. Exit code 0

---

## Content State on Completion
All committed problems: `candidate` → `verified`

## STOP Conditions
- `registry/problems.jsonl` not writable → `deterministic_step_error` (hard — do not mark run done)
- Snapshot write fails after 3 retries → `deterministic_step_error`
- All problems skipped as duplicates → log warning; run marked `done` with status `duplicate_skip`
