```md
# Matrix FORMAT

This document defines the **format of the Matrix knowledge base**.

It describes **representation only**:
- structure
- artifact types
- identifiers
- relations
- versioning
- attribution

It defines **no meaning**, **no truth**, **no correctness**,  
and has **no epistemic or normative authority**.

Interpretation, evaluation, and validation
lie **outside** the scope of this document.

---

## 1. Purpose of the Matrix Format

The Matrix is the **persistent knowledge base**
managed by the Matrix Management System (MMS).

It stores **epistemic state descriptions** produced under
the constraints of the research-program
and enforced by MMS.

This document answers one question only:

> *How does a Matrix state look when persisted?*

It does **not** answer:
- why a state exists
- whether it is good or bad
- whether it is correct
- how it should be used

---

## 2. Design Principles

The Matrix format follows these principles:

- **Explicitness**  
  No implicit fields, defaults, or inferred meaning.

- **Stability**  
  Once an artifact is written, it is never modified.

- **Referential Integrity**  
  All references are explicit and resolvable.

- **Auditability**  
  Every artifact is attributable and time-bound.

- **Extensibility**  
  New artifact types may be added
  without invalidating existing data.

---

## 3. Canonical Concepts

### 3.1 Artifact

An **artifact** is the smallest persistent unit
stored in the Matrix.

All artifacts share the following properties:

- a globally unique identifier
- a type
- an origin (Run reference)
- a creation timestamp
- immutable content

Artifacts are **append-only**.
Corrections and revisions are new artifacts.

---

### 3.2 Run Reference

Every artifact references exactly one **Run**.

A Run represents the accountable execution context
that produced the artifact.

The Matrix does not interpret Runs.
They serve attribution and audit only.

---

### 3.3 Commit Reference

A **Commit** represents the introduction of
a new global Matrix state.

Each commit:
- is produced by exactly one Run
- introduces zero or more new artifacts
- does not modify existing artifacts

Commits allow Matrix states to be referenced,
compared, and reproduced.

---

## 4. Core Artifact Types

The following artifact types are canonical.

Additional types may be introduced,
but must not violate core principles.

---

### 4.1 Claim

A **Claim** represents an explicit statement,
assertion, or description.

A Claim:
- is content-bearing
- has no implied truth value
- exists independently of agreement or conflict

Claims may contradict other claims.
This is expected and allowed.

---

### 4.2 Relation

A **Relation** explicitly links two or more artifacts.

Relations:
- are directional or non-directional
- are typed (e.g. supports, contradicts, refers-to)
- do not imply correctness or priority

Relations are artifacts themselves
and follow the same immutability rules.

---

### 4.3 Conflict

A **Conflict** represents explicit disagreement
between artifacts.

Conflicts:
- are first-class artifacts
- may persist indefinitely
- are never resolved implicitly

A Conflict documents incompatibility,
not failure.

---

### 4.4 Provenance

**Provenance artifacts** describe origin,
source, or context information.

They may include:
- authorship
- source references
- methodological context
- assumptions

Provenance does not imply reliability.

---

### 4.5 Policy (research-program)

**Policy artifacts** represent versioned
research-program definitions.

They are stored in the Matrix
to ensure transparency and historical traceability.

Policy artifacts:
- constrain admissibility
- do not assert truth
- are enforced by MMS, not interpreted

---

### 4.6 Enrichment

**Enrichment artifacts** add non-authoritative
annotations or experience.

Enrichments may:
- document failure or limitation
- mark approaches as insufficient or problematic
- compare alternatives without selection
- record empirical or practical experience

Markers such as:
- “bad”
- “failed”
- “insufficient”

are treated as **experience records**,
not judgments.

Enrichments:
- never delete or override other artifacts
- never imply consensus or correctness
- remain explicitly attributed

---

## 5. Identity and Referencing

### 5.1 Identifiers

All artifacts use globally unique identifiers.

Identifiers:
- are opaque
- are stable
- carry no semantic meaning

---

### 5.2 References

Artifacts may reference other artifacts
only by identifier.

No positional or implicit references are allowed.

---

## 6. Time and Versioning

All artifacts are time-bound at creation.

Time:
- records when an artifact was written
- does not imply temporal validity in reality

Versioning is expressed by:
- new artifacts
- explicit relations (e.g. revises, supersedes)

There is no in-place update.

---

## 7. What This Format Does *Not* Define

This document explicitly does **not** define:

- truth conditions
- correctness criteria
- ranking or scoring
- conflict resolution
- aggregation or synthesis
- user interfaces
- query semantics
- reasoning procedures

Any system requiring such behavior
must implement it **outside** the Matrix format.

---

## 8. Evolution Rules

The Matrix format may evolve under strict rules:

- new artifact types may be added
- existing artifacts are never invalidated
- backward compatibility is preferred
- history must remain interpretable

Breaking history is forbidden.

---

## 9. Summary

The Matrix format defines **how epistemic state descriptions are stored**.

It guarantees:
- persistence
- traceability
- explicit structure

It guarantees **nothing else**.

Meaning, merit, and decision
begin **outside** this format.
```

