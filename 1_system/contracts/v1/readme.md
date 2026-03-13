# Matrix Contracts — Version v1

---

## Status

- **Contract set:** v1
- **Scope:** canonical Matrix commits (`3.commit/*`)
- **Stability:** closed and stable
- **Authority:** technical contracts only (non-epistemic)

This directory defines the **first complete and closed contract set**
for canonical Matrix content.

v1 is considered **sufficient and complete**
to produce real, auditable Matrix commits.

---

## Purpose of v1

The purpose of **contracts/v1** is to define the **minimum required structure**
for Matrix records such that:

- content is structurally admissible,
- records are referencable and indexable,
- provenance is explicit and auditable,
- disagreement can be preserved without collapse,
- commit history remains interpretable over time.

v1 deliberately optimizes for:
- stability,
- simplicity,
- mechanical validation,
- long-term interpretability,

not for expressiveness, elegance, or epistemic ambition.

---

## What v1 Does — and Does Not — Do

### What v1 Does

v1 contracts:
- define **required fields** for canonical records,
- enforce **problem-centered anchoring**,
- mandate **append-only history**,
- require explicit provenance,
- preserve conflicts as first-class artifacts,
- enable deterministic validation at commit time.

v1 is designed to **survive real-world data pressure**.

---

### What v1 Does Not Do

v1 explicitly does **not**:
- define truth or correctness,
- rank claims or sources,
- resolve conflicts,
- enforce ontologies or taxonomies,
- guarantee completeness,
- prescribe workflows or tooling,
- encode domain semantics.

All evaluation, interpretation, and authority
lie **outside the contract layer**.

---

## Included Record Contracts (v1)

The following record types are **required** in v1.
Each is defined in a dedicated contract file.

---

### 1. Problem Records

- **File:** `problem.required.md`
- **Role:** epistemic anchors

Problems define:
- where epistemic work begins,
- how relevance is scoped,
- how all other records are anchored.

> Without an explicit problem, no canonical Matrix content is admissible.

---

### 2. Claim Records

- **File:** `claim.required.md`
- **Role:** atomic assertions

Claims:
- express single, index-atomic assertions,
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
- never resolve disagreement,
- preserve alternative structures explicitly.

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
- record attribution and traceability,
- do not imply trust, quality, or authority,
- prevent implicit credibility assignment.

---

## Contract Scope and Enforcement

v1 contracts are enforced **at commit time**.

A commit is valid **only if**:
- all required record types conform to their contracts,
- all required fields are present,
- all references resolve to existing records,
- problem anchoring rules are satisfied,
- STOP conditions are not triggered.

Semantic correctness is explicitly **out of scope**.

---

## Relationship to Other Layers

These contracts operate within a larger architecture:

- **Research Program**  
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
- Optional-field extensions MAY occur in v1.x,
  but MUST NOT invalidate existing commits.

Historical commits must always remain interpretable.

---

## Revision Criteria

v1 should be revised **only** if:

- real commits reveal missing required structure,
- validation cannot be performed mechanically,
- ambiguity leads to systematic misinterpretation,
- or new record types become unavoidable.

Convenience, elegance, or expressiveness
are **not sufficient reasons** for revision.

---

## Freeze Statement

> **v1 is closed and ready for real Matrix commits.**

Further work should focus on:
- real data ingestion,
- real MMS runs,
- real commit history.

Structural changes belong in v2.

---

## Guiding Statement

> **v1 defines what must exist —  
> not what must be believed.**

