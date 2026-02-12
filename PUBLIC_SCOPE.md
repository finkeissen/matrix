# PUBLIC_SCOPE.md

## Purpose of this Repository

This repository publishes the **normative and structural core** of the Matrix / MMS research program.

Its purpose is **not** to provide solutions, implementations, or empirical results, but to make the **logical admissibility conditions** for such work explicit, inspectable, and contestable.

The public scope is intentionally minimal.


---

## What This Repository Claims

The repository claims **only** the following:

1. That a formally bounded system for structuring problem-related knowledge can be specified.
2. That this system can be described without:
   - implicit ontology
   - implicit epistemology
   - implicit normativity
3. That admissibility, roles, constraints, and stop conditions can be made explicit and enforced at the structural level.
4. That example artifacts can be used to demonstrate **form**, not **truth**, **correctness**, or **real-world validity**.

These claims are **structural and logical**, not empirical.


---

## What This Repository Does *Not* Claim

This repository explicitly does **not** claim:

- to describe the world
- to provide explanations, predictions, or truths
- to solve real-world problems
- to validate domains, models, or sources
- to contain implementations or executable systems
- to provide usable results for decision-making

Any interpretation beyond the explicit scope defined here is a category error.


---

## Normative vs. Explanatory Material

The repository contains different classes of material:

### Normative Material (Binding)

The following directories and documents define **binding constraints**:

- `foundation/` (core axioms only)
- `1.system/schema/`
- `1.system/contracts/`
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`
- `FORMAT.md`

Violations of these constraints invalidate artifacts or runs.


### Explanatory Material (Non-Binding)

The following materials are **non-normative** and serve explanatory purposes only:

- `1.handbook/`
- architectural overviews
- reading guides
- examples marked as `minimal`

They do not introduce new constraints and cannot override normative rules.


---

## Examples and Runs

All publicly included examples are:

- minimal
- schematic
- non-empirical
- non-authoritative

They exist solely to demonstrate **structural admissibility**.

No public example constitutes a validated solution, model, or claim about the world.


---

## Excluded Material

The following categories of material are intentionally **excluded** from the public scope:

- real or experimental runs
- workspaces and intermediate artifacts
- drafts, hypotheses, or exploratory material
- historical or legacy material
- domain-specific knowledge bases
- empirical datasets or sources

Their absence is intentional and required to preserve scope integrity.


---

## Integrity Boundary

Nothing outside the explicitly included public material:

- is implied
- is referenced implicitly
- can be used to justify interpretations of the system

The public repository must stand on its own under these constraints.


---

## Consequence for Extensions

Any future extension of the public repository must:

1. Explicitly declare its admissibility conditions.
2. Specify whether it is normative or explanatory.
3. Remain compatible with existing stop rules.
4. Accept that rejection by stop conditions is a valid outcome.

Growth without explicit admissibility is invalid.


---

## Summary

This repository proves **constraints**, not **content**.

Its value lies in the explicit limitation of what may be claimed, not in the volume of material provided.

