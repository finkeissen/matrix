# Problems Track: Inventory Modules (Phase A)

## A1) `problems/update_problem_seed`
Create `ProblemCandidate` records from legacy sources.

**Outputs**
- `ProblemCandidate` with required `subtype`
- evidence pointers (source excerpts)

**Re-entry**
- fingerprint over normalized excerpt + subtype + params

---

## A2) `problems/update_problem_atomize`
Convert candidates into atomic `Problem` records using atomization rules (see `atomize.md`).

---

## A3) `problems/update_problem_identity`
Resolve same/similar/supersedes relations (see `dedup.md`).

---

## A4) `problems/update_inventory_publish`
Materialize navigation artifacts (indexes, status) from current atomic set.
