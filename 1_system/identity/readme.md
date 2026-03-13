# identity

This directory documents **identity and reference conventions**
used within the Matrix.

Identity defines **how artifacts are referred to**,
not **what they mean**.

Identity does not establish truth, equivalence, priority,
or persistence beyond explicit reference.

---

## Purpose of Identity in the Matrix

Identity exists to support:

- unambiguous reference
- traceability across runs
- comparison across time
- auditability of transformations

Identity does **not** exist to:
- define sameness of meaning
- enforce canonical forms
- collapse variants
- imply continuity

Two artifacts may share meaning without sharing identity.
Two artifacts may share identity without sharing meaning over time.

---

## Artifact Identity

Each artifact in the Matrix must have an explicit identifier.

An identifier:
- is opaque
- has no semantic meaning
- does not encode type, domain, or status
- does not imply persistence

Identifiers are **labels**, not descriptions.

---

## Identity vs. Equality

Identity must not be confused with equality.

- Identity answers: *“Which artifact is being referred to?”*
- Equality answers: *“Are two artifacts the same in some respect?”*

The Matrix records identity.
Any notion of equality must be explicit,
scoped, and represented as an artifact itself.

---

## Identity Across Runs

Artifacts produced in different runs:
- may reference each other
- may supersede each other
- may contradict each other

Identity does not guarantee continuity across runs.

Continuity, if relevant, must be:
- explicitly represented
- explicitly justified
- explicitly scoped

---

## Identity and Versioning

Versioning is **not implicit**.

If an artifact is revised:
- a new artifact identity may be created
- or a relation indicating revision may be added

Version semantics must never be inferred from identifiers.

---

## Identity and Domains

Artifact identity is **global across the Matrix**.

Domains:
- do not define identity
- do not own identity namespaces
- do not imply uniqueness

The same artifact may be referenced
from multiple domains without duplication.

---

## External References

External identifiers (e.g. ISBNs, DOIs, URLs):
- may be recorded as provenance
- must not be reused as Matrix identifiers
- must not be treated as authoritative anchors

External identity and Matrix identity are distinct.

---

## Explicit Non-Goals

Identity conventions must not:
- encode semantics
- imply hierarchy
- enforce lifecycle models
- simulate ontology or taxonomy

Any attempt to infer meaning from identity
is a category error.

---

## Summary

> **Identity enables reference.
> It does not enable interpretation.**

It exists to keep structure traceable
without collapsing difference or uncertainty.

