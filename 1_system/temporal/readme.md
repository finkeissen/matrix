# temporal

This directory documents **temporal conventions**
used within the Matrix.

Temporal structure records **when artifacts exist, change, or are referenced**.
It does not imply progress, improvement, decay, or correctness.

Time in the Matrix is descriptive, not evaluative.

---

## Purpose of Temporal Representation

Temporal representation exists to make:

- historical context explicit
- change traceable
- coexistence of versions visible
- revision non-destructive

Temporal structure prevents:
- silent overwriting
- implicit updates
- loss of historical states

---

## Time Is Not Progress

The Matrix does **not** assume that:
- newer artifacts are better
- later runs are improvements
- revisions are corrections
- recency implies relevance

Temporal ordering records **sequence**, not value.

---

## Temporal Attributes

Artifacts may be associated with temporal attributes such as:

- time of assertion
- time of extraction
- time of transformation
- time of run execution
- time of snapshot creation

Temporal attributes must be explicit.
Implicit temporal inference is not permitted.

---

## Coexistence Across Time

Artifacts from different times may:
- coexist without replacement
- contradict each other
- refer to the same external source
- apply to different temporal scopes

Temporal coexistence is a **normal state**.

Supersession, if relevant, must be represented explicitly.

---

## Revision and Supersession

Revision is not implicit.

If an artifact revises or supersedes another:
- this relationship must be explicitly represented
- the earlier artifact remains preserved
- the scope of revision must be stated

Deletion is not a valid substitute for revision.

---

## Temporal Scope vs. Artifact Time

Artifact time must not be confused with scope.

- Artifact time answers: *“When was this asserted or recorded?”*
- Temporal scope answers: *“When does this claim apply?”*

These are independent dimensions
and must be represented separately.

---

## Temporal Relations

Temporal relations between artifacts
(e.g. precedes, follows, overlaps)
may be represented explicitly.

Such relations:
- describe ordering or overlap
- do not imply causality
- do not imply dependence

---

## Temporal Boundaries and STOP Conditions

STOP conditions may be temporal.

Examples include:
- lack of data beyond a certain date
- methodological limits tied to time
- explicit historical cutoffs

Temporal STOP conditions
must be documented as such.

---

## Runs and Time

Runs record procedural time.

A run captures:
- when it occurred
- under which system state
- producing which artifacts

Runs do not retroactively alter time
of previously recorded artifacts.

---

## Snapshots and Time

Snapshots freeze a Matrix state
at a specific moment.

They do not:
- halt further evolution
- privilege that moment
- define a canonical timeline

Snapshots exist for comparison, not authority.

---

## Explicit Non-Goals

Temporal conventions must not:
- enforce version numbers
- imply lifecycle stages
- encode maturity models
- suggest convergence over time

Any such interpretation
lies outside the Matrix scope.

---

## Summary

> **Time in the Matrix records sequence and context.
> It does not imply improvement or truth.**

Temporal structure exists
to preserve history without privileging it.

