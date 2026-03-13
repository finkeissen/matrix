# Run — Lifecycle and Directory Layout

**Version:** 2.0.0
**Changes from v1:** `kb_snapshot_id` = sha256(seeds file) for generation runs (E-03); `clarification_rounds` field added to `run_record.json` (E-01); directory layout adapted for per-category envelopes.

---

## Core Invariant

> A run is the canonical unit of work.
> Everything reproducible must exist under `runs/<date>/<run_id>/`.
> No important state lives only in memory.

---

## Run ID Format

```
YYYY-MM-DD_NNN
```

Example: `2026-03-04_001`

Run IDs are sequential per day. Uniqueness is enforced by the run directory: if it already exists, increment `NNN`.

---

## Lifecycle States

```
INIT
  │
PREFLIGHT         ← check seed file, inputs exist, output dir writable
  │
PLANNED           ← all envelopes created, task_ids derived, manifest initialized
  │
RUNNING           ← envelopes dispatched and executed in order
  │
FINALIZING        ← 08_finalization + 09_commit executed
  │
DONE  ←────────── all required outputs exist, hashes verified, registry appended
  or
STOP              ← unrecoverable error; stop_record.json written
```

Every transition is logged as an event in `state.jsonl`.

---

## kb_snapshot_id (E-03)

In generation runs, there is no external knowledge base. The "KB" is the subdomain seed file.

```python
import hashlib

def compute_kb_snapshot_id(seed_path: str) -> str:
    with open(seed_path, "rb") as f:
        return "sha256:" + hashlib.sha256(f.read()).hexdigest()

# Called at preflight:
kb_snapshot_id = compute_kb_snapshot_id("seeds/seed_atomare_probleme.csv")
```

This value is written to `run_record.json` and carried in every envelope. Cross-run Novelty Guard reuse requires matching `kb_snapshot_id` — preventing stale cache hits when the seed file changes.

---

## Clarification Rounds (E-01)

`run_record.json` carries a `clarification_rounds` counter (default 0). The orchestrator increments it before dispatching `06_clarification`. If `clarification_rounds >= 2` before dispatch:

```
STOP: scope_clarification_exhausted
```

No further `06_clarification` envelope is created.

---

## Directory Layout

```
runs/
  2026-03-04_001/
    run_record.json          ← run metadata
    manifest.json            ← artifact registry
    state.jsonl              ← append-only lifecycle events
    stop_record.json         ← present only if run ended with STOP
    envelopes/
      <task_id>.json         ← one file per envelope (immutable after creation)
    artifacts/
      01_scope/
        scope.json
      01_scope_confidence/
        scope_confidence.json
      02_retrieval/
        canonical_structure.json
      03_enrichment_01_categories/
        categories.json
      03_enrichment_02_normalize/
        normalized_categories.json
      03_enrichment_03_gap_detection/
        gap_detection.json
      04a_generation/
        cat_1/problems_draft.json
        cat_2/problems_draft.json
        ...
        cat_N/problems_draft.json
      04b_generation_review/
        cat_1/problems_reviewed.json
        cat_2/problems_reviewed.json
        ...
        cat_N/problems_reviewed.json
      05_validation/
        validation_report.json
      06_clarification/
        clarification_request_round_1.json  ← if triggered
        clarification_request_round_2.json  ← if triggered again
      07_examination_01_hallucination_scan/
        hallucination_report.json
      07_examination_02_alternative_check/
        alternative_check.json
      08_finalization/
        final_problems.jsonl
        run_audit.json
      09_commit/
        commit_record.json
    snapshots/
      <snapshot_id>/
        manifest_snapshot.json
        state_offset.json
    logs/
      run.jsonl
      llm_calls.jsonl        ← raw LLM responses (for replay on resume)
```

---

## run_record.json Schema

```json
{
  "run_id": "2026-03-04_001",
  "session_id": "sess-00001",
  "kb_snapshot_id": "sha256:<hash of seeds/seed_atomare_probleme.csv>",
  "subdomain_id": "SD-001",
  "subdomain_label": "Algebra",
  "system_version": "2.0.0",
  "status": "running | done | stop",
  "created_at": "2026-03-04T10:00:00Z",
  "completed_at": null,
  "envelopes_total": 24,
  "envelopes_complete": 0,
  "envelopes_pending": 24,
  "clarification_rounds": 0,
  "category_count": 10,
  "prior_run_id": null
}
```

`prior_run_id` is set on re-runs (E-07) to enable delta computation.

---

## Preflight Checks

| Check | Failure Action |
|---|---|
| `seeds/seed_atomare_probleme.csv` exists and is readable | STOP: `preflight_snapshot_missing` |
| Output run directory is writable | STOP: `preflight_dir_unwritable` |
| `subdomain_id` exists in seed file | STOP: `preflight_input_empty` |
| `registry/` directory writable | STOP: `preflight_dir_unwritable` |

---

## Snapshot Cadence

Snapshots are created:
- After `03_enrichment_03_gap_detection` completes (pre-generation checkpoint)
- After `05_validation` completes
- After any clarification round completes
- At `08_finalization` (pre-commit checkpoint)
- At `09_commit` (final state)
- Before STOP
