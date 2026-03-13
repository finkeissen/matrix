# TaskEnvelope System
## Bridging GIA Pipeline v2 and the Matrix Engine Execution Model

**Version:** 1.0.0
**Status:** Reference
**Builds on:** `pipeline_steps_v2/`, `GIA_v2.md`, Matrix Engine version06/07
**Language:** Python (runtime reference implementation)

---

## What This Is

This package defines the **TaskEnvelope execution layer** for the GIA pipeline. It is the bridge between:

- The **GIA pipeline** (what to do, in what order, with what knowledge)
- The **Matrix Engine execution model** (how work is tracked, resumed, and made reproducible)

Without this layer, the pipeline is a sequence of function calls.
With this layer, it is a **resumable, auditable, hash-verified run**.

---

## Core Invariant (inherited from Matrix Engine)

> **A run is the canonical unit of work.**
>
> Everything reproducible must exist under `runs/<date>/<run_id>/`.
> No important state lives only in memory.

---

## File Index

```
README.md                        ← this file
core/
  envelope.md                   ← TaskEnvelope schema (canonical)
  run.md                        ← Run lifecycle and directory layout
  manifest.md                   ← Manifest and artifact registry
  novelty_guard.md              ← Anti-loop / cache-hit mechanism
  content_states.md             ← Candidate → Verified → Disputed lifecycle
runtime/
  executor.md                   ← How envelopes are dispatched and completed
  resume.md                     ← Resume algorithm and skip rules
  stop.md                       ← STOP protocol and stop codes
steps/
  00_step_registry.md           ← All 14 steps as envelope definitions
  01_parsing_01_extraction.md   ← Envelope spec for this step
  01_parsing_02_confidence.md
  02_retrieval.md
  03_enrichment_01_terminology.md
  03_enrichment_02_unit_normalization.md
  03_enrichment_03_gap_detection.md
  04_hypothesis.md
  05_validation.md
  06_clarification.md
  07_examination_01_weakness_scan.md
  07_examination_02_alternative_check.md
  08_finalization.md
  09_commit.md
schemas/
  envelope.schema.json          ← JSON Schema for TaskEnvelope
  run_record.schema.json        ← JSON Schema for run state events
  manifest.schema.json          ← JSON Schema for artifact manifest
  stop_record.schema.json       ← JSON Schema for STOP records
```

---

## Design Decisions

### 1. task_id is content-addressed
`task_id = sha256(step_id + sorted(input_hashes))` — identical work always produces the same ID. This enables deduplication and safe resume without a central coordinator.

### 2. Compute type is declared, not inferred
Every envelope declares `type: deterministic | llm`. Deterministic steps run first. LLM steps are never retried more than declared in `policy.retries`.

### 3. Novelty guard before every LLM step
Before dispatching any LLM envelope, the runtime checks whether the same inputs produced a completed result in a prior run. If yes: return cached result, skip LLM call.

### 4. STOP is a valid outcome
If any step produces an unrecoverable error, the run terminates with an explicit `stop_record.json`. This is not a failure — it is a structured diagnostic.

### 5. Content state is separate from task state
A task can be `complete` while its output is still `candidate` (not yet verified). The content state lifecycle (`candidate → verified → disputed → superseded`) is tracked in the manifest, not in the envelope.

---

## Relationship to Pipeline v2

The pipeline v2 defines **what** each step does.
This envelope system defines **how** it is tracked, run, and resumed.

Every file in `pipeline_steps_v2/` has a corresponding file in `steps/` here.
The step files here are **not replacements** — they are the execution wrappers.

---

## Minimum Viable Run

A run is valid when:
1. `run_record.json` exists with `status: done | stop`
2. All completed envelopes have output hashes in `manifest.json`
3. `state.jsonl` is append-only and non-empty
4. At least one snapshot exists under `snapshots/`
