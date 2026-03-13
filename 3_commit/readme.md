# 3.commit — Canonical Matrix Commits  
## Goals, Constraints, and the Stable Commit Contract

---

## Purpose of This Document

This document defines the **canonical contract** for `3.commit`.

It specifies:
- the **goal** of the Matrix at commit level,
- the **rules** under which content becomes canonical,
- and the **minimum assumptions** required to keep the commit history
  interpretable, auditable, and evolvable over time.

This document is intentionally explicit and occasionally repetitive.
Redundancy is used to protect against misinterpretation,
not to optimize for brevity.

Schemas, formats, and tooling are expected to evolve.
The **commit history must remain stable, readable, and re-interpretable**.

---

## Overall Objective

The Matrix is designed so that external systems
(e.g. Elasticsearch or comparable indexing engines) can:

- index content efficiently,
- filter and aggregate it meaningfully,
- support time-aware queries,
- and enable retrieval that preserves context.

At the same time, the Matrix explicitly accepts that:

- the final schema for representing knowledge is not yet known,
- multiple schema revisions are expected,
- premature commitment to a single ontology must be avoided.

For this reason, the Matrix is built as a **stable, append-only history
of structured records (JSONL)**,
not as a finalized knowledge model.

---

## Why the Matrix Is Problem-Centered

The Matrix does not aim to store “knowledge” as isolated facts.

Facts without a problem context:
- cannot be meaningfully evaluated,
- cannot be prioritized,
- cannot be acted upon responsibly,
- and cannot be reliably retired or superseded.

In contrast, problem–solution structures:
- anchor claims to a concrete task or question,
- make relevance explicit,
- allow competing claims to coexist as alternatives,
- provide a stable unit for indexing, filtering, and responsibility assignment.

Therefore, the Matrix accepts **no general knowledge**.

> **Every claim must be anchored to at least one explicit problem.**  
> Without a problem reference, a statement has no admissible place
> in the canonical Matrix.

This is **not a philosophical preference**.
It is a **structural requirement** derived from the research-program
and applied at the level of canonical commits.

---

## Problem-First Is a Commit Rule, Not a Heuristic

### No Free-Floating Facts

A single fact in isolation is structurally weak:

- it is hard to retrieve at the right moment,
- hard to interpret (“why does this matter?”),
- hard to apply (“to which decision?”),
- easy to misuse outside its original scope.

Facts without problems are not knowledge.
They are noise with delayed consequences.

---

### No Problem, No Claim

The Matrix does not accept problem-free claims.

A record is admissible **only** if it is anchored
to at least one **Problem**.

> **No problem → no claim in the canonical Matrix.**

The Matrix is therefore a repository of
**problem-centered epistemic artifacts**,
not a universal encyclopedia.

---

## Problem Catalog and Scaling

To scale problem-centered knowledge,
the Matrix maintains an explicit catalog structure:

- ~80 domains,
- ~1,800 subdomains,
- ~100,000 problem groups,
- problems as the canonical anchors.

Important distinctions:

- domains and subdomains are **navigation and faceting scaffolding**,
- problem groups support aggregation,
- **problems are the epistemic anchors**,
- claims attach to problems, not to domains.

This avoids folder-based semantics
and keeps meaning queryable rather than implicit.

---

## Two Distinct Notions of Validity

Every canonical record exists on two validity axes:

1. **World validity**  
   When a statement, problem, or relationship
   is considered valid in reality.

2. **Matrix validity**  
   When a record is valid inside the Matrix commit history.

We aim for alignment,
but mismatches are expected due to:

- delayed ingestion,
- retrospective reconstruction,
- reinterpretation,
- conflicting sources,
- explicit editorial decisions.

Such mismatches are preserved as **explicit structure**,
not corrected or hidden.

---

## Explicit Simplifications (and Why They Are Acceptable)

The Matrix makes simplifications that are known to be imperfect:

1. **Global world validity**  
   Validity is treated as global,
   even though it is often regional or institutional.

2. **Discrete validity intervals**  
   Validity is represented via `from` / `until`,
   even when transitions are fuzzy or disputed.

3. **Atomic records**  
   Index-atomic claims are stored
   even when meaning emerges only in graphs.

4. **Stability before completeness**  
   A stable commit log is preferred
   over maximal expressiveness.

These are **engineering constraints**, not epistemic claims.
They are explicit so they can be revised later.

---

## What 3.commit Is (and Is Not)

`3.commit` contains **only canonical Matrix states**.

Everything stored here is:
- binding **inside the Matrix**,
- non-authoritative **outside the Matrix**.

A commit represents a **deliberate decision**
to include content in the canonical record.

`3.commit` is:
- not a workspace,
- not a scratchpad,
- not a raw dump.

It is the **technical point of no return**
for Matrix history.

---

## Commit Instead of “Current State”

There is no implicit “current” Matrix.

Every state exists only because
an explicit commit decision was made.

All changes are:
- traceable,
- dated,
- reproducible,
- append-only in practice.

A commit is an epistemic decision,
not a technical side effect.

---

## Temporal Organization

Commits are organized by date or commit ID,
not by domain or topic.

Example:

3.commit/
└── 2026-01-19/
└── 2026-02-03/


The past is never overwritten,
only extended.

---

## Relationship Between Runs and Commits

Commits do **not** arise implicitly.

A commit is created by **consolidating artifacts**
produced by one or more explicit runs stored under `2.runs`.

- Runs document **how** artifacts were generated.
- Commits document **which artifacts are accepted** as canonical.

A commit may consolidate:
- multiple runs from the same day,
- runs with different scopes or focuses,
- runs that produced overlapping or even conflicting artifacts.

A commit must never modify run outputs.
All consolidation is performed by **selection and aggregation**,
not mutation.

---

## Canonical Commit Directory Contract

Each commit directory follows a stable contract:

<commit-id>/
manifest.json
matrix.problems.jsonl
matrix.claims.jsonl
matrix.relations.jsonl
matrix.conflicts.jsonl
matrix.sources.jsonl

catalog.domains.jsonl
catalog.subdomains.jsonl
catalog.problem_groups.jsonl
catalog.problems.jsonl

notes.md


Catalog files may be omitted
if unchanged.
In that case, the manifest must reference
the catalog version used.

---

## Meaning of the Canonical Files

- **matrix.problems.jsonl**  
  Canonical problem records.

- **matrix.claims.jsonl**  
  Canonical claims.  
  Every claim references at least one problem.

- **matrix.relations.jsonl**  
  Structured relations between problems and claims.

- **matrix.conflicts.jsonl**  
  Explicitly represented contradictions and disputes.

- **matrix.sources.jsonl**  
  Canonical sources with provenance.

- **catalog.\***  
  Navigation scaffolding, not knowledge.

---

## Manifest Requirements

`manifest.json` must allow:

- reproduction of the commit,
- integrity verification (checksums),
- schema identification,
- traceability to MMS runs.

At minimum:
- commit ID and timestamp,
- run IDs,
- schema versions,
- checksums,
- catalog references.

---

## Notes File

`notes.md` is non-canonical.

It documents:
- motivation,
- known gaps,
- explicit non-decisions,
- intended follow-ups.

It must not introduce new canonical knowledge.

---

## Change, Identity, and Persistence

- Problems and claims are anchored by stable IDs.
- Catalog nodes use curated identifiers.
- Commits are immutable.
- Change is expressed through new records and relations
  (`supersedes`, `refines`, `splits`, `merges`).

No mutation in place.

---

## Atomicity

Claims are **index-atomic**:
- one coherent assertion per record,
- independently sourceable,
- independently time-scoped.

Solutions emerge from graphs,
not single objects.

---

## Guiding Principle

> **3.commit is where work becomes knowledge —  
> not through progress, but through deliberate commitment.**

We optimize for:
- traceability,
- retrieval,
- reinterpretation,

not for certainty.
