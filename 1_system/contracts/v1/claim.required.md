# Claim Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** structural admissibility only
- **Authority:** technical contract (non-epistemic)

---

## Purpose of the Claim Record

A **Claim** is a single articulated assertion
expressed **within an explicit problem context**.

Claims:
- do not assert truth,
- do not confer authority,
- do not stand alone.

> **Without an explicit problem reference, a claim is inadmissible.**

Claims are the atomic assertion units
from which structure emerges through:
- relations,
- conflicts,
- scope constraints,
- provenance.

---

## What a Claim Is (and Is Not)

### A Claim Is

A Claim is:
- an explicit assertion,
- index-atomic (one coherent statement),
- problem-anchored,
- attributable,
- append-only.

Claims describe **what is being asserted**,
not whether it should be believed.

---

### A Claim Is Not

A Claim is **not**:
- a fact,
- a conclusion,
- a solution,
- an endorsement,
- a resolution of disagreement.

Claims gain structure only via explicit links.

---

## Record Type and Versioning (Binding)

Each claim record is exactly one JSON object per line (JSONL).

Required:
- `record_type` MUST be `"claim"`
- `schema_version` MUST be present (string)

Schema versioning ensures interpretability across commits.

---

## Required Identifier

### `claim_id` (required)

- MUST be present (string).
- MUST be unique within a commit bundle.
- SHOULD be content-addressed (recommended),
  or explicitly curated and versioned.

The `claim_id` identifies the **assertion**, not its correctness.

---

## Required Problem Anchoring

### `problem_ids` (required)

- MUST be present as an array.
- MUST be non-empty.
- Every element MUST be a valid `problem_id`.

Rules:
- Every referenced problem MUST resolve
  within the same commit or a referenced prior commit.
- Claims without problem anchoring MUST NOT appear
  in canonical commits.

This rule is **non-negotiable**.

---

## Required Claim Content

### `text` (required)

- MUST be present.
- MUST be a non-empty string.
- MUST be understandable without external context.
- MUST express exactly one coherent assertion.

Composite or conjunctive statements MUST be split
into multiple claims.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the lifecycle of the claim **inside the Matrix**.

Required fields:
- `introduced_in_commit` (string)
- `deprecated_in_commit` (string or null)
- `status` (string)

Allowed `status` values (v1):
- `active`
- `deprecated`

Rules:
- Claims are append-only.
- Changes are expressed via:
  - new claims,
  - and explicit relations (e.g. `supersedes`).

If `matrix_validity.status` is invalid, the commit MUST STOP.

---

## Required Provenance Container

### `provenance` (required)

All canonical claims MUST be attributable.

`provenance` MUST be present as an object.

Within `provenance`:

#### `source_ids` (required)

- MUST be present as an array.
- MAY be empty.
- Each entry MUST be a valid `source_id`.

If a provided `source_id` does not resolve,
the commit MUST STOP.

#### `extracted_by_run` (recommended)

- SHOULD be present (string).
- Identifies the MMS run that introduced the claim.

Manual claims MUST still include the `provenance` container.

---

## Optional but Supported Fields (v1)

The following fields are optional and non-binding.

### World Validity (Optional)

`world_validity` (object):

- `from` (string or null)
- `until` (string or null)
- `status` (string; e.g. `asserted`, `unknown`, `disputed`)
- `assumption` (string)
- `precision` (string)

World validity describes applicability in the world,
not correctness or acceptance.

---

### Claim Role (Optional, Controlled Vocabulary)

`claim_role` (string)

Roles are **descriptive labels only**.
They MUST NOT be interpreted as execution logic.

Recommended values (non-exhaustive):

- `assumption`
- `definition`
- `evidence`
- `constraint`
- `solution_fragment`

Navigation-oriented roles:
- `position`
- `target`
- `option`
- `route_segment`

Tradeoff-related roles:
- `pro`
- `con`
- `tradeoff`
- `cost`

Norm-representing roles (descriptive only):
- `norm`
- `authority`

---

### Tags (Optional)

- `tags` (array of strings)

Used only for retrieval and faceting.

---

### Entities (Reserved, Optional)

- `entities` (array)

May include:
- `entity_id`
- `role`

v1 does not require an entity registry to exist.

---

### Notes (Optional)

- `notes` (string)

Non-canonical commentary.
Notes MUST NOT function as hidden evaluation.

---

## Structural Constraints (Binding)

1. **No Free-Floating Claims**  
   Every claim MUST reference ≥ 1 problem.

2. **No Implicit Authority**  
   Claims never assert truth or priority.

3. **Append-Only History**  
   Claims are never modified in place.

4. **Explicit Structure Only**  
   All structure must be represented via records,
   not inferred.

---

## STOP Conditions (v1)

A canonical commit MUST STOP if any of the following holds:

- `record_type` is missing or not `"claim"`.
- `schema_version` is missing or empty.
- `claim_id` is missing or empty.
- `problem_ids` is missing, empty, or contains unresolved IDs.
- `text` is missing or empty.
- `matrix_validity` is missing or incomplete.
- `matrix_validity.status` is not an allowed value.
- `provenance` is missing or not an object.
- `provenance.source_ids` is missing or not an array.
- any provided `source_id` does not resolve.

---

## What This Contract Does Not Enforce

This contract does **not** enforce:
- correctness,
- importance,
- usefulness,
- completeness,
- resolution of disagreement.

It enforces **structural admissibility only**.

---

## Minimal Valid Example (v1)

```json
{
  "record_type": "claim",
  "schema_version": "mms.claim@1",
  "claim_id": "clm:sha256:...",
  "problem_ids": ["prb:sha256:xyz"],
  "text": "Policy A reduces short-term emissions but increases long-term costs.",
  "provenance": {
    "source_ids": ["src:doi:10.1234/example"],
    "extracted_by_run": "run:2026-01-18T10-12Z:analysis01"
  },
  "matrix_validity": {
    "introduced_in_commit": "2026-01-18",
    "deprecated_in_commit": null,
    "status": "active"
  }
}

