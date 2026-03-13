# Case Template

This directory defines the required structure for an archived case.

Each case represents a single classification decision:
the explicit determination that specific material is inadmissible.

Cases are append-only.
Once created, they must not be altered.

---

## Required files

Each case directory must contain exactly two primary files:

- `gate.md`
- `case.md`

No additional files are required.
Supporting material should be referenced, not duplicated.

---

## `gate.md`

`gate.md` contains the classification metadata.

It answers the question:
**Why is this material stopped?**

Typical contents include:

- Case identifier
- Classification date
- Status (usually `STOP`)
- Referenced failure modes
- Optional cross-references to related cases

`gate.md` is authoritative for the classification decision.

---

## `case.md`

`case.md` contains the descriptive context.

It answers the question:
**What is being archived, and under what circumstances?**

Typical contents include:

- Description of the material
- Origin and context
- Relevant excerpts or summaries
- Rationale for inadmissibility
- References to `raw/` material where applicable

`case.md` may be descriptive and narrative,
but must not argue for rehabilitation or correction.

---

## Constraints

- A case documents inadmissibility, not improvement.
- A case does not propose fixes or alternatives.
- A case does not evolve after creation.

If interpretation changes,
a new case must be created elsewhere.

---

## Naming and numbering

- Case directories are numeric and sequential.
- IDs used in `gate.md` must match the directory name.
- Gaps in numbering are permitted; reuse is not.

---

## Status

This template is normative.

All cases must conform to it.

