# schema

This directory contains **formal schemas**
used to describe and validate Matrix artifacts.

Schemas define **structure and constraints**.
They do **not** define meaning, interpretation, or truth.

Their purpose is to make artifacts:
- machine-readable
- structurally comparable
- auditable across runs

---

## Role of Schemas in the Matrix

Schemas operate at the **lowest normative level** of the Matrix.

They specify:
- required fields
- admissible data types
- minimal structural relationships

They do **not** specify:
- semantic interpretation
- epistemic validity
- correctness or relevance
- domain meaning

Schemas constrain **form**, not **content**.

---

## Relationship to Other Layers

Schemas in this directory:

- implement constraints defined elsewhere
- are consumed by MMS
- are referenced by runs

They do **not**:
- redefine research-program rules
- replace MMS logic
- impose domain semantics

Schemas are **derivative**, not foundational.

---

## Scope of Schema Enforcement

Schema enforcement applies to:
- artifacts written to `domains/`
- run manifests in `runs/`
- exports derived from validated states

Schema enforcement does **not** apply to:
- `work/` material
- handbook documentation
- external source material

This separation is intentional.

---

## Types of Schemas

This directory may contain schemas for:

- **Artifact structures**  
  (claims, relations, conflicts, gaps, metadata)

- **Run manifests**  
  (inputs, outputs, system versions, constraints)

- **Domain-local extensions**  
  (additional fields required by a specific domain)

The presence of a schema does **not** mandate its universal use.
Domains may extend schemas explicitly.

---

## Schema Evolution

Schemas are expected to evolve.

Changes to schemas must be:
- explicit
- versioned
- traceable

Backward compatibility is **not guaranteed**.

Schema changes may invalidate older artifacts.
Such invalidation must be visible, not silent.

---

## Schema Violations

A schema violation indicates:
- a structural error
- an incomplete artifact
- a mismatch between expectations and representation

It does **not** indicate:
- epistemic error
- incorrectness
- falsehood

Structural failure and epistemic failure
are intentionally distinct.

---

## Explicit Non-Goals

Schemas must not:
- encode domain meaning
- enforce terminology
- collapse heterogeneity
- optimize for convenience
- simulate ontology

Any attempt to use schemas
to standardize interpretation
is a misuse.

---

## Summary

> **Schemas keep structure honest.
> They do not make content correct.**

They exist to support comparison,
auditability, and evolution —
and nothing else.

