# Relation Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** structural admissibility (not semantic correctness)
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Relation Record

A **Relation** is an explicit, typed connection between two or more canonical Matrix records.

Relations:
- do **not** introduce new claims,
- do **not** resolve disagreements,
- do **not** transfer authority.

They exist to:
- make structure explicit (no implicit inference),
- preserve parallel structures without collapse,
- encode refinement, dependency, contradiction, or linkage,
- enable graph-based retrieval under explicit problem contexts.

Relations describe **structure**, not truth.

---

## What a Relation Is (and Is Not)

### A Relation Is

A Relation is:
- explicit (never inferred),
- typed (relation kind is named),
- scoped (anchored to one or more problems),
- attributable (provenance exists),
- append-only (never mutated in place).

### A Relation Is Not

A Relation is **not**:
- a new claim,
- a conclusion,
- a ranking or endorsement,
- a conflict resolution,
- an implicit solution.

---

## Record Type and Versioning (Binding)

Each relation record is exactly one JSON object per line (JSONL).

Required:
- `record_type` MUST be `"relation"`
- `schema_version` MUST be present (string)

`schema_version` ensures historical interpretability.

---

## Required Identifiers

### `relation_id` (required)

- Stable identifier for this relation instance.
- MUST be unique within a commit bundle.
- SHOULD be content-addressed (recommended),
  or explicitly versioned if curated.

The `relation_id` identifies the **connection**, not its correctness.

---

## Required Endpoints

### `from_ids` (required)

- MUST be present as an array.
- MUST be non-empty.
- Each element MUST be a valid record ID
  (e.g., problem_id, claim_id, source_id, conflict_id, etc.),
  as permitted by the system contracts.

### `to_ids` (required)

- MUST be present as an array.
- MUST be non-empty.
- Each element MUST be a valid record ID.

Relations MAY be:
- one-to-one,
- one-to-many,
- many-to-many.

Endpoints MUST resolve either:
- within the same commit bundle, or
- in an explicitly referenced prior state (as defined by the commit contract).

If any referenced endpoint cannot be resolved, the commit MUST STOP.

---

## Required Relation Type

### `relation_type` (required)

- MUST be a non-empty string.
- MUST be selected from a controlled vocabulary.

The controlled vocabulary is defined here:
- `1.system/relations.vocab.md` (or the canonical equivalent path)

Typical relation types (illustrative, non-exhaustive):
- `supports`
- `contradicts`
- `refines`
- `supersedes`
- `depends_on`
- `answers`
- `is_variant_of`

Relation type makes intended semantics explicit,
but does not enforce correctness.

If `relation_type` is not in the controlled vocabulary, the commit MUST STOP.

---

## Required Problem Anchoring

### `problem_ids` (required)

- MUST be present as an array.
- MUST be non-empty.
- Each element MUST be a valid `problem_id`.

**Problem consistency rule (v1):**
At least one `problem_id` in the relation MUST be shared with
at least one endpoint record (directly or via the endpoint’s own problem anchoring rules),
to prevent cross-problem leakage and implicit global structure.

If problem anchoring cannot be established, the commit MUST STOP.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the lifecycle of the relation inside the Matrix.

Required fields:
- `introduced_in_commit` (string)
- `deprecated_in_commit` (string or null)
- `status` (string)

Allowed `status` values (v1):
- `active`
- `deprecated`

Append-only rule:
- relations MUST NOT be modified in place,
- changes are expressed by adding a new record and/or setting deprecation metadata.

If `matrix_validity.status` is not one of the allowed values, the commit MUST STOP.

---

## Required Provenance Container

### `provenance` (required)

Relations must be attributable.

`provenance` MUST be present as an object.

Within `provenance`:

#### `source_ids` (required)

- MUST be present as an array.
- MAY be empty (v1 allows editorial/structural relations without a directly cited source).
- If non-empty, every referenced `source_id` MUST resolve to a Source record.

If any `source_id` does not resolve, the commit MUST STOP.

#### `extracted_by_run` (recommended)

- SHOULD be present as a string.
- If the relation is produced by an MMS run, this SHOULD identify that run.

If absent, the relation is treated as editorial/manual.

---

## Optional but Supported Fields (Non-Required in v1)

Allowed but not required:
- `confidence` (uncertainty of the relation itself)
- `notes` (free-text explanation; non-canonical)
- `directionality` (`directed` / `undirected`)
- `scope_constraints` (additional applicability limits)

Absence of these fields MUST NOT block a canonical commit.

---

## Structural Constraints (Binding)

1. **No Implicit Relations**  
   Relations MUST be explicitly recorded.
   Tooling MUST NOT infer relations and treat them as canonical.

2. **No Authority Transfer**  
   Relations do not elevate or validate endpoint records.

3. **Problem-Scoped by Default**  
   Relations MUST operate inside explicit problem contexts.
   Cross-problem linking must be explicit and justified through shared anchoring.

4. **Immutability (Append-only)**  
   Relations are never modified in place.
   Supersession is expressed via new records and/or lifecycle metadata.

---

## STOP Conditions (v1)

A canonical commit MUST STOP if any of the following holds:

- `record_type` is missing or not `"relation"`.
- `schema_version` is missing or empty.
- `relation_id` is missing or empty.
- `from_ids` is missing, not an array, or empty.
- `to_ids` is missing, not an array, or empty.
- any endpoint ID in `from_ids` or `to_ids` does not resolve.
- `relation_type` is missing/empty or not in the controlled vocabulary.
- `problem_ids` is missing, not an array, or empty.
- any `problem_id` does not resolve.
- problem anchoring cannot be established for the relation.
- `matrix_validity` is missing or incomplete.
- `matrix_validity.status` is not an allowed value.
- `provenance` is missing or not an object.
- `provenance.source_ids` is missing or not an array.
- any `provenance.source_ids[*]` does not resolve.

---

## What This Contract Does Not Enforce

This contract does **not** enforce:
- correctness of the relation,
- appropriateness of the relation type,
- logical consistency across the graph,
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

