# TaskEnvelope — Canonical Schema
## The Smallest Executable Unit

**Version:** 2.0.0
**Changes from v1:** Added `policy.model` for step-specific model routing (E-06).
**Used by:** All 15 pipeline steps (v2)

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
  "envelope_version": "2.0.0",

  "task_id": "sha256:a1b2c3...",
  "run_id": "2026-03-04_001",
  "session_id": "sess-00001",

  "step": "04a_generation",
  "parent_step": "04_generation",
  "type": "llm | deterministic",

  "inputs": {
    "scope_hash": "sha256:...",
    "category_hash": "sha256:...",
    "kb_snapshot_id": "sha256:..."
  },
  "input_snapshot_id": "sha256:...",

  "expected_outputs": [
    {
      "key": "problems_draft",
      "path": "runs/2026-03-04_001/artifacts/04a_generation/cat_5/problems_draft.json",
      "required": true
    }
  ],

  "policy": {
    "retries": 1,
    "timeout_sec": 60,
    "priority": "normal",
    "novelty_guard": true,
    "cache_scope": "cross_run",
    "require_same_snapshot": true,
    "model": "35b"
  },

  "provenance": {
    "created_by": "orchestrator",
    "created_at": "2026-03-04T10:00:00Z",
    "parent_task_id": null,
    "reason": "generate_atomic_problems_draft"
  }
}
```

---

## Field Definitions

### Identity

| Field | Type | Description |
|---|---|---|
| `task_id` | string | SHA-256 of `(step + sorted input hashes)`. Identical work → identical ID. |
| `run_id` | string | The run this envelope belongs to. Format: `YYYY-MM-DD_NNN`. |
| `session_id` | string | Links envelopes across steps for one subdomain run. |

### Step Declaration

| Field | Type | Description |
|---|---|---|
| `step` | string | Exact step ID — matches filename in `pipeline/steps/`. |
| `parent_step` | string | Logical parent (e.g. `04_generation` for `04a_generation` and `04b_generation_review`). |
| `type` | enum | `deterministic` or `llm`. Deterministic steps run before LLM steps. |

### Policy

| Field | Type | Default | Description |
|---|---|---|---|
| `retries` | int | 1 | Max retry attempts on failure. |
| `timeout_sec` | int | 30 | Wall clock timeout. `null` = no limit. |
| `priority` | enum | `normal` | `high \| normal \| low`. Deterministic steps always run before LLM steps. |
| `novelty_guard` | bool | `true` for llm | If true, check cache before dispatching. |
| `cache_scope` | enum | `cross_run` | `run`: current run only. `cross_run`: reuse from prior runs. |
| `require_same_snapshot` | bool | `true` | Cross-run reuse only valid if `kb_snapshot_id` matches. |
| `model` | enum | — | **New in v2.** `19b \| 35b \| 122b`. Required for `type: llm`. Executor resolves to local endpoint. See E-06. |

### task_id Derivation

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

The same step with the same inputs **always** produces the same `task_id`. Foundation of the Novelty Guard and resume skip logic.

---

## Step IDs (v2)

```
01_scope
01_scope_confidence
02_retrieval
03_enrichment_01_categories
03_enrichment_02_normalize
03_enrichment_03_gap_detection
04a_generation
04b_generation_review
05_validation
06_clarification
07_examination_01_hallucination_scan
07_examination_02_alternative_check
08_finalization
09_commit
```

---

## Immutability Rule

Once created, an envelope is **never modified**. If inputs change (e.g. after clarification), a **new envelope** is created with a new `task_id`. The old envelope and its outputs remain in the run directory as history.
