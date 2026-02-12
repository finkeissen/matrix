# INTEGRITY_CLAIMS.md

## Purpose

This document specifies the **integrity claims** made by the public Matrix repository.

Integrity claims describe what can be relied upon when inspecting, citing, or extending
the repository — and what explicitly cannot.

No integrity claim is implicit.


---

## Scope of Integrity

Integrity claims apply **only** to material that is:

- publicly visible in the repository
- explicitly included within the defined public scope
- compliant with declared admissibility and stop rules

No integrity is claimed beyond this boundary.


---

## Claimed Properties

The repository claims the following properties.


### 1. Structural Integrity

The repository guarantees that:

- normative rules are explicitly declared
- schemas, contracts, and roles are non-circular
- no file derives authority from undeclared sources
- directory structure reflects conceptual separation

Structural violations invalidate artifacts.


---

### 2. Admissibility Integrity

The repository guarantees that:

- admissibility conditions are explicit
- no artifact or run is valid by default
- violations are conceptually detectable
- stop conditions override all other considerations

Nothing bypasses admissibility.


---

### 3. Scope Integrity

The repository guarantees that:

- excluded material is not implicitly referenced
- no hidden dependency exists on private or legacy content
- public material stands on its own

Absence of material is intentional.


---

### 4. Revision Integrity

The repository guarantees that:

- public material is version-controlled
- changes are explicit and attributable
- no generated or transient artifacts are included
- scope boundaries are enforced via repository structure

Integrity is preserved across revisions.


---

## Explicit Non-Claims

The repository explicitly does **not** guarantee:

- correctness of content
- truth of claims
- empirical validity
- usefulness for any purpose
- completeness
- stability of interpretations
- fitness for decision-making

Confusing integrity with correctness is an error.


---

## Relationship to Examples and Runs

Examples and runs:

- do not extend integrity claims
- do not add authority
- do not validate the system

They are admissible demonstrations only.


---

## Failure Modes

Integrity is considered violated if:

- material outside the public scope is required for interpretation
- admissibility conditions are bypassed
- stop rules are implicitly relaxed
- explanatory material is treated as normative
- legacy or excluded material is cited as justification

Violation invalidates downstream use.


---

## Consequences for Extensions

Any extension claiming compatibility with this repository must:

1. Restate applicable integrity claims.
2. Declare any deviations explicitly.
3. Accept invalidation if integrity constraints are violated.

Silence is not compatibility.


---

## Summary

This repository guarantees **integrity of structure and constraint** — nothing else.

All other properties must be established externally and explicitly.

