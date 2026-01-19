# Conflict Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** structural explicitness, not semantic resolution
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Conflict Record

Conflicts make **disagreement explicit**.

They do not:
- resolve contradictions,
- select winners,
- rank claims,
- or collapse uncertainty.

They preserve incompatibility as a first-class, queryable artifact.

Conflicts are essential to prevent implicit authority formation via:
- omission,
- forced synthesis,
- or silent normalization.

---

## Record Type and Versioning

Each conflict record is exactly one JSON object per line.

Required fields:

- `record_type` MUST be `"conflict"`
- `schema_version` MUST be present (string)

Schema versioning ensures historical interpretability across changes.

---

## Required Identifiers

### `conflict_id` (required)

- MUST be present (string).
- MUST be globally unique within the Matrix.
- SHOULD be content-addressed (recommended) or explicitly versioned.

The `conflict_id` identifies the **disagreement artifact**, not its correctness.

---

## Required Conflict Scope (What Is in Conflict)

At least one of the following fields MUST be present:

- `claim_ids` (array of strings)
- `relation_ids` (array of strings)

Binding rules:

- Across `claim_ids` and `relation_ids`, at least **two referenced records** MUST be involved.
- Referenced IDs MUST exist in the Matrix
  (within this commit or a referenced prior state).

Conflicts may span:
- claim–claim,
- relation–relation,
- claim–relation

as long as explicit references are provided.

---

## Required Conflict Type

### `conflict_type` (required)

- MUST be present (string).

Notes:
- `conflict_type` is a **controlled but extensible vocabulary**.
- Common examples include:
  - `"contradiction"`
  - `"incompatible_assumptions"`
  - `"competing_explanations"`
  - `"temporal_overlap"`
  - `"scope_mismatch"`

The type clarifies the nature of the disagreement.
It does not determine resolution.

---

## Required Problem Anchoring

### `problem_ids` (required)

- MUST be present (array).
- MUST be non-empty.
- Every element MUST be a valid `problem_id`.

Rationale:
- Conflicts must be discoverable in a problem context.
- Conflicts without problems are structurally orphaned and operationally unusable.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the status of the conflict **inside the Matrix**.

Required fields:

- `introduced_in_commit` (string)  
  - MUST equal the commit directory name (e.g. `"2026-01-18"`)

- `deprecated_in_commit` (string or null)

- `status` (string)  
  - MUST be one of:
    - `"active"`
    - `"deprecated"`

Notes:
- Conflicts may be deprecated if explicitly reframed or resolved externally.
- Deprecation does not erase historical disagreement.

---

## Required Provenance Container

### `provenance` (required)

- `provenance` MUST be present (object)

Within `provenance`:

- `extracted_by_run` SHOULD be present (string)
- `source_ids` MAY be present (array of strings)

Provenance makes the conflict attributable
even when created manually or editorially.

---

## Optional but Supported Fields (v1)

### World validity (Optional)

- `world_validity` (object)  
  - same semantics as for problems, claims, and relations

World validity describes context in the world,
not correctness or resolution.

---

### Notes (Optional)

- `notes` (string)  
  - SHOULD explain the nature of the disagreement in plain language

Notes are non-canonical explanation aids.
They must not function as implicit arbitration.

---

## Structural Constraints (Binding)

1. **No Implicit Conflict Resolution**  
   A conflict record never resolves disagreement.
   It preserves it.

2. **No Single-Record Conflicts**  
   A conflict must reference at least two records in total.

3. **Problem Context Required**  
   Conflicts must be discoverable via `problem_ids`.

4. **Append-Only History**  
   Conflicts are not deleted; they may be deprecated.

---

## What This Contract Does Not Enforce

This contract does **not** enforce:
- correctness of involved claims/relations,
- completeness of conflict coverage,
- whether a conflict is “important”,
- any resolution procedure.

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
  "problem_ids": ["prb:sha256:..."],
  "provenance": {
    "extracted_by_run": "run:2026-01-18T10-12Z:import01"
  },
  "matrix_validity": {
    "introduced_in_commit": "2026-01-18",
    "deprecated_in_commit": null,
    "status": "active"
  }
}

