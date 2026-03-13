# Pipeline Architecture
## Model- and Technology-Agnostic Execution Layer

### Purpose
Build a fully automatable pipeline that can be refined indefinitely while remaining stable under:
- ontology changes (Problem/Solution today, alternatives tomorrow),
- implementation changes (LLMs today, successors later),
- tightening validation policies over time.

This architecture defines **process contracts**, not truth.

---

## 1) Core execution pattern

Every pipeline step is an update module:

> `update(state, inputs, params) -> (patches, report)`

- `state` is read-only during updates.
- `patches` are append-only **events** that propose structural changes.
- `report` describes metrics, warnings, and review queues.

**Re-entry** is guaranteed because modules:
- compute stable fingerprints,
- are deterministic under declared params (or record non-determinism),
- can be rerun independently.

---

## 2) Runs vs State vs Commit

- **Runs**: append-only execution records (the provenance backbone).
- **State**: a materialized view derived from runs (queryable).
- **Commit**: integrity gate for publishing state snapshots (not a truth gate).

---

## 3) Substrate vs Ontologies

The pipeline assumes only a minimal substrate:
- Entities
- Assertions/Relations (typed)
- Evidence
- Patch Events (ops)

Ontologies are *packages* layered on top and can coexist.

---

## 4) Tracks (sub-pipelines)

Tracks are curated module sets for a purpose:
- Problems Track: build atomic problem inventory + enrich profiles.
- Solutions Track: build solution approaches + verification + link to problems.

Tracks can be added without changing the core contracts.

---

## 5) Navigation
- Normative: `UPDATE_CONTRACT.md`
- Substrate: `STATE_MODEL.md`
- Quality: `QUALITY_MODEL.md`
- Policies: `policies/`
- Track specs: `modules/`
