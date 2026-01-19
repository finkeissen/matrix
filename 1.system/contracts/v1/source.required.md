# Source Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit/*`)
- **Scope:** provenance and traceability, not authority or trust
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Source Record

A **Source** records where information comes from.

Sources do **not**:
- establish truth,
- confer authority,
- rank credibility,
- or validate claims.

They make **attribution explicit** and **traceable**.

Every canonical claim, relation, conflict, or problem
may reference sources.
Sources exist to prevent implicit authority
through unattributed assertions.

---

## What a Source Is (and Is Not)

### A Source Is

A Source is:
- a referenceable origin of information,
- human, institutional, documentary, or technical,
- stable enough to be cited over time,
- explicitly identified.

Sources function as **provenance anchors**.

---

### A Source Is Not

A Source is **not**:
- evidence of correctness,
- a guarantee of quality,
- an endorsement,
- a ranking signal,
- a proxy for truth.

Presence of a source never upgrades epistemic status.

---

## Record Type and Versioning

Each source record is exactly one JSON object per line.

Required fields:

- `record_type` MUST be `"source"`
- `schema_version` MUST be present (string)

Schema versioning ensures interpretability
across time and format changes.

---

## Required Identifier

### `source_id` (required)

- MUST be present (string).
- MUST be globally unique within the Matrix.
- SHOULD be content-addressed
  (e.g. hash of a canonical reference),
  or explicitly curated.

The `source_id` identifies the **reference**, not its reliability.

---

## Required Source Description

### `source_type` (required)

- MUST be present (string).

Examples (non-exhaustive):
- `"scientific_publication"`
- `"legal_text"`
- `"standard"`
- `"dataset"`
- `"expert_statement"`
- `"interview"`
- `"observation"`
- `"guideline"`
- `"web_resource"`

The type aids interpretation.
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

---

## Required Provenance Metadata

### `provenance` (required)

Sources themselves are also artifacts
and must be attributable.

Required structure:

- `provenance` MUST be present (object)

Within `provenance`:

- `added_by_run` SHOULD be present (string)
- `added_manually_by` MAY be present (string or identifier)

This distinguishes automated ingestion
from editorial introduction.

---

## Required Matrix Validity Metadata

### `matrix_validity` (required)

Defines the status of the source **inside the Matrix**.

Required fields:

- `introduced_in_commit` (string)
- `deprecated_in_commit` (string or null)
- `status` (string)
  - MUST be one of:
    - `"active"`
    - `"deprecated"`

Deprecation does not erase references.
It marks that the source should no longer be newly used.

---

## Optional but Supported Fields (v1)

The following fields are optional and non-binding:

### Metadata (Optional)

- `title`
- `authors`
- `publisher`
- `publication_year`
- `language`
- `jurisdiction`
- `version`
- `accessed_at`

These fields support retrieval and interpretation.
Their absence must not block a commit.

---

### World Validity (Optional)

- `world_validity` (object)

Same semantics as in other record types.
Describes applicability in the world,
not trustworthiness.

---

### Notes (Optional)

- `notes` (string)

Free-text commentary, warnings, or context.
Notes must not function as credibility judgments.

---

## Structural Constraints (Binding)

1. **No Implicit Trust**  
   Sources never imply correctness or priority.

2. **Stable Referencing**  
   A `source_id` must remain stable once introduced.

3. **Append-Only History**  
   Sources are never deleted.
   They may be deprecated.

4. **Non-Blocking Absence**  
   Claims may exist without sources,
   but source references must be explicit when present.

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

