# exports

The `exports/` directory contains **frozen, externally consumable snapshots**
derived from the Matrix state.

Exports are **representations**, not extensions, of the Matrix.

They exist to support:
- inspection
- communication
- comparison
- external use

They do **not** modify the Matrix
and do **not** feed back into it automatically.

---

## Role of `exports/` in the Repository

This repository distinguishes strictly between:

- `domains/` — the current Matrix state  
- `runs/` — execution records and provenance  
- **`exports/` — frozen representations**  

Exports provide **stable reference points**
in an otherwise evolving system.

They allow external systems and readers
to interact with the Matrix
without participating in its internal dynamics.

---

## What an Export Is

An export is a **snapshot**.

It captures:
- a specific Matrix state
- at a specific point in time
- under a specific set of assumptions
- produced by a specific run or run set

Exports may include:
- subsets of domains
- transformed representations
- filtered or projected views
- serialized artifacts

Exports do **not**:
- resolve uncertainty
- remove conflict
- imply endorsement
- establish truth

They merely **freeze structure temporarily**.

---

## Relationship to Runs

Every export must be traceable
to one or more **runs**.

An export without a run reference
is structurally invalid.

Runs explain:
- how the exported state was produced
- which constraints were active
- which system version applied

Exports without provenance
are indistinguishable from arbitrary publications.

---

## Relationship to Domains

Exports are **derived from domains**,
but they are **not domains themselves**.

Domains may continue to evolve
after an export is created.

An export does not:
- protect domains from revision
- establish a canonical version
- override later structural changes

Exports are **read-only artifacts**.

---

## Intended Use

Exports may be used for:
- reporting
- discussion
- comparison across time
- integration with external systems
- archival purposes

Any interpretation, evaluation,
or decision-making based on an export
occurs **outside the responsibility**
of the Matrix architecture.

---

## Export Stability

Exports are immutable once published.

If an export is superseded,
this is represented by:
- creating a new export
- documenting the relationship

Historical exports are retained
for transparency and auditability.

---

## Summary

> **Exports make the Matrix visible.
> They do not make it authoritative.**

They provide stability for observation —
not conclusions, decisions, or truth.

