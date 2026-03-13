# Executor — Dispatch and Completion

**Version:** 1.0.0

---

## Responsibility

The executor receives a TaskEnvelope, runs the step logic, writes outputs, and reports completion or failure back to the orchestrator. It does not plan, schedule, or make routing decisions — those belong to the orchestrator.

---

## Dispatch Flow

```
Orchestrator → envelope → Executor

1. Novelty guard check (if policy.novelty_guard = true)
   └─ cache hit → log task.cache_hit → return cached outputs → done

2. Log: task.claimed

3. Execute step logic (see steps/ for each step's logic)

4. Write outputs to declared paths under runs/<run_id>/artifacts/<step>/

5. Compute SHA-256 for each output file

6. Register hashes in manifest (atomic write)

7. Validate: do all required expected_outputs exist with registered hashes?
   └─ yes → log task.complete; update content_state to candidate
   └─ no  → log task.failed; retry if retries remain; else STOP

8. Signal orchestrator: task complete or failed
```

---

## Output Writing Rules

- Outputs are written **atomically**: write to `<path>.tmp`, then rename to `<path>`
- If a file at `<path>` already exists with a matching hash → skip write (idempotent)
- If a file exists with a different hash → overwrite only if task is a retry; else STOP

---

## LLM Step Execution

For `type: llm` steps, the executor additionally:

1. Constructs the prompt from the step's prompt template + current inputs
2. Records the prompt hash in the run log
3. Invokes the LLM with declared `model_id` and `temperature`
4. Records the raw LLM response verbatim in `logs/llm_calls.jsonl`:

```json
{
  "ts": "2026-03-03T09:01:45Z",
  "task_id": "sha256:...",
  "step": "01_parsing_01_extraction",
  "model_id": "local-mistral-7b",
  "temperature": 0.0,
  "prompt_hash": "sha256:...",
  "prompt_tokens": 312,
  "completion_tokens": 87,
  "raw_response": "{ ... }"
}
```

5. Parses and validates the response against the step's output schema
6. On parse failure: retry once; on second failure: STOP

The raw response is always logged before parsing. This enables replay: on resume, if a completed task is re-encountered, the raw response is replayed rather than the LLM being re-invoked.

---

## Deterministic Step Execution

For `type: deterministic` steps (02_retrieval, 03_enrichment_02, 05_validation, 09_commit), the executor:

1. Runs the deterministic logic (no LLM, no network if avoidable)
2. Writes outputs
3. Registers hashes
4. Never retries on logic error — deterministic failures are always STOP

---

## Completion Event

```json
{
  "event": "task.complete",
  "task_id": "sha256:...",
  "step": "01_parsing_01_extraction",
  "outputs": [
    {
      "key": "raw_facts",
      "path": "runs/.../artifacts/01_parsing_01_extraction/raw_facts.json",
      "hash": "sha256:..."
    }
  ],
  "duration_ms": 1240,
  "type": "llm",
  "cache_hit": false
}
```

---

## Failure Event

```json
{
  "event": "task.failed",
  "task_id": "sha256:...",
  "step": "04_hypothesis",
  "attempt": 1,
  "reason": "llm_malformed_json",
  "retry_scheduled": true,
  "next_attempt": 2
}
```

---

## Retry Behavior

| Failure Reason | `type: llm` | `type: deterministic` |
|----------------|------------|----------------------|
| Malformed output | Retry (≤ retries) | STOP |
| Timeout | Retry once | STOP |
| Missing required output | STOP | STOP |
| Novelty guard: no novelty on retry | STOP (no_novelty) | — |
| Loop limit exceeded | STOP (loop_limit) | — |

---

## LLM Replay on Resume

If a run is resumed and an LLM task is already complete (hash in manifest, raw response in `logs/llm_calls.jsonl`):

1. Executor reads the raw response from the log
2. Re-parses it (no LLM call)
3. Verifies output hash matches manifest
4. Marks task complete — identical to original completion

This guarantees deterministic replay of non-deterministic steps.
