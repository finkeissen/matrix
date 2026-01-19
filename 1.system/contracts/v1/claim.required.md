# Claim Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** structural admissibility, not semantic correctness
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Claim Record

A **Claim** represents a single articulated assertion
within a problem-centered epistemic structure.

Claims exist **only** in relation to explicit problems.
They do not stand on their own and do not assert authority or truth.

> **No problem → no claim in the canonical Matrix.**

Claims are the atomic units from which
problem–solution structures emerge through relations and conflicts.

---

## Record Type and Versioning

Each claim record is exactly one JSON object per line.

Required fields:

- `record_type` MUST be `"claim"`
- `schema_version` MUST be present (string)

Schema versioning ensures that historical commits
remain interpretable as formats evolve.

---

## Required Identifiers

### `claim_id` (required)

- Stable identifier for the claim.
- MUST be globally unique within the Matrix.
- SHOULD be content-addressed (recommended),
  or explicitly versioned if curated.

The `claim_id` identifies the **assertion**, not its truth.

---

## Required Problem Anchoring

### `problem_ids` (required)

- MUST be present as an array.
- MUST be non-empty.
- Every element MUST be a valid `problem_id`.
- Every referenced problem MUST exist
  in `matrix.problems.jsonl`
  (in the same commit or a referenced prior state).

This is a **hard structural rule**.

Claims without explicit problem references
are **inadmissible** in canonical commits.

---

## Required Claim Content

### `text` (required)

- MUST be present.
- MUST be a non-empty string.
- MUST be understandable on its own.
- SHOULD express exactly one coherent assertion
  (index-atomic).

Composite statements must be split into multiple claims.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the status of the claim **inside the Matrix**.

Required fields:

- `introduced_in_commit` (string)  
  - MUST equal the commit directory name (e.g. `"2026-01-18"`)

- `deprecated_in_commit` (string or null)

- `status` (string)  
  - MUST be one of:
    - `"active"`
    - `"deprecated"`

Notes:
- Deprecation does **not** remove history.
- Changes are expressed through:
  - new claims,
  - and explicit relations (e.g. `supersedes`).

---

## Required Provenance Container

### `provenance` (required)

Provenance is mandatory for all canonical claims.

Required structure:

- `provenance` MUST be present (object)

Within `provenance`:

- `source_ids` MUST be present (array)
  - MAY be empty
  - each element MUST be a `source_id` (string)

- `extracted_by_run` SHOULD be present (string)

Rationale:
- Even manually created claims must be explicitly attributable.
- Absence of provenance structure is **not allowed** in canonical commits.

---

## Optional but Supported Fields (v1)

The following fields are **optional** but allowed and encouraged when applicable.

### World Validity (Optional)

`world_validity` (object):

- `from` (string or null)
- `until` (string or null)
- `status` (string)  
  e.g. `"asserted"`, `"unknown"`, `"disputed"`
- `assumption` (string)  
  e.g. `"globally_uniform"`
- `precision` (string)  
  e.g. `"day"`, `"month"`, `"year"`, `"era"`

World validity describes how a claim relates to the world,
not whether it is correct.

---

### Claim Role (Optional, Controlled)

`claim_role` (string)

The role aids retrieval and interpretation.
It does not confer priority, authority, or correctness.

Recommended values (non-exhaustive):

**General:**
- `"solution_fragment"`
- `"evidence"`
- `"constraint"`
- `"assumption"`
- `"definition"`

**Knowledge navigation (Position → Target → Routing):**
- `"position"`  
  (Standortbestimmung; context / current state / situational constraints)

- `"target"`  
  (Zielbestimmung; desired outcomes, preferences, must-not constraints)

- `"option"`  
  (a candidate path / course of action)

- `"route_segment"`  
  (optional: intermediate segment of an option/path)

**Tradeoffs:**
- `"pro"`  
  (advantage / benefit claim linked to an option)

- `"con"`  
  (disadvantage / downside claim linked to an option)

- `"tradeoff"`  
  (structured tradeoff statement, e.g. cost vs risk vs time)

- `"cost"`  
  (descriptive cost; not automatically negative)

**Norms / Authorities (represented, not enforced):**
- `"norm"`  
  (a rule / norm / requirement statement)

- `"authority"`  
  (institution / issuer / interpreter statement)

Notes:
- Roles are descriptive labels for retrieval.
- A claim may be linked into navigation via relations;
  roles must never be treated as execution logic.

---

### Tags (Optional)

- `tags` (array of strings)
- MAY be empty

Used exclusively for retrieval and faceting.

---

### Entities (Reserved, Optional)

- `entities` (array)

Each entry MAY include:
- `entity_id`
- `role`

v1 does not require an entity catalog to exist.

---

### Notes (Optional)

- `notes` (string)

