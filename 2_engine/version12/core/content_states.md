# Content States
## Result Lifecycle: Candidate → Verified → Accepted

**Version:** 1.0.0

---

## Why Content State Exists

A task can be `complete` (outputs written, hashes registered) while its output is still `candidate` — meaning it has not yet been validated or examined. Content state separates **execution completion** from **epistemic trust**.

This is the key insight from the Matrix Engine: generation and verification are different activities, and their results must be tracked independently.

---

## State Machine

```
              [task.complete]
                    │
                    ▼
              candidate
                    │
        [05_validation: valid=true]
                    │
                    ▼
              verified
             /        \
[07_exam_01:         [07_exam_01:
 all strong]          ambiguous/weak]
      │                     │
      ▼                     ▼
  accepted              disputed
                            │
                 [07_exam_02: decision=reject]
                            │
                            ▼
                       superseded
                   (new candidate from retry)
```

---

## State Definitions

| State | Epistemic Meaning | Set By |
|-------|------------------|--------|
| `candidate` | Produced; untested | Executor on `task.complete` |
| `verified` | Passed deterministic validation | `05_validation` when `valid=true` |
| `disputed` | Validation passed but examination found weakness | `07_examination_01` on `ambiguous` or `weak` |
| `accepted` | Passed full adversarial examination | `07_examination_02` on `decision=accept` |
| `superseded` | Replaced by a newer result in same run | Orchestrator on retry |
| `rejected` | Failed examination; not used downstream | `07_examination_02` on `decision=reject` |

---

## What Flows Downstream

Only artifacts in the right content state are passed to downstream steps:

| Downstream Step | Requires Input State |
|----------------|---------------------|
| `06_clarification` | `candidate` (validation found missing facts) |
| `07_examination_01` | `verified` |
| `07_examination_02` | `verified` (with weakness scan result) |
| `08_finalization` | `accepted` (or `verified` if examination skipped) |
| `09_commit` | `accepted` |

Passing a `candidate` artifact to `08_finalization` is a policy violation — the orchestrator must block it.

---

## Disputed Results in Output

When a result reaches `08_finalization` with `content_state: accepted` but with non-empty `weak_criteria` from `07_examination_01`, the final answer includes:

```json
{
  "result": { ... },
  "weak_points": [
    "Measurement interval between fasting glucose tests not documented."
  ],
  "content_state": "accepted_with_caveats"
}
```

This surfaces epistemic nuance to the caller without blocking delivery.

---

## Superseded History

When a candidate is superseded by a retry:

- The original artifact **remains in the manifest** with `content_state: superseded`
- The new artifact is created with a new `task_id`
- Both are linked via `supersedes: <original_artifact_hash>` in the manifest

History is never deleted. The run directory always contains the full decision trail.

---

## Content State in Audit Trace

The final audit trace (`08_finalization`) records the content state trajectory:

```json
{
  "trace_id": "TRACE-2026-03-03-00291",
  "result_aku_id": "AKU-00123",
  "content_state_at_delivery": "accepted",
  "state_trajectory": [
    { "state": "candidate",  "task_id": "sha256:aaa...", "ts": "09:01" },
    { "state": "verified",   "task_id": "sha256:bbb...", "ts": "09:02" },
    { "state": "disputed",   "task_id": "sha256:ccc...", "ts": "09:03" },
    { "state": "accepted",   "task_id": "sha256:ddd...", "ts": "09:04" }
  ]
}
```
