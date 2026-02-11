# Operational Core
## Runs, Time, and Validity (Binding)

---

## Status

This document is **normative**.

It defines the minimal operational substrate
required for the Matrix to function without
implicit execution logic, temporal bias,
or hidden authority.

No additional operational assumptions are permitted
outside this document.

---

## 1. Runs as the Only Source of Change

All change in the Matrix occurs **only** via runs.

There are:
- no implicit updates,
- no background processes,
- no standing interpretations.

A run is the **sole admissible mechanism** by which:
- artifacts are created,
- relations are introduced,
- observations are produced,
- lifecycle states are affected,
- STOP conditions are raised.

Anything not produced by a run
does not exist in the Matrix.

---

## 2. Minimal Run Categories (Closed Set)

Every run must declare exactly one `run_type`
from the following **closed, minimal set**:

### R_ingest
Introduce external material as artifacts
(e.g. sources, raw datasets, imported structures).

### R_construct
Construct new epistemic artifacts
(problems, claims, relations, conflicts)
from existing artifacts.

### R_compare
Compare artifacts, runs, or states.
Outputs **observations only**.
No merges, no decisions.

### R_transform
Re-express structure without semantic upgrade
(e.g. refactoring, normalization with trace,
schema migration with derivation).

### R_validate
Check structural, schema, or policy compliance.
May emit observations or STOP records.

### R_reflexive
Produce artifacts about the Matrix, MMS,
Research Program, or their limits.

### R_stop
Explicitly generate STOP records.
Does not modify other artifacts.

No additional run types are permitted.
Specialization must occur via parameters,
not via new categories.

---

## 3. Run Determinacy and Authority

Runs may be:
- deterministic,
- non-deterministic,
- human-assisted,
- tool-assisted (e.g. LLMs).

Run determinacy has **no epistemic effect**.

No run:
- grants authority,
- implies correctness,
- establishes priority,
- resolves conflicts.

Runs produce artifacts.
Interpretation remains external.

---

## 4. Time Model (Minimal and Explicit)

The Matrix distinguishes strictly between:

- **Run Time**  
  When a run was executed.

- **Artifact Validity Time**  
  When an artifact is declared applicable.

These are never identical by default.

There is:
- no implicit “now”,
- no global present,
- no automatic recency preference.

---

## 5. Validity as Scope, Not State

Temporal applicability is expressed **only** via scope.

Artifacts may declare:
- validity intervals,
- temporal constraints,
- unknown or open-ended time.

Absence of temporal scope means:
- temporal applicability is unknown,
- not universal,
- not current.

Lifecycle state does not encode time.
Time does not encode authority.

---

## 6. Temporal Conflict Admissibility

Artifacts may:
- overlap in time,
- contradict across time,
- supersede each other explicitly,
- coexist without resolution.

Temporal inconsistency is admissible.

Resolution is optional and must be explicit.

---

## 7. Versioning and Supersession

Versions express:
- structural succession,
- not improvement,
- not correction,
- not truth.

Supersession must be explicit via relations
or lifecycle events.

Later versions do not invalidate earlier ones
unless explicitly scoped to do so.

---

## 8. Queries and Time

All queries must specify temporal intent explicitly.

Admissible:
- “valid at time t”
- “produced before t”
- “active during interval i”

Forbidden:
- implicit present-tense queries,
- recency-as-relevance assumptions.

---

## 9. STOP as Temporal Boundary

STOP records may:
- halt further runs,
- block certain run types,
- restrict future transformations.

STOP does not erase history.
STOP is itself an artifact, bound in time and scope.

---

## 10. Operational Invariant (Binding)

> Nothing happens without a run.  
> Nothing applies without scope.  
> Nothing is current by default.

Operation is explicit.
Time is explicit.
Authority is nowhere implicit.

