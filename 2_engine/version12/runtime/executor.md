# Executor — Dispatch and Completion

**Version:** 2.0.0
**Changes from v1:** Model routing via `policy.model` (E-06); per-category envelope dispatch for 04a/04b; updated step IDs.

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

3. Execute step logic (see pipeline/steps/ for each step's logic)

4. Write outputs to declared paths under runs/<run_id>/artifacts/<step>/

5. Compute SHA-256 for each output file

6. Register hashes in manifest (atomic write)

7. Validate: do all required expected_outputs exist with registered hashes?
   └─ yes → log task.complete; update content_state to candidate
   └─ no  → log task.failed; retry if retries remain; else STOP

8. Signal orchestrator: task complete or failed
```

---

## Model Routing (E-06)

For `type: llm` steps, the executor resolves `policy.model` to a local endpoint before dispatch:

```python
MODEL_ENDPOINTS = {
    "19b":  "http://localhost:11434/api/generate?model=qwen2.5-19b-a3b",
    "35b":  "http://localhost:11434/api/generate?model=qwen2.5-35b-a3b",
    "122b": "http://localhost:11434/api/generate?model=qwen2.5-122b-a10b",
}

def resolve_model(policy_model: str) -> str:
    if policy_model not in MODEL_ENDPOINTS:
        raise ConfigError(f"Unknown model: {policy_model}")
    return MODEL_ENDPOINTS[policy_model]
```

Model endpoints are configured externally (e.g. `config/models.json`). The executor never hardcodes endpoints. All LLM calls use `temperature: 0.0` for reproducibility.

---

## LLM Step Execution

For `type: llm` steps, the executor:

1. Constructs the prompt from the step's prompt template + current inputs
2. Resolves `policy.model` to local endpoint
3. Records the prompt hash in the run log
4. Invokes the LLM with `temperature: 0.0`
5. Records the raw LLM response verbatim in `logs/llm_calls.jsonl`:

```json
{
  "ts": "2026-03-04T10:01:45Z",
  "task_id": "sha256:...",
  "step": "04a_generation",
  "model": "35b",
  "model_endpoint": "http://localhost:11434/...",
  "temperature": 0.0,
  "prompt_hash": "sha256:...",
  "prompt_tokens": 1300,
  "completion_tokens": 1500,
  "raw_response": "{ ... }"
}
```

6. Parses and validates the response against the step's output schema
7. On parse failure: retry once; on second failure: STOP

The raw response is always logged before parsing. This enables replay on resume.

---

## Deterministic Step Execution

For `type: deterministic` steps (`02_retrieval`, `03_enrichment_02_normalize`, `05_validation` phase 1, `09_commit`):

1. Runs the deterministic logic (no LLM, no network if avoidable)
2. Writes outputs
3. Registers hashes
4. Never retries on logic error — deterministic failures are always STOP

---

## Per-Category Dispatch (04a / 04b)

Steps `04a_generation` and `04b_generation_review` are instantiated once per category. The orchestrator creates N envelope pairs from `normalized_categories.items`. The executor dispatches them sequentially in category index order:

```
04a cat_1 → 04b cat_1 → 04a cat_2 → 04b cat_2 → ... → 04a cat_N → 04b cat_N
```

Each envelope has a unique `task_id` because `category_hash` is part of inputs. Novelty Guard operates independently per category-step pair.

---

## Output Writing Rules

- Outputs written **atomically**: write to `<path>.tmp`, then rename to `<path>`
- If file at `<path>` already exists with matching hash → skip (idempotent)
- If file exists with different hash → overwrite only on retry; else STOP

---

## Retry Behavior

| Failure Reason | `type: llm` | `type: deterministic` |
|---|---|---|
| Malformed output | Retry (≤ retries) | STOP |
| Timeout | Retry once | STOP |
| Missing required output | STOP | STOP |
| No novelty on retry | STOP: `no_novelty_on_retry` | — |
| Loop limit exceeded | STOP: `loop_limit_exceeded` | — |

---

## LLM Replay on Resume

If a run is resumed and an LLM task is already complete:

1. Executor reads raw response from `logs/llm_calls.jsonl`
2. Re-parses it (no LLM call)
3. Verifies output hash matches manifest
4. Marks task complete — identical to original completion

Guarantees deterministic replay of non-deterministic steps.
