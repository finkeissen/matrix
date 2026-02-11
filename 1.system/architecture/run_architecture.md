# Run Architecture

## Status

This document is **normative**.

It defines the role of runs as the sole
operational mechanism of the Matrix.

All detailed run semantics are delegated to:
- operational_core.md
- run manifest schemas
- run examples

---

## 1. Runs as Operational Units

Runs are the only admissible units of execution.

They:
- create artifacts,
- introduce relations,
- produce observations,
- affect lifecycle state,
- emit STOP records.

There are no background processes.

---

## 2. No Semantic Authority

Runs do not:
- assert truth,
- establish relevance,
- resolve conflict,
- grant priority.

Run outputs are artifacts, nothing more.

---

## 3. Delegation

This document defines **only the role** of runs.

All operational constraints, run types,
and temporal semantics are defined in:

- `operational_core.md`

This document must remain small and stable.

