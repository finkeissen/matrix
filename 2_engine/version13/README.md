# Atomic Problem Identification Pipeline
## Version 2.0.0

**Status:** Reference implementation
**Builds on:** TaskEnvelope System version09, GIA Pipeline v2
**Language:** Python (runtime reference); all outputs in English
**Decision log:** `engine.md`

---

## What This Is

This pipeline generates **atomic problems** for knowledge subdomains. For each subdomain, it produces a JSONL file of self-contained, schema-compliant problems ready for use in evaluation, training, and knowledge management systems.

An atomic problem is a single, self-contained question or task that:
- Can be posed and answered independently
- Is granular enough that it cannot be meaningfully split further
- Has a correct answer or a clear evaluation rubric

---

## Core Invariant (inherited from Matrix Engine)

> **A run is the canonical unit of work.**
> Everything reproducible must exist under `runs/<date>/<run_id>/`.
> No important state lives only in memory.

---

## File Index

```
README.md                             ← this file
engine.md                             ← decision log (read before modifying anything)
CC_BRIEFING.md                        ← original task briefing
seeds/
  seed_atomare_probleme.csv           ← subdomain priority list (153 subdomains, 3 tiers)
schema/
  atomic_problem.schema.json          ← JSON Schema draft-07 for atomic problems
schemas/
  envelope.schema.json                ← TaskEnvelope schema (v2: adds policy.model)
  manifest.schema.json                ← Artifact registry schema
  run_record.schema.json              ← Run metadata schema (v2: adds clarification_rounds)
  state_event.schema.json             ← append-only state event schema
  stop_record.schema.json             ← STOP record schema (v2: adds scope_clarification_exhausted)
core/
  envelope.md                         ← TaskEnvelope canonical spec (v2: policy.model)
  run.md                              ← Run lifecycle (v2: kb_snapshot_id semantics, clarification_rounds)
  manifest.md                         ← Artifact registry spec
  novelty_guard.md                    ← Anti-loop and cache-hit mechanism
  content_states.md                   ← Candidate → Verified → Accepted lifecycle
runtime/
  executor.md                         ← Dispatch, LLM calls, model routing (v2)
  resume.md                           ← Resume algorithm and skip rules
  stop.md                             ← STOP protocol (v2: new stop codes)
pipeline/
  00_step_registry_v2.md              ← All 15 envelopes (adapted for generative runs)
  steps/
    01_scope.md                       ← Define subdomain boundaries (Algebra)
    01_scope_confidence.md            ← Score scope clarity
    02_retrieval.md                   ← Load canonical structure
    03_enrichment_01_categories.md    ← Identify thematic clusters
    03_enrichment_02_normalize.md     ← Soft-normalize category names
    03_enrichment_03_gap_detection.md ← Detect missing categories
    04a_generation.md                 ← Generate problems per category (35b)
    04b_generation_review.md          ← Review and refine problems (122b)
    05_validation.md                  ← Schema, duplicate, atomicity checks
    06_clarification.md               ← Scope refinement loop (max 2 rounds)
    07_examination_01_hallucination_scan.md  ← Flag hallucination risks
    07_examination_02_alternative_check.md   ← Coverage and categorization review
    08_finalization.md                ← Assign IDs, produce JSONL
    09_commit.md                      ← Write to registry
registry/
  problems.jsonl                      ← All committed atomic problems (append-only)
  run_log.jsonl                       ← All runs with status (append-only)
runs/                                 ← One directory per run (created at runtime)
  <YYYY-MM-DD_NNN>/
    run_record.json
    manifest.json
    state.jsonl
    envelopes/
    artifacts/
    snapshots/
    logs/
```

---

## Design Decisions

See `engine.md` for full rationale. Key decisions:

| Decision | Choice |
|---|---|
| Generation unit | Per-category (not per-subdomain) — fits 4k context window |
| Two-stage generation | 04a (35b draft) + 04b (122b review) |
| Model routing | Step-specific: 19b / 35b / 122b per step |
| kb_snapshot_id | sha256(seeds/seed_atomare_probleme.csv) |
| Clarification exit | Max 2 rounds → STOP: scope_clarification_exhausted |
| problem_id prefix | 5-character, derived from subdomain_label |
| Category normalization | Soft only (trim, Title Case, dedup) — no synonym resolution |
| Re-run strategy | Targeted delta-run (steps 04a–09 only) every ~3 months |

---

## Minimum Viable Run

A run is valid when:
1. `run_record.json` exists with `status: done | stop`
2. All completed envelopes have output hashes in `manifest.json`
3. `state.jsonl` is append-only and non-empty
4. At least one snapshot exists under `snapshots/`
5. `registry/problems.jsonl` has been appended (for `status: done`)

---

## First Run: Algebra (SD-001)

See `pipeline/steps/01_scope.md` for the concrete, runnable first prompt.
The complete step sequence for Algebra is documented in `pipeline/00_step_registry_v2.md`.
