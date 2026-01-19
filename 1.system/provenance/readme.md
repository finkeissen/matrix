# provenance

This directory documents **provenance conventions**
used within the Matrix.

Provenance records **where artifacts come from**,
not **what they mean**, **how reliable they are**,
or **what should be done with them**.

Provenance is mandatory for Matrix artifacts.

---

## Purpose of Provenance

Provenance exists to make artifacts:

- traceable
- auditable
- historically situated
- accountable to their origins

Provenance does **not** exist to:
- rank sources
- establish credibility
- infer correctness
- substitute evaluation

Knowing where something comes from
does not say anything about its validity.

---

## What Provenance Records

Provenance may include:

- source references (books, papers, datasets, notes)
- author or originator (as attribution, not authority)
- time of assertion or extraction
- extraction or transformation context
- intermediate processing steps
- run references

The level of detail may vary.
Absence of provenance is not tolerated;
imprecision is.

---

## Provenance vs. Authority

Provenance must not be mistaken for authority.

A well-documented source:
- is not more correct
- is not more important
- is not more relevant

A poorly documented source:
- is not automatically excluded
- may still be epistemically interesting

Provenance exposes origin.
Judgment lies elsewhere.

---

## Provenance and Transformation

When artifacts are transformed:

- original provenance must be preserved
- transformations must be documented
- derived artifacts must reference their inputs

Transformation must never erase origin.

Summarization, normalization, or restructuring
without traceability is a structural failure.

---

## Provenance Across Runs

Runs provide **procedural provenance**.

A run records:
- which inputs were used
- which system version applied
- which schemas were enforced
- which artifacts were produced

Artifact provenance and run provenance
complement each other.

Neither replaces the other.

---

## External Identifiers

External identifiers (ISBN, DOI, URL, etc.):

- may be recorded as provenance
- must not be treated as authoritative
- must not replace Matrix identifiers

External systems may change.
Matrix provenance records that risk explicitly.

---

## Provenance Granularity

Provenance may apply at different levels:

- artifact-level
- field-level
- relation-level

Granularity must be explicit.

Implicit inheritance of provenance
is not permitted.

---

## Provenance and Gaps

Gaps may have provenance.

For example:
- missing data due to unavailable sources
- STOP conditions reached
- unresolved contradictions

Recording why something is unknown
is as important as recording what is known.

---

## Explicit Non-Goals

Provenance conventions must not:
- encode trust models
- score sources
- imply endorsement
- resolve conflict
- justify decisions

Any such use is outside the Matrix scope.

---

## Summary

> **Provenance explains origin.
> It does not explain correctness.**

It exists to keep the Matrix
historically and structurally honest —
and nothing more.

