# PROOF_MAP.md

## Purpose

This document provides a **reader-verifiable path** through the public repository.

It does not introduce new rules.
It only points to existing normative and explanatory material.

If a statement here conflicts with a normative document, this document is wrong.


---

## Reading Order for the Logical Proof

### Step 0 — Scope Boundary (Binding)

Read:

- `PUBLIC_SCOPE.md`

Goal:

- establish what the repository **does** and **does not** claim
- prevent category errors before inspecting any subsystem material


---

### Step 1 — Integrity Boundary (Binding)

Read:

- `INTEGRITY_CLAIMS.md`

Goal:

- identify what the repository guarantees (structure/constraints) and what it does not
- establish the conditions under which the repository may be cited


---

### Step 2 — Admissibility Boundary for Instantiation (Binding)

Read:

- `RUN_ADMISSIBILITY.md`
- `Admissibility.md`
- `Stop_Rules.md`

Goal:

- understand when an instantiation is allowed to exist as a run
- understand when processing must stop and why
- establish that rejection is a valid and expected outcome


---

### Step 3 — Normative Core (Binding)

Read:

- `foundation/README.md`
- `foundation/axioms.md`

Goal:

- identify the axioms and baseline constraints of the framework
- understand what is treated as *formal structure* (not as world-claims)


---

### Step 4 — System Contracts and Schemas (Binding)

Read:

- `1.system/contracts/v1/readme.md`
- `1.system/contracts/v1/*.required.md`
- `1.system/schema/readme.md`
- `1.system/schema/*.schema.json`

Goal:

- inspect the required fields and constraints for artifacts
- verify that artifacts are structurally checkable


---

### Step 5 — System Vocabulary and Coverage (Binding)

Read:

- `1.system/relations.vocab.md`
- `1.system/domain_coverage.md`

Goal:

- inspect the explicit vocabulary for relations
- inspect how domain coverage is expressed without importing authority


---

### Step 6 — Minimal Examples (Explanatory, Non-Binding)

Read:

- `1.system/examples/readme.md`
- `1.system/examples/artifacts/*.minimal.json`
- `1.system/examples/runs/*.minimal.json`

Goal:

- see structural admissibility in practice
- verify that examples demonstrate **form**, not truth or usefulness


---

### Step 7 — Architecture Explanations (Explanatory, Non-Binding)

Read:

- `ARCHITECTURE_OVERVIEW.md`
- `1.system/architecture/readme.md`
- selected architecture documents under `1.system/architecture/`

Goal:

- understand the separation of concerns and layers
- understand how constraints are intended to be enforced conceptually


---

## “If you only have 15 minutes”

Read:

1. `PUBLIC_SCOPE.md`
2. `INTEGRITY_CLAIMS.md`
3. `Stop_Rules.md`
4. `1.system/schema/readme.md`
5. `1.system/examples/readme.md`


---

## Non-Normative Support Material

The following documents support orientation but are not binding:

- `1.handbook/*`
- `INDEX.md`
- `FORMAT.md`
- `LEVELS_OF_ANALYSIS.md`
- `ROLES.md`
- `USE-CASE-TEMPLATE.md`

If any of these appear to introduce new constraints, treat that as an error.


---

## Summary

The public repository is inspectable as a **constraint system**:

- scope boundary
- integrity boundary
- admissibility/stop boundary
- formal core
- schema + contracts
- minimal examples

This is the complete proof surface currently published.


## Proof Surface (Public)

The public scope, integrity claims, and admissibility conditions of this repository are defined in:

- `PUBLIC_SCOPE.md`
- `INTEGRITY_CLAIMS.md`
- `RUN_ADMISSIBILITY.md`

A reader-verifiable path through the public proof surface is provided in `PROOF_MAP.md`.



