# TaskEnvelope — Canonical Schema
## The Smallest Executable Unit

**Version:** 1.0.0
**Used by:** All 14 GIA pipeline steps
**Inherited from:** Matrix Engine version06 TaskEnvelope model

---

## Purpose

A TaskEnvelope is an **immutable declaration of a single unit of work**. It defines everything needed to execute, verify, resume, and audit one pipeline step — before execution begins.

No step may run without a TaskEnvelope.
No envelope may be mutated after creation.
Completion is determined by the existence and integrity of `expected_outputs`, not by the envelope itself.

---

## Full Schema

```json
{
  "envelope_version": "1.0.0",

  "task_id": "sha256:a1b2c3...",
  "run_id": "2026-03-03_run_001",
  "session_id": "sess-00291",

  "step": "01_parsing_01_extraction",
  "parent_step": "01_parsing",
  "type": "llm | deterministic",

  "inputs": {
    "raw_text_hash": "sha256:...",
    "session_id": "sess-00291"
  },
  "input_snapshot_id": "SNAP-00189",

  "expected_outputs": [
    {
      "key": "raw_facts",
      "path": "runs/2026-03-03/run_001/artifacts/01_parsing_01/raw_facts.json",
      "required": true
    }
  ],

  "policy": {
    "retries": 1,
    "timeout_sec": 30,
    "priority": "normal",
    "novelty_guard": true
  },

  "provenance": {
    "created_by": "orchestrator",
    "created_at": "2026-03-03T09:00:00Z",
    "parent_task_id": null,
    "reason": "initial_parse"
  }
}
```

---

## Field Definitions

### Identity

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | SHA-256 of `(step + sorted input hashes)`. Identical work → identical ID. |
| `run_id` | string | The run this envelope belongs to. Format: `YYYY-MM-DD_NNN`. |
| `session_id` | string | User session — links envelopes across steps for one query. |

### Step Declaration

| Field | Type | Description |
|-------|------|-------------|
| `step` | string | Exact step ID — matches filename in `pipeline_steps_v2/`. |
| `parent_step` | string | Logical parent (e.g. `01_parsing` for both `01_parsing_01` and `01_parsing_02`). |
| `type` | enum | `deterministic` or `llm`. Determines scheduling priority and retry behavior. |

### Inputs

| Field | Type | Description |
|-------|------|-------------|
| `inputs` | object | Flat map of input name → hash or value. **No raw content — only references.** |
| `input_snapshot_id` | string | KB snapshot used for this step. Must be pinned. |

Inputs are hashed, not embedded. Large values (AKU context, case facts) live in the artifact store; only their hash is in the envelope.

### Expected Outputs

Each entry declares:

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | Logical name for downstream steps to reference. |
| `path` | string | Deterministic canonical path under the run directory. |
| `required` | bool | If `true`, missing output → STOP. If `false`, missing output → warn. |

A task is `complete` when all `required: true` outputs exist at their declared paths and their SHA-256 hashes are registered in the manifest.

### Policy

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `retries` | int | 1 | Max retry attempts on failure. |
| `timeout_sec` | int | 30 | Wall clock timeout. `null` = no limit. |
| `priority` | enum | `normal` | `high | normal | low`. Deterministic steps always run before LLM steps. |
| `novelty_guard` | bool | `true` for LLM, `false` for deterministic | If `true`, check cache before dispatching. |

### Provenance

| Field | Type | Description |
|-------|------|-------------|
| `created_by` | string | Module or component that created this envelope. |
| `created_at` | ISO 8601 | Creation timestamp. |
| `parent_task_id` | string or null | The task whose output triggered creation of this envelope. |
| `reason` | string | Short human-readable reason (`initial_parse`, `retry_after_rejection`, etc.). |

---

## task_id Derivation

```python
import hashlib, json

def derive_task_id(step: str, inputs: dict) -> str:
    canonical = json.dumps(
        {"step": step, "inputs": inputs},
        sort_keys=True,
        ensure_ascii=True
    )
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
```

The same step with the same inputs **always** produces the same `task_id`. This is the foundation of the novelty guard and resume skip logic.

---

## Output Path Derivation

Paths are deterministic — never random:

```
runs/<run_id>/artifacts/<step>/<output_key>.json
```

Example:
```
runs/2026-03-03_001/artifacts/01_parsing_01_extraction/raw_facts.json
```

---

## Immutability Rule

Once created, an envelope is **never modified**. If inputs change (e.g. after clarification), a **new envelope** is created with a new `task_id`. The old envelope and its outputs remain in the run directory as history.

---

## Envelope States (tracked in state.jsonl, not in envelope)

```
created → dispatched → running → complete
                              → failed → (retry → running)
                                      → stop
```

State transitions are append-only events in `state.jsonl`. The envelope itself does not change.

---

## Failure Behavior by Type

| `type` | On timeout | On LLM error | On missing output |
|--------|-----------|--------------|-------------------|
| `deterministic` | STOP | — | STOP |
| `llm` | Retry (≤ policy.retries), then STOP | Retry once, then STOP | STOP if required |
