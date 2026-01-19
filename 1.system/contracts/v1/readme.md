# Matrix Contracts — Version v1

---

## Status

- **Contract set:** v1
- **Scope:** canonical Matrix commits (`3.commit/*`)
- **Stability:** stable (v1)
- **Authority:** technical contracts only (non-epistemic)

This directory defines the **first stable contract set**
for canonical Matrix content.

v1 is considered **sufficient and complete**
to produce real Matrix commits.

---

## Purpose of v1

The purpose of **contracts/v1** is to define the **minimum required structure**
for Matrix records such that:

- content is structurally admissible,
- records are referencable and indexable,
- provenance is explicit,
- conflicts are preservable,
- and the commit history remains interpretable over time.

v1 deliberately optimizes for:
- stability,
- simplicity,
- auditability,

not for expressiveness or completeness.

---

## What v1 Does — and Does Not — Do

### v1 Does

v1 contracts:
- define **required fields** for canonical records,
- enforce **problem-centered anchoring**,
- ensure **append-only history**,
- make provenance explicit,
- keep disagreement representable,
- enable mechanical validation.

v1 is designed to **hold under real data pressure**.

---

### v1 Does Not

v1 explicitly does **not**:
- define epistemic correctness,
- rank claims or sources,
- resolve conflicts,
- enforce ontologies,
- guarantee completeness,
- prescribe workflows or tooling,
- encode domain semantics.

All evaluation, interpretation, and authority
lie **outside** the contracts.

---

## Included Record Contracts (v1)

The following record types are defined as **required** in v1:

### 1. Problem Records

- **File:** `problem.required.md`
- **Role:** epistemic anchors

Problems define:
- where epistemic work begins,
- how relevance is scoped,
- how claims, relations, and conflicts are anchored.

> Without a problem, no canonical Matrix content is admissible.

---

### 2. Claim Records

- **File:** `claim.required.md`
- **Role:** atomic assertions

Claims:
- express single assertions,
- always reference ≥ 1 problem,
- never stand on their own,
- never assert authority or truth.

---

### 3. Relation Records

- **File:** `relation.required.md`
- **Role:** explicit structural connections

Relations:
- connect problems, claims, and other artifacts,
- never introduce new claims,
- never resolve conflicts,
- preserve alternative structures.

---

### 4. Conflict Records

- **File:** `conflict.required.md`
- **Role:** preserved disagreement

Conflicts:
- make incompatibility explicit,
- prevent silent normalization,
- never select winners,
- never collapse uncertainty.

---

### 5. Source Records

- **File:** `source.required.md`
- **Role:** provenance anchors

Sources:
- record attribution,
- do not imply trust or authority,
- prevent implicit credibility assignment.

---

## Contract Scope and Enforcement

v1 contracts are enforced at **commit time**.

A commit is valid **only if**:
- all required record types conform to their contracts,
- required fields are present,
- references resolve to existing records,
- problem anchoring rules are satisfied.

Semantic correctness is **out of scope**.

---

## Relationship to Other Layers

- **research-program**  
  Defines epistemic boundaries and admissibility assumptions.

- **MMS**  
  Implements operational logic and execution.
  MMS does not define epistemic rules.

- **Matrix (this repository)**  
  Stores instantiated artifacts under these contracts.

v1 contracts do **not** override any of these layers.
They operationalize their separation.

---

## Versioning Policy

- v1 is **append-only**.
- Changes to required fields result in **v2**.
- Additions of optional fields may occur in v1.x documents,
  but must not invalidate existing commits.

Historical commits must always remain interpretable.

---

## When to Revise v1

v1 should be revised **only** if:

- real commits reveal missing required structure,
- validation cannot be performed mechanically,
- ambiguity leads to systematic misinterpretation,
- or new record types become unavoidable.

Convenience, elegance, or expressiveness
are **not sufficient reasons**.

---

## Freeze Statement

> **v1 is considered closed and ready for real Matrix commits.**

Further work should focus on:
- real data ingestion,
- real runs,
- real commit history.

Structural changes belong in v2.

---

## Guiding Statement

> **v1 defines what must exist —  
> not what must be believed.**

