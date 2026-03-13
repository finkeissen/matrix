# STOP — Protocol and Stop Codes

**Version:** 1.0.0

---

## Principle

> STOP is a valid outcome — not a failure.
> A STOP with a clear diagnostic is better than silent continuation with corrupt state.

---

## When STOP Is Emitted

| Trigger | Stop Code |
|---------|-----------|
| Preflight: KB snapshot missing | `preflight_snapshot_missing` |
| Preflight: output directory not writable | `preflight_dir_unwritable` |
| Preflight: input empty | `preflight_input_empty` |
| Manifest integrity mismatch on resume | `manifest_integrity_mismatch` |
| Required output missing after all retries | `required_output_missing` |
| Deterministic step logic error | `deterministic_step_error` |
| LLM step: malformed output after retries | `llm_output_invalid` |
| Retry with no novelty detected | `no_novelty_on_retry` |
| Loop limit exceeded | `loop_limit_exceeded` |
| Max clarification rounds exceeded | `clarification_limit_exceeded` |
| Audit log write failure | `audit_write_failure` |
| Policy violation in commit gate | `policy_violation` |

---

## stop_record.json Schema

Written atomically to `runs/<run_id>/stop_record.json`:

```json
{
  "run_id": "2026-03-03_001",
  "session_id": "sess-00291",
  "stop_code": "required_output_missing",
  "recoverable": false,
  "stage": "04_hypothesis",
  "task_id": "sha256:...",
  "reason": "LLM returned malformed JSON after 1 retry. Step: 04_hypothesis.",
  "details": {
    "attempt": 2,
    "raw_response_logged": true,
    "last_error": "JSONDecodeError at position 142"
  },
  "snapshot_before_stop": "SNAP-003",
  "timestamp": "2026-03-03T09:08:44Z"
}
```

---

## Recoverability

| `recoverable` | Meaning | Action |
|---------------|---------|--------|
| `true` | External condition may change (e.g. KB snapshot unavailable); resume may succeed | User can fix condition and resume |
| `false` | Structural or logic failure; resume will reproduce same error | Requires code or data fix |

---

## STOP Procedure

```
1. Log: run.stop (in state.jsonl)
2. Write stop_record.json (atomic)
3. Create snapshot (partial state preserved)
4. Terminate gracefully (exit code 2)
```

The snapshot created at STOP time captures everything produced before the failure. A later investigation can inspect the run directory to understand what happened.

---

## Recoverable STOPs and Partial Results

For `recoverable: true` STOPs, the final answer may still be delivered in a degraded form:

| Stop Code | Degraded Response |
|-----------|------------------|
| `clarification_limit_exceeded` | Return `status: insufficient_facts` with best partial candidate |
| `no_novelty_on_retry` | Return `status: insufficient` with prior result and uncertainty flag |
| `llm_output_invalid` (non-critical step) | Return `status: degraded` with explanation |

The degraded response is always structured — never fabricated.

---

## STOP vs Warn

Not every anomaly triggers STOP. The distinction:

| Condition | STOP? | Reason |
|-----------|-------|--------|
| Required output missing | Yes | Integrity cannot be guaranteed |
| Optional output missing | No (warn) | Downstream steps can proceed without it |
| LLM confidence low | No (warn) | Flagged in content state; validation handles it |
| Retrieval returned fewer than top_k | No (warn) | Proceed with available context |
| Unit conversion rule missing | No (warn) | Retain original value; flag field |
