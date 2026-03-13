# integration checklist

This document provides a **structural checklist**
for integrating external material
(e.g. books, repositories, notes)
into the Matrix.

It is not a workflow prescription.
It does not mandate outcomes.
It does not define success.

Its purpose is to prevent
implicit transitions and silent assumptions.

---

## Scope of This Checklist

This checklist applies when material moves between:

- external sources → `work/`
- `work/` → `domains/`
- `domains/` → `exports/`

It does **not** apply to:
- handbook documentation
- system specifications
- architectural discussion

---

## Phase 1: External Source → Source Map

Before any content is extracted or structured:

- [ ] Is the source listed in `handbook/source-map.md`?
- [ ] Is its **role** described (influence, input, counterpoint, history)?
- [ ] Is the **scope of influence** explicitly limited?
- [ ] Are **non-adopted aspects** mentioned if relevant?

If the source is not listed,
it must not silently influence structure or content.

---

## Phase 2: External Source → `work/raw/`

When raw material is collected:

- [ ] Is it clearly placed under `work/raw/`?
- [ ] Is it explicitly marked as non-normative?
- [ ] Are licensing or access constraints noted if relevant?
- [ ] Is it clear that this material may never enter the Matrix?

Raw material is allowed to be messy.
Its only requirement is **explicit containment**.

---

## Phase 3: Raw Material → `work/exploration/`

When material is actively explored:

- [ ] Are provisional claims clearly marked as such?
- [ ] Are alternative interpretations allowed to coexist?
- [ ] Are assumptions written down, even if uncertain?
- [ ] Are unresolved questions preserved as gaps?

Exploration must not simulate structure prematurely.

---

## Phase 4: Exploration → Pre-Domain Structuring

Before anything approaches `domains/`:

- [ ] Are candidate artifacts explicitly identified?
- [ ] Is provenance recorded, even if imprecise?
- [ ] Are scopes declared or explicitly left open?
- [ ] Are potential conflicts noted, not resolved?

At this stage, structure is tentative
and remains outside the Matrix state.

---

## Phase 5: Entry into `domains/` (via Run)

No content enters `domains/` without a run.

Before a run is executed:

- [ ] Are inputs explicitly listed?
- [ ] Are system and schema versions known?
- [ ] Are STOP conditions considered?
- [ ] Is the intent of the run documented?

After a run:

- [ ] Are produced artifacts traceable to the run?
- [ ] Are surfaced conflicts preserved?
- [ ] Are gaps explicitly represented?
- [ ] Is nothing silently excluded?

If something cannot survive this phase,
it should remain in `work/`.

---

## Phase 6: Domain Presence Review

After content exists in `domains/`:

- [ ] Is its provisional status clear?
- [ ] Is provenance inspectable?
- [ ] Are conflicts visible, not collapsed?
- [ ] Are temporal attributes explicit?

Stability, if observed, is descriptive only.

---

## Phase 7: Domain → Export (Optional)

Before creating an export:

- [ ] Is the export purpose documented?
- [ ] Is the referenced run (or runs) specified?
- [ ] Is it clear that this is a snapshot, not a conclusion?
- [ ] Is downstream interpretation explicitly out of scope?

Exports must not feed back into the Matrix implicitly.

---

## Explicit Non-Checks

This checklist intentionally does **not** include:

- quality assessment
- truth evaluation
- relevance ranking
- completeness checks
- decision criteria

Those belong outside the Matrix.

---

## Summary

> **Integration is successful
> when nothing important happens implicitly.**

This checklist exists
to slow integration just enough
to preserve epistemic honesty.

