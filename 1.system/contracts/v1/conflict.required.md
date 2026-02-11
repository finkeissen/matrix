# Conflict Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** structural explicitness, not semantic resolution
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Conflict Record

A **Conflict** makes **disagreement explicit**.

Conflicts exist to:
- preserve incompatible structures without collapse,
- prevent silent normalization or forced synthesis,
- expose disagreement as a first-class, queryable artifact.

Conflicts do **not**:
- resolve contradictions,
- select winners,
- rank claims,
- assert correctness.

A conflict records the **existence of incompatibility**, nothing more.

---

## What a Conflict Is (and Is Not)

### A Conflict Is

A Conflict is:
- an explicit declaration of incompatibility,
- anchored to concrete records,
- scoped to explicit problems,
- attributable and auditable,
- append-only.

### A Conflict Is Not

A Conflict is **not**:
- a resolution mechanism,
- an evaluation,
- a meta-claim about truth,
- an implicit endorsement of any side.

---

## Record Type and Versioning (Binding)

Each conflict record is exactly one JSON object per line (JSONL).

Required:
- `record_type` MUST be `"conflict"`
- `schema_version` MUST be present (string)

Schema versioning ensures historical interpretability.

---

## Required Identifiers

### `conflict_id` (required)

- MUST be present (string).
- MUST be unique within a commit bundle.
- SHOULD be content-addressed (recommended) or explicitly versioned.

The `conflict_id` identifies the **disagreement artifact**, not its correctness.

---

## Required Conflict Scope (What Is in Conflict)

At least **two canonical records** MUST be involved.

The conflict MUST reference at least one of:

- `claim_ids` (array of strings)
- `relation_ids` (array of strings)

Binding rules:
- Across `claim_ids` and `relation_ids`, the total number of referenced records MUST be ≥ 2.
- All referenced IDs MUST resolve:
  - within the same commit bundle, or
  - in an explicitly referenced prior commit.

Conflicts MAY span:
- claim–claim,
- relation–relation,
- claim–relation

If fewer than two resolvable records are referenced, the commit MUST STOP.

---

## Required Conflict Type

### `conflict_type` (required)

- MUST be present (string).
- MUST NOT be empty.

`conflict_type` names the **kind of incompatibility**, not its outcome.

Typical examples (illustrative, non-exhaustive):
- `contradiction`
- `incompatible_assumptions`
- `competing_explanations`
- `temporal_overlap`
- `scope_mismatch`

The vocabulary is controlled but extensible.
Unknown values MAY be accepted if documented elsewhere in `1.system/`.

---

## Required Problem Anchoring

### `problem_ids` (required)

- MUST be present (array).
- MUST be non-empty.
- Each element MUST be a valid `problem_id`.

Rationale:
- Conflicts must be discoverable within problem contexts.
- Conflicts without problems are structurally orphaned.

If any referenced `problem_id` does not resolve, the commit MUST STOP.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the lifecycle of the conflict **inside the Matrix**.

Required fields:
- `introduced_in_commit` (string)
- `deprecated_in_commit` (string or null)
- `status` (string)

Allowed `status` values (v1):
- `active`
- `deprecated`

Rules:
- Conflicts are append-only.
- Deprecation records historical supersession, not resolution.

If `matrix_validity.status` is not an allowed value, the commit MUST STOP.

---

## Required Provenance Container

### `provenance` (required)

Conflicts must be attributable.

`provenance` MUST be present as an object.

Within `provenance`:

#### `extracted_by_run` (recommended)

- SHOULD be present (string).
- Identifies the MMS run that surfaced or generated the conflict.

#### `source_ids` (optional)

- MAY be present (array of strings).
- If present, every referenced `source_id` MUST resolve to a Source record.

If a provided `source_id` does not resolve, the commit MUST STOP.

---

## Optional but Supported Fields (v1)

Allowed but not required:
- `world_validity` (contextual applicability, not correctness)
- `notes` (plain-language explanation; non-canonical)

Absence of these fields MUST NOT block a canonical commit.

---

## Structural Constraints (Binding)

1. **No Implicit Conflicts**  
   Disagreement MUST be explicitly recorded.
   Tooling MUST NOT infer conflicts implicitly.

2. **No Single-Record Conflicts**  
   A conflict MUST involve at least two records.

3. **Problem-Scoped by Default**  
   Conflicts operate within explicit problem contexts.

4. **Append-Only History**  
   Conflicts are never deleted; they may only be deprecated.

---

## STOP Conditions (v1)

A canonical commit MUST STOP if any of the following holds:

- `record_type` is missing or not `"conflict"`.
- `schema_version` is missing or empty.
- `conflict_id` is missing or empty.
- fewer than two resolvable records are referenced.
- neither `claim_ids` nor `relation_ids` is present.
- any referenced record ID does not resolve.
- `conflict_type` is missing or empty.
- `problem_ids` is missing, empty, or contains unresolved IDs.
- `matrix_validity` is missing or incomplete.
- `matrix_validity.status` is not an allowed value.
- `provenance` is missing or not an object.
- any provided `provenance.source_ids[*]` does not resolve.

---

## What This Contract Does Not Enforce

This contract does **not** enforce:
- correctness of the disagreement,
- importance of the conflict,
- resolution procedures,
- prioritization of claims.

It enforces **structural explicitness only**.

---

## Minimal Valid Example (v1)

```json
{
  "record_type": "conflict",
  "schema_version": "mms.conflict@1",
  "conflict_id": "cnf:sha256:...",
  "conflict_type": "contradiction",
  "claim_ids": ["clm:sha256:a", "clm:sha256:b"],
  "problem_ids": ["prb:sha256:xyz"],
  "provenance": {
    "extracted_by_run": "run:2026-01-18T10-12Z:import01"
  },
  "matrix_validity": {
    "introduced_in_commit": "2026-01-18",
    "deprecated_in_commit": null,
    "status": "active"
  }
}

