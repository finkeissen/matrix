# Commit Manifest – Required Fields (v1)

## Purpose

This document defines the **mandatory contract** for any canonical commit
under `3.commit/`.

A commit without a valid manifest is **non-canonical**.

The manifest does not justify content.
It only documents **provenance, scope, and admissibility**.

---

## Scope

This contract applies to:
- all directories under `3.commit/`
- all consolidated artefacts referenced therein
- all future commit versions unless explicitly superseded

---

## Mandatory Files

Each commit directory MUST contain:

- `manifest.json`
- `README.md` (human-readable summary)
- referenced artefact files (no loose files)

---

## Required Manifest Fields

The file `manifest.json` MUST contain the following fields.

### 1. Identity

- `commit_id`
  - unique identifier (string)
- `commit_date`
  - ISO 8601 date (`YYYY-MM-DD`)
- `commit_version`
  - semantic or incremental version label

---

### 2. Provenance (Non-Negotiable)

- `source_runs`
  - list of run identifiers (paths under `2.runs/`)
- `run_dates`
  - execution dates of referenced runs
- `run_manifests`
  - checksums or hashes of run manifests

If an artefact cannot be traced to at least one run,
the commit is invalid.

---

### 3. Foundation Compliance

- `foundation_version`
  - explicit reference (e.g. `foundation-v1`)
- `foundation_modules`
  - list of Foundation modules relied upon
- `compliance_statement`
  - declarative statement of compliance

No commit may introduce primitives
outside the referenced Foundation.

---

### 4. STOP and Gap Accounting

- `stop_events`
  - list of STOP triggers encountered (may be empty)
- `gaps_referenced`
  - list of Gap IDs or paths (may be empty)
- `rejected_items`
  - list of explicitly rejected artefacts (if any)

Absence of Gaps does **not** imply completeness.
Presence of Gaps does **not** block a commit.

---

### 5. Artefact Inventory

- `artefacts`
  - list of included artefacts with:
    - `artefact_id`
    - `type` (claim, relation, gap-reference, etc.)
    - `source_run`
    - `checksum`

No artefact may appear without checksum
and run attribution.

---

### 6. Validation Status

- `validation_status`
  - one of: `unchecked`, `partial`, `validated`
- `validation_runs`
  - list of validation runs (if any)
- `known_limitations`
  - explicit list of unresolved issues or boundaries

Validation is optional.
Silence is admissible.

---

## Forbidden Manifest Content

The manifest MUST NOT contain:

- truth claims
- recommendations
- optimization statements
- future plans
- interpretations of results

Any such content invalidates the commit.

---

## Commit Semantics (Normative)

A commit represents:
- a **consolidated snapshot** of admissible artefacts,
- selected from one or more runs,
- under explicit Foundation, STOP, and Gap constraints.

A commit does **not** represent:
- correctness,
- completeness,
- progress,
- consensus,
- endorsement.

---

## Failure Conditions

A commit MUST be rejected if:

- any required field is missing,
- any artefact lacks run provenance,
- Foundation compliance is not declared,
- STOP or Gap handling is implicit or omitted,
- checksums do not match referenced artefacts.

---

## Final Statement

A commit is valid if and only if:

> Every included artefact is traceable, admissible,
> Foundation-aligned, and STOP-aware.

Anything else is a category error.

