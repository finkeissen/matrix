# Run — Lifecycle and Directory Layout

**Version:** 1.0.0

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

Example: `2026-03-03_001`

Run IDs are sequential per day. Uniqueness is enforced by the run directory: if the directory already exists, increment `NNN`.

---

## Lifecycle States

```
INIT
  │
PREFLIGHT         ← check KB snapshot, inputs exist, output dir writable
  │
PLANNED           ← all envelopes created, task_ids derived, manifest initialized
  │
RUNNING           ← envelopes dispatched and executed in order
  │
FINALIZING        ← 08_finalization + 09_commit executed
  │
DONE  ←──────────── all required outputs exist, hashes verified
  or
STOP              ← unrecoverable error; stop_record.json written
```

Every transition is logged as an event in `state.jsonl`.

---

## Directory Layout

```
runs/
  2026-03-03_001/
    run_record.json          ← run metadata (id, session_id, kb_snapshot, status)
    manifest.json            ← artifact registry (path → hash → content_state)
    state.jsonl              ← append-only lifecycle events
    stop_record.json         ← present only if run ended with STOP
    envelopes/
      <task_id>.json         ← one file per envelope (immutable after creation)
    artifacts/
      01_parsing_01_extraction/
        raw_facts.json
      01_parsing_02_confidence/
        scored_facts.json
      02_retrieval/
        context_units.json
      03_enrichment_01_terminology/
        mapped_facts.json
      03_enrichment_02_unit_normalization/
        normalized_facts.json
      03_enrichment_03_gap_detection/
        gap_detection.json
      04_hypothesis/
        candidate.json
      05_validation/
        validation_report.json
      06_clarification/
        clarification_request.json    ← only if triggered
      07_examination_01_weakness_scan/
        weakness_scan.json
      07_examination_02_alternative_check/
        examination_result.json
      08_finalization/
        final_answer.json
      09_commit/
        commit_record.json
    snapshots/
      <snapshot_id>/
        manifest_snapshot.json
        state_offset.json
    logs/
      run.jsonl              ← orchestrator events
```

---

## run_record.json Schema

```json
{
  "run_id": "2026-03-03_001",
  "session_id": "sess-00291",
  "kb_snapshot_id": "SNAP-00189",
  "kb_version": "2.1.0",
  "system_version": "2.0.0",
  "status": "running | done | stop",
  "created_at": "2026-03-03T09:00:00Z",
  "completed_at": null,
  "envelopes_total": 14,
  "envelopes_complete": 7,
  "envelopes_pending": 7,
  "clarification_rounds": 0
}
```

---

## state.jsonl Events

Every event is one JSON line, append-only. Required fields:

```json
{
  "ts": "2026-03-03T09:00:12Z",
  "run_id": "2026-03-03_001",
  "actor": "orchestrator | executor | step:<step_id>",
  "event": "<event_name>",
  "task_id": "<sha256:...> or null",
  "payload": {}
}
```

### Standard Events

| Event | Actor | When |
|-------|-------|------|
| `run.init` | orchestrator | Run directory created |
| `run.preflight_ok` | orchestrator | All preconditions met |
| `run.planned` | orchestrator | All envelopes created |
| `run.done` | orchestrator | All required outputs exist |
| `run.stop` | orchestrator | Unrecoverable error |
| `task.created` | orchestrator | Envelope written to `envelopes/` |
| `task.dispatched` | orchestrator | Sent to executor |
| `task.claimed` | executor | Executor started work |
| `task.complete` | executor | All expected_outputs exist + hashes registered |
| `task.failed` | executor | Error during execution |
| `task.retrying` | orchestrator | Retry attempt N of policy.retries |
| `task.cache_hit` | orchestrator | Novelty guard returned prior result |
| `snapshot.created` | orchestrator | Snapshot written |

---

## Preflight Checks

Before any envelope is created:

| Check | Failure Action |
|-------|---------------|
| KB snapshot exists and is readable | STOP: `preflight_snapshot_missing` |
| Output run directory is writable | STOP: `preflight_dir_unwritable` |
| `raw_text` input is non-empty | STOP: `preflight_input_empty` |
| System version recorded | warn; continue |

Preflight never creates envelopes. It only validates preconditions.

---

## Snapshot Cadence

A snapshot captures the current `manifest.json` + `state.jsonl` offset so the run can be resumed from that point.

Snapshots are created:
- After `03_enrichment_03_gap_detection` completes (pre-LLM checkpoint)
- After `05_validation` completes
- After any clarification round completes
- At `08_finalization` (pre-commit checkpoint)
- Before STOP

Snapshot creation is logged as `snapshot.created` in `state.jsonl`.
