# 2.runs

This directory contains execution runs only.
Runs are diagnostic operations, not claims.
No architecture, norms, or system rules may be defined here.

Reproducible generators and validators.

A **run** represents a **single, explicit execution step**
that produces candidate artifacts which **may** enter `3.commit`.

Runs are **process artifacts**, not knowledge snapshots.

---

## Core Principle

A run is the **only legitimate producer** of canonical artifacts
that may enter `3.commit`.

- No artifact may appear in `3.commit` without being traceable to one or more runs.
- Runs are **append-only** and must never be modified retroactively.
- Errors or revisions are handled by **new runs**, not by editing old ones.

---

## What a Run Produces

Each run should output:

- a **run manifest**
  - inputs
  - tool versions
  - schema versions
  - checksums (where applicable)

- **generated JSONL artifacts**
  - problems
  - claims
  - relations
  - sources  
  (as applicable to the run scope)

- **logs**
  - warnings
  - validation results
  - extraction notes

Not every run must generate all artifact types,
but every generated artifact must be attributable to a run.

---

## Run Scope and Focus

Each run should have a **clear and narrow focus**, for example:

- position / context extraction
- target formulation
- option enumeration
- tradeoff articulation
- norm or authority extraction
- conflict or supersession detection

Runs are **not required** to be complete or consistent on their own.
They may produce partial, overlapping, or even conflicting artifacts.

---

## Run Organization

Runs are grouped by execution date:

2.runs/
└── YYYY-MM-DD/
├── run_01_<focus>/
├── run_02_<focus>/
└── run_N_<focus>/


Where:

- the numeric prefix (`run_01`, `run_02`, …) expresses **execution order**
- `<focus>` is a short, descriptive label
- ordering is **procedural**, not semantic

The execution order documents **how artifacts were produced**,
not how they should be interpreted.

---

## Relationship to Commits

- Runs explain **how** artifacts came into existence.
- Commits (`3.commit`) show **what currently constitutes a consolidated snapshot**.
- Commits may consolidate artifacts from:
  - one run
  - multiple runs
  - multiple days

A commit must **never** modify run outputs.
All consolidation happens by **selection and aggregation**, not mutation.

---

## Non-Goals

Runs are **not**:

- decision systems
- ranking or optimization mechanisms
- conflict resolution engines
- truth adjudicators
- authoritative sources

They exist solely to make artifact generation
**explicit, reproducible, and auditable**.


## Placeholder Runs and Intentional Minimality

A run may exist **without producing substantive artifacts**.

Such runs serve to:
- explicitly fix a conceptual boundary or failure mode,
- reserve architectural space for future execution,
- prevent implicit category collapse,
- document that a distinction has been identified, even if not yet executed.

Placeholder runs are **intentional**, not incomplete.

They may contain only minimal documentation (`README.md`, `stress_test.md`)
until a concrete execution is required.

The absence of generated artifacts does **not** imply that a run is invalid,
failed, or pending completion.

