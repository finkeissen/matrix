# Pipeline Architecture
## Model- and Technology-Agnostic Execution Layer

**Version:** 2.0.0
**Status:** Reference Architecture
**Scope:** Domain-agnostic; integrates with Grounded Intelligence Architecture

---

## Table of Contents

1. Purpose & Design Philosophy
2. Core Execution Pattern
3. Runs, State, and Commit
4. Substrate vs. Ontologies
5. Tracks (Sub-Pipelines)
6. Module Contract Specification
7. Error Handling & Failure Modes
8. Observability & Auditability
9. Extension Points
10. Navigation & Related Documents

---

## 1. Purpose & Design Philosophy

This document defines a **fully automatable, indefinitely refinable execution layer** for structured knowledge pipelines.

The architecture is designed to remain stable under three axes of change:

| Axis | Example Today | Example Tomorrow |
|------|--------------|-----------------|
| **Ontology** | Problem / Solution entities | Alternatives, Constraints, Tradeoffs |
| **Implementation** | LLM-based hypothesis generation | Symbolic reasoners, successor models |
| **Validation policy** | Permissive (warn only) | Strict (block on any violation) |

**Core invariant:** This architecture defines **process contracts**, not truth. It makes no assumptions about what is correct — only about how correctness is checked, recorded, and evolved.

### 1.1 What This Is Not

- Not a data schema: entity shapes are declared in `STATE_MODEL.md`.
- Not a validation rulebook: rules live in `policies/`.
- Not a track specification: module logic lives in `modules/`.

This document defines the **execution substrate** on which all of the above operate.

---

## 2. Core Execution Pattern

### 2.1 The Update Module

Every pipeline step is an **update module** with a single, uniform interface:

```
update(state, inputs, params) -> (patches, report)
```

| Argument | Type | Description |
|----------|------|-------------|
| `state` | read-only snapshot | The materialized state at invocation time. Never mutated in place. |
| `inputs` | typed payload | External data or outputs from an upstream module. |
| `params` | declared config | All parameters that affect behavior. Must be logged with the run. |
| `patches` | append-only events | Proposed structural changes to state. Not applied until committed. |
| `report` | structured metadata | Metrics, warnings, validation results, and review queue entries. |

### 2.2 Contracts Per Argument

**`state` (read-only):**
Modules must not modify state during execution. Side effects are expressed exclusively as patches. This enables safe parallel execution and deterministic replay.

**`patches` (append-only events):**
Patches are **proposals**, not commands. They are applied only after passing the commit integrity gate. Each patch must declare: `op` (create/update/deprecate), `entity_id`, `author` (module ID + version), `timestamp`, and `rationale`.

```json
{
  "op": "update",
  "entity_id": "PROB-00042",
  "field": "status",
  "value": "validated",
  "author": "validator-module@1.3.0",
  "timestamp": "2025-06-01T14:22:00Z",
  "rationale": "All required criteria matched. Validation report: VAL-00289."
}
```

**`report` (structured metadata):**
Reports must be machine-readable. Every report includes:

```json
{
  "module_id": "string",
  "module_version": "string",
  "run_id": "string",
  "status": "ok | warn | error | blocked",
  "metrics": {},
  "warnings": [],
  "errors": [],
  "review_queue": []
}
```

### 2.3 Re-entry Guarantee

Every module must support safe re-execution. Re-entry is guaranteed when modules:

| Property | Mechanism |
|----------|-----------|
| **Idempotent** | Running the same module twice with the same inputs produces the same patches. |
| **Fingerprinted** | Stable content hashes identify unchanged entities; already-applied patches are skipped. |
| **Deterministic** | Output is fully determined by `(state, inputs, params)`. Non-deterministic operations (e.g., LLM calls) must record their outputs as part of the run record. |
| **Independently runnable** | A module has no implicit dependency on prior module execution state beyond what is declared in its `inputs`. |

*Example:* Re-running the enrichment module after a partial failure will skip entities whose fingerprint has not changed and re-process only those that are new or stale.

---

## 3. Runs, State, and Commit

### 3.1 Definitions

| Concept | Role | Characteristics |
|---------|------|----------------|
| **Run** | Execution record | Append-only; the provenance backbone. Never deleted. |
| **State** | Materialized view | Derived from runs; queryable; rebuilt deterministically from the run log. |
| **Commit** | Integrity gate | Publishes a new state snapshot after patches pass policy checks. Not a truth gate — it enforces structural validity, not domain correctness. |

### 3.2 Run Record Schema

Each run produces an immutable record:

```json
{
  "run_id": "RUN-20250601-0042",
  "module_id": "enrichment-module",
  "module_version": "2.1.0",
  "triggered_by": "scheduler | user | upstream-module-id",
  "params": {},
  "input_fingerprint": "sha256:...",
  "state_snapshot_id": "SNAP-00189",
  "patches_proposed": 14,
  "patches_committed": 12,
  "patches_rejected": 2,
  "report": {},
  "started_at": "2025-06-01T14:00:00Z",
  "completed_at": "2025-06-01T14:03:42Z"
}
```

### 3.3 Commit Gate

The commit gate applies proposed patches to state only if:

1. The patch is structurally valid (schema check).
2. The patch does not violate active policies (declared in `policies/`).
3. The patch does not create circular dependencies or constraint violations in the substrate.

**Rejected patches** are logged with a rejection reason and queued for review. They do not block other patches in the same run.

### 3.4 State Reconstruction

State is always reconstructible from the run log:

```
state(t) = apply(∅, all_committed_patches where timestamp ≤ t)
```

This means any past state can be recovered for audit, replay, or regression testing.

---

## 4. Substrate vs. Ontologies

### 4.1 The Minimal Substrate

The pipeline assumes only four primitive types. Everything else is an ontology layer on top.

| Primitive | Description | Example |
|-----------|-------------|---------|
| **Entity** | A uniquely identified node in the knowledge graph. | `PROB-00042`, `SOL-00017` |
| **Assertion / Relation** | A typed, directed relationship between entities or between an entity and a value. | `PROB-00042 --has_solution--> SOL-00017` |
| **Evidence** | A reference to an external or internal source that supports an assertion. | `{ source: "AKU-00123", confidence: 0.95 }` |
| **Patch Event** | A proposed or committed structural change (create / update / deprecate). | See Section 2.2 |

### 4.2 Ontologies as Packages

Ontologies define **entity types, relation types, and validation rules** for a domain. They are packages layered on top of the substrate and can:

- coexist in the same pipeline instance,
- be versioned independently of the substrate,
- be added or replaced without changing the core execution contracts.

*Example:* The `grounded-intelligence-v2` ontology package defines `AKU`, `ValidationReport`, and `ClarificationRequest` entity types, plus the relations between them. The substrate does not know about these types — it only stores the generic primitives.

### 4.3 Ontology Compatibility Rules

| Scenario | Allowed? | Procedure |
|----------|----------|-----------|
| Add new entity type | Yes | Add to ontology package; no substrate change. |
| Add new relation type | Yes | Add to ontology package; no substrate change. |
| Rename existing entity type | Yes (MINOR) | Publish migration mapping; update retrieval queries. |
| Change required fields of existing type | MAJOR | Regression test required; existing entities may become invalid. |
| Remove entity type | MAJOR | Deprecate first; archive only after no active entities reference it. |

---

## 5. Tracks (Sub-Pipelines)

### 5.1 What Is a Track?

A track is a **curated, ordered set of modules** assembled for a specific purpose. Tracks operate on the same substrate and run record format. Adding a new track never changes core contracts.

### 5.2 Standard Tracks

| Track | Purpose | Key Modules |
|-------|---------|-------------|
| **Problems Track** | Build and enrich the atomic problem inventory. | ingestion, normalization, deduplication, AKU linking, profile enrichment |
| **Solutions Track** | Build solution approaches, verify them, and link to problems. | hypothesis generation, validation, conflict detection, linking, scoring |

### 5.3 Track Execution Model

```
Track Entry
    │
    ▼
Module A ──► patches_A, report_A
    │
    ▼ (state updated via commit gate)
Module B ──► patches_B, report_B
    │
    ▼ (state updated via commit gate)
  ...
    │
    ▼
Track Exit ──► summary report + review queue
```

Each module receives the **committed state** from the prior step, not the raw patches. This ensures each module operates on a consistent, validated snapshot.

### 5.4 Track-Level Report

At track exit, a summary report is produced:

```json
{
  "track_id": "problems-track",
  "track_version": "1.4.0",
  "run_ids": [],
  "entities_created": 34,
  "entities_updated": 12,
  "patches_rejected": 3,
  "review_queue_size": 5,
  "warnings": [],
  "completed_at": "2025-06-01T15:00:00Z"
}
```

### 5.5 Adding a New Track

To add a track without breaking core contracts:

1. Define the track's purpose and output entities in a new `modules/<track-name>/` directory.
2. Declare module sequence and input/output types in a `TRACK_SPEC.md`.
3. Ensure all modules implement the standard `update()` contract.
4. Register the track in the pipeline manifest.

No changes to `UPDATE_CONTRACT.md`, `STATE_MODEL.md`, or core substrate are required.

---

## 6. Module Contract Specification

### 6.1 Module Identity

Every module must declare:

```json
{
  "module_id": "string (stable, unique)",
  "module_version": "semver",
  "track": "string",
  "input_types": ["EntityType | RelationType | ..."],
  "output_patch_types": ["op:EntityType | ..."],
  "params_schema": "JSON Schema reference",
  "deterministic": true,
  "idempotent": true
}
```

### 6.2 Non-Deterministic Modules

Modules that invoke LLMs or other non-deterministic components must:

- Set `"deterministic": false` in their declaration.
- Record the raw model output (including model ID, temperature, seed if set) in the run record.
- Treat the recorded output as the canonical result for replay purposes.

This ensures that re-running a non-deterministic module in replay mode produces the same patches as the original run.

### 6.3 Module Versioning

| Increment | Trigger | Impact on Existing Runs |
|-----------|---------|------------------------|
| PATCH | Bug fix; no behavioral change | Existing run records remain valid |
| MINOR | New output fields; backward compatible | Existing run records remain valid |
| MAJOR | Breaking change to contract or output shape | Prior runs must be flagged; regression test required |

---

## 7. Error Handling & Failure Modes

### 7.1 Module-Level Failures

| Failure Type | Behavior |
|-------------|----------|
| **Input validation error** | Reject run before execution; log error; do not produce patches. |
| **Partial execution failure** | Produce patches for completed entities; log errors for failed ones; mark run as `warn`. |
| **Total execution failure** | Produce no patches; log error; mark run as `error`; trigger alert. |
| **Policy violation** | Commit gate rejects patches; log rejection reason; queue for review. |
| **Timeout** | Treat as partial failure; record entities processed; allow re-entry from last stable fingerprint. |

### 7.2 Cascade Prevention

Modules are **stateless with respect to each other**. A failure in Module B does not corrupt the state produced by Module A, because:

- Patches from each module are committed independently via the integrity gate.
- State is only updated on successful commit; partial patch sets are never partially applied.
- Re-entry from any module is safe (see Section 2.3).

### 7.3 Review Queue

Any patch or run result that requires human judgment is placed in the review queue. Review queue entries declare:

```json
{
  "entry_id": "RQ-00045",
  "run_id": "RUN-20250601-0042",
  "entity_id": "PROB-00042",
  "reason": "Deduplication confidence below threshold (0.72 < 0.80). Manual review required.",
  "suggested_action": "merge | keep-separate | investigate",
  "priority": "high | medium | low",
  "created_at": "2025-06-01T14:03:00Z"
}
```

---

## 8. Observability & Auditability

### 8.1 What Is Logged

Every run produces, at minimum:

- Full run record (Section 3.2)
- All proposed patches (accepted and rejected)
- Module report (Section 2.2)
- State snapshot ID at invocation and at commit

### 8.2 Reproducibility

A run is reproducible if and only if:

- The same module version is used.
- The same `params` are declared.
- The same `state_snapshot_id` is referenced.
- For non-deterministic modules: the recorded raw output is replayed (not re-generated).

### 8.3 Performance Targets

| Metric | Target |
|--------|--------|
| Run record write latency | < 50ms |
| State reconstruction (from full run log) | < 60s per 100k patches |
| Commit gate evaluation | < 100ms per patch |
| Review queue query | < 200ms |

---

## 9. Extension Points

The following aspects of the pipeline are explicitly designed for extension without core contract changes:

| Extension Point | How to Extend | Contract Stability |
|-----------------|--------------|-------------------|
| New entity/relation types | Add to ontology package | Core substrate unchanged |
| New validation policy | Add file to `policies/` | Core commit gate unchanged |
| New track | Add directory to `modules/` | Core execution pattern unchanged |
| New module in existing track | Add to track spec | Other modules unchanged |
| New substrate primitive type | Requires `STATE_MODEL.md` update | MAJOR; full regression required |

The last row is the only change that touches core contracts. All other extensions are additive.

---

## 10. Navigation & Related Documents

| Document | Role | Location |
|----------|------|----------|
| `UPDATE_CONTRACT.md` | Normative module contract specification | `UPDATE_CONTRACT.md` |
| `STATE_MODEL.md` | Substrate entity and relation schema | `STATE_MODEL.md` |
| `QUALITY_MODEL.md` | Quality metrics, thresholds, and scoring | `QUALITY_MODEL.md` |
| `policies/` | Active validation policies (commit gate rules) | `policies/` |
| `modules/` | Track specifications and module implementations | `modules/` |
| `GIA_v2.md` | Grounded Intelligence Architecture (knowledge layer) | `GIA_v2.md` |

**Reading order for new contributors:**

1. This document (execution substrate and contracts)
2. `STATE_MODEL.md` (what lives in state)
3. `UPDATE_CONTRACT.md` (full module contract specification)
4. `QUALITY_MODEL.md` (how quality is measured)
5. Relevant track spec in `modules/`
