# domains

The `domains/` directory contains the **current, referencable epistemic state**
of the Matrix.

Material in `domains/` represents **structured epistemic artifacts**
that have passed at least one explicit transition
from exploratory work into the Matrix state.

This does **not** imply correctness, truth, stability, or consensus.

It implies **explicit structuring, explicit provenance,
and explicit responsibility boundaries**.

---

## Role of `domains/` in the Repository

This repository distinguishes strictly between:

- `work/` — exploratory, provisional, non-normative material  
- **`domains/` — the current Matrix state**  
- `runs/` — auditable execution records  
- `exports/` — frozen external snapshots  

`domains/` is the **only location**
whose contents may be referenced as
“what is currently represented in the Matrix”.

This status is **always provisional**
and may change with future runs.

---

## What a Domain Is

A domain is a **bounded epistemic stress environment**.

A domain defines:
- which kinds of claims may appear
- which relations between claims are admissible
- how uncertainty and conflict are represented
- which assumptions are explicit
- which questions are **out of scope**

Domains are **not disciplines**,
**not theories**, and **not taxonomic truths**.

They are **containers for structured disagreement**.

---

## What a Domain Is Not

A domain is **not**:
- a body of knowledge
- a collection of facts
- a consensus representation
- a decision basis
- a curriculum or ontology
- a completeness claim

Domains do **not** converge toward truth.
They converge toward **explicit structure under load**.

---

## Domain Stability and Change

Material in `domains/` may:
- be revised
- be superseded
- be contradicted
- be removed
- coexist in conflict

No domain is final.
No domain is canonical.
No domain is protected from revision.

Stability, if it exists at all,
is an **observed property across runs**,
not a design guarantee.

---

## Domain Categories (Navigation Only)

Subdirectories under `domains/`
(e.g. `natural/`, `society/`, `technology/`, `meta/`)
exist **solely for navigation and orientation**.

They do **not**:
- impose ontological commitments
- define disciplinary truth
- restrict cross-domain interaction
- encode epistemic priority

A domain may be:
- moved between categories
- referenced from multiple categories
- reorganized as the Matrix evolves

Navigation must **never be mistaken for meaning**.

---

## Internal Domain Structure (Recommended)

While not strictly enforced,
domains are expected to converge toward
a common internal structure, such as:

<domain>/
readme.md
data/
nodes.jsonl
edges.jsonl
sources.jsonl


This structure exists to support:
- auditability
- comparability
- tooling interoperability

Deviations are permitted,
but must be explicit and justified.

---

## Relationship to Runs

No domain content appears in `domains/`
without at least one corresponding **run**.

Runs document:
- how content entered the Matrix
- which constraints were active
- which conflicts were surfaced
- which assumptions were applied

Domains without runs are **invalid**.

---

## Relationship to Work

Domains do **not** absorb unfinished material.

Exploration, hypothesis generation,
and provisional structuring
must remain in `work/`.

The transition from `work/` to `domains/`:
- is not automatic
- is not uniform
- is not guaranteed

It must always be:
- explicit
- documented
- traceable

---

## Self-Reference

Domains may describe:
- the Matrix itself
- other domains
- their own limitations
- their own failure modes

There is no privileged domain.
Meta-domains have **no authority**
over non-meta domains.

---

## Summary

> **Domains are not where the Matrix decides.  
> Domains are where structure is exposed to pressure.**

They represent
the current state of structured epistemic stress —
nothing more, and nothing less.
