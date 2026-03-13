# Novelty Guard
## Anti-Loop and Cache-Hit Mechanism for LLM Steps

**Version:** 1.0.0
**Applies to:** All steps with `type: llm` and `policy.novelty_guard: true`

---

## Problem This Solves

Without a novelty guard, a pipeline re-run with identical inputs will invoke the LLM again, spend tokens, and produce a result that is either identical (wasted compute) or slightly different (non-determinism). In a system that processes many queries or reruns, this accumulates.

The novelty guard provides:
1. **Cache hit**: identical inputs → return prior result instantly
2. **Loop prevention**: if the same step keeps being retried with no input change, detect and STOP

---

## How It Works

Before any LLM envelope is dispatched, the executor runs:

```
task_id = derive_task_id(step, inputs)

if task_id in manifest.completed_tasks:
    → return cached output (skip LLM call)
    → log event: task.cache_hit

else:
    → dispatch envelope normally
```

Since `task_id` is content-addressed (derived from step + input hashes), identical work always produces the same `task_id`. If that ID is already marked complete in the manifest, the output is reused.

---

## Cache Hit Behavior

When a cache hit occurs:

```json
{
  "event": "task.cache_hit",
  "task_id": "sha256:...",
  "step": "04_hypothesis",
  "run_id": "2026-03-03_001",
  "prior_run_id": "2026-03-02_003",
  "output_key": "candidate",
  "reused_artifact_hash": "sha256:..."
}
```

The cached artifact is **symlinked** (not copied) into the current run's artifact directory. The manifest records it as `reused_from: prior_run_id`.

Cross-run reuse requires that both runs reference the same `kb_snapshot_id`. If snapshots differ, the cache hit is skipped even if `task_id` matches.

---

## Novelty Check (Input Change Detection)

Before a retry after examination rejection, the orchestrator checks whether the retry inputs are actually different from the prior attempt:

```
prior_input_hash = manifest.get_task_input_hash(prior_task_id)
new_input_hash   = hash(new_inputs)

if prior_input_hash == new_input_hash:
    → no novelty detected
    → do NOT retry
    → STOP: no_novelty_on_retry
```

This prevents the retry loop from regenerating the same candidate repeatedly.

---

## Novelty Score (Informational)

For observability, the novelty guard computes a simple novelty signal per LLM step:

```
novelty_score = 1.0   if task_id is new (no prior result)
              = 0.0   if task_id was a cache hit
              = 0.5   if task_id is new but inputs share > 80% of fields with a prior task
```

This is logged but does not affect routing. It is used in future `review_pack` generation to detect stagnating sessions.

---

## Configuration

Per-envelope, in `policy`:

```json
{
  "novelty_guard": true,
  "cache_scope": "run | cross_run",
  "require_same_snapshot": true
}
```

| Field | Default | Meaning |
|-------|---------|---------|
| `novelty_guard` | `true` for LLM, `false` for deterministic | Enable/disable |
| `cache_scope` | `cross_run` | `run`: only reuse from current run. `cross_run`: reuse from prior runs. |
| `require_same_snapshot` | `true` | If `true`, cross-run reuse only valid if `kb_snapshot_id` matches. |

---

## Loop Detection

A run-level loop counter tracks how many times a step has been dispatched within one session:

```
run_state.dispatch_counts["04_hypothesis"] = 3
```

If `dispatch_counts[step] > policy.retries + 1`:
- Log: `loop.detected`
- STOP: `loop_limit_exceeded`

This is the hard backstop against infinite retry loops.

---

## Summary

| Scenario | Behavior |
|----------|----------|
| Same inputs, same snapshot, prior result exists | Cache hit → skip LLM |
| Same inputs, different snapshot | Run LLM normally |
| Different inputs | Run LLM normally |
| Retry with unchanged inputs | Detect no novelty → STOP |
| Step dispatched > retries+1 times | Loop detected → STOP |
