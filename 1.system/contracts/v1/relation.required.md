# Relation Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** structural admissibility, not semantic correctness
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Relation Record

A **Relation** represents an explicit, typed connection
between two or more canonical Matrix records.

Relations do not introduce new claims.
They make existing structure explicit.

Relations are required to:
- express how claims, problems, and other artifacts are connected,
- preserve alternative structures without collapse,
- document disagreement, refinement, or dependency,
- enable graph-based retrieval without implicit inference.

Relations never assert truth or priority.
They describe **structure**, not validity.

---

## What a Relation Is (and Is Not)

### A Relation Is

A Relation is:
- an explicit statement that two or more records are related,
- typed to make the nature of the relationship explicit,
- directional or non-directional as declared,
- independent of correctness or acceptance.

Relations function as **epistemic connectors**.

---

### A Relation Is Not

A Relation is **not**:
- a new claim,
- a conclusion,
- a ranking or preference,
- a resolution of conflict,
- an implicit solution.

Relations must never be interpreted as endorsement.

---

## Record Type and Versioning

Each relation record is exactly one JSON object per line.

Required fields:

- `record_type` MUST be `"relation"`
- `schema_version` MUST be present (string)

Schema versioning ensures historical interpretability.

---

## Required Identifiers

### `relation_id` (required)

- Stable identifier for the relation.
- MUST be globally unique.
- SHOULD be content-addressed,
  or explicitly versioned if curated.

The `relation_id` identifies the **connection**, not its correctness.

---

## Required Endpoints

### `from_ids` (required)

- MUST be present as a non-empty array.
- Each element MUST be a valid record ID
  (problem_id, claim_id, or other supported record type).

### `to_ids` (required)

- MUST be present as a non-empty array.
- Each element MUST be a valid record ID.

Relations may be:
- one-to-one,
- one-to-many,
- many-to-many.

Endpoints must exist in the same commit
or in a referenced prior state.

---

## Required Relation Type

### `relation_type` (required)

- MUST be a non-empty string.
- MUST be selected from a controlled vocabulary
  defined in `1.system/relations.vocab.md`
  (or equivalent).

Typical examples (non-exhaustive):
- `supports`
- `contradicts`
- `refines`
- `supersedes`
- `depends_on`
- `answers`
- `is_variant_of`

The relation type makes semantics explicit
but does not enforce interpretation.

---

## Required Problem Anchoring

### `problem_ids` (required)

- MUST be present as an array.
- MUST be non-empty.
- Every element MUST be a valid `problem_id`.

At least one problem referenced by the relation
MUST overlap with the problems of the linked records.

This prevents:
- cross-problem leakage,
- implicit global structure,
- accidental synthesis across unrelated contexts.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the status of the relation **inside the Matrix**.

Required fields:

- `introduced_in_commit` (string)
- `deprecated_in_commit` (string or null)
- `status` (string)
  - MUST be one of:
    - `"active"`
    - `"deprecated"`

Relations follow the same append-only rules as claims.

---

## Required Provenance Container

### `provenance` (required)

Relations must be attributable.

Required structure:

- `provenance` MUST be present (object)

Within `provenance`:

- `source_ids` MUST be present (array)
  - MAY be empty
- `extracted_by_run` SHOULD be present (string)

Manual or editorial relations
must still be explicitly attributable.

---

## Optional but Supported Fields (v1)

The following fields are optional:

- `confidence`  
  (expressed uncertainty of the relation itself)

- `notes`  
  (free-text, non-canonical explanation)

- `directionality`  
  (`"directed"` / `"undirected"`)

- `scope_constraints`  
  (additional applicability limits)

Absence of these fields must not block a commit.

---

## Structural Constraints (Binding)

1. **No Implicit Relations**  
   Relations must be explicitly recorded.
   They must not be inferred by tooling.

2. **No Authority Transfer**  
   Relations do not elevate the status of linked records.

3. **Problem Consistency**  
   Relations must remain within explicit problem contexts.

4. **Immutability**  
   Relations are never modified in place.
   Change is expressed via new relations.

---

## What This Contract Does Not Enforce

This contract does **not** enforce:
- correctness of the relation,
- appropriateness of the relation type,
- logical consistency,
- conflict resolution.

It enforces **structural explicitness only**.

---

## Minimal Valid Example (v1)

```json
{
  "record_type": "relation",
  "schema_version": "mms.relation@1",
  "relation_id": "rel:sha256:...",
  "from_ids": ["clm:sha256:abc"],
  "to_ids": ["clm:sha256:def"],
  "relation_type": "contradicts",
  "problem_ids": ["prb:sha256:xyz"],
  "provenance": {
    "source_ids": [],
    "extracted_by_run": "run:2026-01-18T10-12Z:import01"
  },
  "matrix_validity": {
    "introduced_in_commit": "2026-01-18",
    "deprecated_in_commit": null,
    "status": "active"
  }
}

