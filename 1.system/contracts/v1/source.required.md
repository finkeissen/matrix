# Source Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** provenance and traceability only
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Source Record

A **Source** records **where information comes from**.

Sources exist to:
- make attribution explicit,
- preserve traceability,
- prevent implicit authority through unattributed assertions.

Sources do **not**:
- establish truth,
- confer authority,
- rank credibility,
- validate claims,
- imply correctness.

A source answers **“where did this come from?”**, nothing more.

---

## What a Source Is (and Is Not)

### A Source Is

A Source is:
- a referenceable origin of information,
- human, institutional, documentary, or technical,
- stable enough to be cited over time,
- explicitly identified and addressable.

Sources function as **provenance anchors**.

---

### A Source Is Not

A Source is **not**:
- evidence of correctness,
- a measure of quality,
- an endorsement,
- a trust signal,
- a proxy for truth.

The presence of a source never upgrades epistemic status.

---

## Record Type and Versioning (Binding)

Each source record is exactly one JSON object per line (JSONL).

Required:
- `record_type` MUST be `"source"`
- `schema_version` MUST be present (string)

Schema versioning ensures interpretability across time.

---

## Required Identifier

### `source_id` (required)

- MUST be present (string).
- MUST be unique within a commit bundle.
- SHOULD be content-addressed (recommended),
  or explicitly curated.

The `source_id` identifies the **reference**, not its reliability or authority.

---

## Required Source Description

### `source_type` (required)

- MUST be present (string).
- MUST NOT be empty.

Examples (illustrative, non-exhaustive):
- `scientific_publication`
- `legal_text`
- `standard`
- `dataset`
- `expert_statement`
- `interview`
- `observation`
- `guideline`
- `web_resource`

The type aids classification.
It does not imply hierarchy or trust.

---

### `reference` (required)

- MUST be present (string).
- MUST be sufficient to identify the source unambiguously.

Examples:
- DOI
- ISBN
- URL
- court decision identifier
- dataset accession number
- institutional document ID

If a reference cannot be resolved or identified, the source MUST NOT be introduced.

---

## Required Provenance Container

### `provenance` (required)

Sources themselves are Matrix artifacts
and must be attributable.

`provenance` MUST be present as an object.

Within `provenance`:

#### `added_by_run` (recommended)

- SHOULD be present (string).
- Identifies the MMS run that introduced the source.

#### `added_manually_by` (optional)

- MAY be present (string or identifier).
- Used for editorial or manual introduction.

At least one of `added_by_run` or `added_manually_by`
SHOULD be present to avoid orphan sources.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the lifecycle of the source **inside the Matrix**.

Required fields:
- `introduced_in_commit` (string)
- `deprecated_in_commit` (string or null)
- `status` (string)

Allowed `status` values (v1):
- `active`
- `deprecated`

Rules:
- Sources are append-only.
- Deprecation prevents new use but preserves history.

If `matrix_validity.status` is not an allowed value, the commit MUST STOP.

---

## Optional but Supported Fields (v1)

The following fields are optional and non-binding:

### Descriptive Metadata (Optional)

- `title`
- `authors`
- `publisher`
- `publication_year`
- `language`
- `jurisdiction`
- `version`
- `accessed_at`

These fields aid retrieval and interpretation.
Their absence MUST NOT block a commit.

---

### World Validity (Optional)

- `world_validity` (object)

Describes contextual applicability in the world.
It does not express trust or correctness.

---

### Notes (Optional)

- `notes` (string)

Free-text commentary or warnings.
Notes MUST NOT function as credibility judgments.

---

## Structural Constraints (Binding)

1. **No Implicit Authority**  
   Sources never imply correctness, priority, or trust.

2. **Stable Referencing**  
   A `source_id` MUST remain stable once introduced.

3. **Append-Only History**  
   Sources are never deleted; they may be deprecated.

4. **Reference Integrity**  
   If a source is referenced by another record,
   the referenced `source_id` MUST resolve.

---

## STOP Conditions (v1)

A canonical commit MUST STOP if any of the following holds:

- `record_type` is missing or not `"source"`.
- `schema_version` is missing or empty.
- `source_id` is missing or empty.
- `source_type` is missing or empty.
- `reference` is missing or empty.
- `provenance` is missing or not an object.
- `matrix_validity` is missing or incomplete.
- `matrix_validity.status` is not an allowed value.

---

## What This Contract Does Not Enforce

This contract does **not** enforce:
- source quality,
- credibility,
- relevance,
- completeness,
- ranking or preference.

It enforces **traceability only**.

---

## Minimal Valid Example (v1)

```json
{
  "record_type": "source",
  "schema_version": "mms.source@1",
  "source_id": "src:doi:10.1234/example",
  "source_type": "scientific_publication",
  "reference": "https://doi.org/10.1234/example",
  "provenance": {
    "added_by_run": "run:2026-01-18T10-12Z:import01"
  },
  "matrix_validity": {
    "introduced_in_commit": "2026-01-18",
    "deprecated_in_commit": null,
    "status": "active"
  }
}

