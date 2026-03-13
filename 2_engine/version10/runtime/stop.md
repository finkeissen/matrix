# STOP — Protocol and Stop Codes

**Version:** 2.0.0
**Changes from v1:** Added `scope_clarification_exhausted`, `retrieval_empty`; updated clarification limit from 3 to 2 rounds (E-01).

---

## Principle

> STOP is a valid outcome — not a failure.
> A STOP with a clear diagnostic is better than silent continuation with corrupt state.

---

## When STOP Is Emitted

| Trigger | Stop Code | Recoverable |
|---|---|---|
| Preflight: seed file missing or unreadable | `preflight_snapshot_missing` | true |
| Preflight: output directory not writable | `preflight_dir_unwritable` | true |
| Preflight: subdomain_id not found in seed | `preflight_input_empty` | true |
| Manifest integrity mismatch on resume | `manifest_integrity_mismatch` | false |
| Required output missing after all retries | `required_output_missing` | false |
| Deterministic step logic error | `deterministic_step_error` | false |
| LLM step: malformed output after retries | `llm_output_invalid` | false |
| Retry with no novelty detected | `no_novelty_on_retry` | false |
| Loop limit exceeded | `loop_limit_exceeded` | false |
| Clarification rounds >= 2 before dispatch | `scope_clarification_exhausted` | false |
| Retrieval: no chapters and no fallback | `retrieval_empty` | true |
| Audit log write failure | `audit_write_failure` | false |
| Registry write failure | `deterministic_step_error` | false |

---

## stop_record.json Schema

Written atomically to `runs/<run_id>/stop_record.json`:

```json
{
  "run_id": "2026-03-04_001",
  "session_id": "sess-00001",
  "stop_code": "scope_clarification_exhausted",
  "recoverable": false,
  "stage": "06_clarification",
  "task_id": null,
  "reason": "Scope clarification limit of 2 rounds reached without producing a valid scope. Manual review required.",
  "details": {
    "clarification_rounds_attempted": 2,
    "last_scope_confidence_score": 0.61,
    "subdomain_id": "SD-001"
  },
  "snapshot_before_stop": "snap-003",
  "timestamp": "2026-03-04T10:45:00Z"
}
```

---

## STOP Procedure

```
1. Log: run.stop (in state.jsonl)
2. Write stop_record.json (atomic)
3. Create snapshot (partial state preserved)
4. Terminate gracefully (exit code 2)
```

---

## Recoverable STOPs and Partial Results

| Stop Code | Degraded Response |
|---|---|
| `scope_clarification_exhausted` | Return partial run with best scope attempt; manual review required |
| `retrieval_empty` | Retry after providing local copy of canonical source |
| `preflight_snapshot_missing` | Fix seed file path; resume |
| `no_novelty_on_retry` | Return prior result with `review_status: draft` and uncertainty flag |

---

## STOP vs Warn

| Condition | STOP? | Reason |
|---|---|---|
| Required output missing | Yes | Integrity cannot be guaranteed |
| Optional output missing | No (warn) | Downstream steps can proceed |
| Retrieval fallback used | No (warn) | Proceed with scope.boundaries as chapters |
| LLM confidence low | No (warn) | Flagged in content state |
| Category estimated_problem_count = 0 | No (warn) | Skip category in 04a dispatch |
| problem_id prefix collision (A/B) | No (warn) | Resolved with suffix |
