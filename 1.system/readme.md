# system

The `system/` directory contains **matrix-internal system information**.

It documents **how the Matrix is structured, constrained, and managed**,
not what the Matrix claims about the world.

Nothing in `system/` establishes truth, relevance, or correctness.
Nothing in `system/` is domain knowledge.

`system/` exists to make the Matrix **auditable, inspectable, and reproducible**.

---

## Role of `system/` in the Repository

This repository distinguishes strictly between:

- `handbook/` — conceptual and explanatory documentation  
- **`system/` — matrix-internal system specification**  
- `domains/` — the current epistemic state  
- `work/` — non-normative working material  
- `runs/` — execution records  
- `exports/` — frozen external artifacts  

`system/` defines **how the Matrix works**,  
not **what the Matrix contains**.

---

## What Belongs in `system/`

The `system/` directory may contain:

- structural specifications used by MMS
- schemas for Matrix artifacts
- ID and referencing conventions
- provenance and temporality models
- conflict representation rules
- STOP conditions as system behavior
- examples illustrating system behavior
- **definitions of admissible artifact types**, including
  claims, relations, sources, and observations

All material in `system/` must satisfy:

- it is **content-agnostic**
- it applies **across domains**
- it does **not** embed domain assumptions
- it does **not** imply evaluation or prioritization

---

## What Does Not Belong in `system/`

The following must **never** appear in `system/`:

- factual claims
- empirical statements
- domain interpretations
- recommendations or conclusions
- workflow instructions for users
- decisions about relevance or correctness
- assessments of domain quality or maturity

If something depends on **what** is being claimed,
it does **not** belong in `system/`.

---

## Relationship to research-program and MMS

The Matrix system layer is **not** the source of epistemic norms.

- **research-program** defines epistemic admissibility and limits  
- **MMS** implements those constraints operatively  
- **Matrix system** documents how those implementations appear *here*

`system/` may:
- reference research-program constraints
- reference MMS behavior

It must **not**:
- redefine epistemic rules
- duplicate research-program texts
- function as a normative authority

`system/` is **derivative**, not foundational.

---

## Schemas and Specifications

Schemas in `system/schema/` define:
- admissible artifact shapes
- required metadata
- validation boundaries
- **which artifact types may be produced or referenced by runs**

Schemas exist to support:
- tooling interoperability
- reproducibility
- structural comparison

Schemas do **not**:
- define meaning
- enforce interpretation
- encode truth conditions

A schema violation is a **structural error**, not an epistemic one.

---

## Observations as System Artifacts

The system recognizes **observations** as a valid artifact type.

Observations are:
- produced only by runs
- explicitly attributable and time-bound
- descriptive of structural patterns

The system:
- permits observations to be stored and referenced
- does not interpret or evaluate observations
- does not aggregate them into judgments or scores

Any meaning derived from observations
lies outside the system layer.

---

## System Evolution

System material may evolve over time.

Changes to `system/` must be:
- explicit
- versioned
- traceable

Backward compatibility is **not guaranteed**,
but breaking changes must be visible.

Historical system states may be retained
for audit and comparison.

---

## Relationship to Runs

Runs are the **operational manifestation**
of system behavior.

A run records:
- which system version was active
- which schemas were applied
- which constraints were enforced
- which artifact types were produced

System definitions without runs are inert.
Runs without system references are invalid.

---

## Self-Reference

The system may describe:
- its own constraints
- its own limits
- its own failure modes
- its own evolution

This self-description has **no special authority**.
It is subject to the same auditability
as any other Matrix artifact.

---

## Summary

> **`system/` defines how the Matrix holds structure,
> not what the Matrix asserts.**

It exists to make the Matrix
transparent about its own mechanics —
and nothing else.

