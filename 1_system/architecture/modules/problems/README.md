# Problems Track (v2)

## Objective
1) Generate a **complete inventory** of atomic problems from legacy domain knowledge.
2) Enrich each atomic problem into a structured profile (symptoms, causes, consequences, constraints, tests).
3) Prepare stable linking targets for solutions.

## Phases
- **Phase A — Inventory**: coverage-first (list everything, even if shallow).
- **Phase B — Enrichment**: precision-first (fill schema, attach evidence, add tests).

## Critical design points
- ProblemCandidate subtype prevents semantic upgrades.
- Atomization uses explicit **split protocol** (no history loss).
- Completeness is governed by policy (`policies/completeness.md`).

## Files
- `inventory.md`
- `atomize.md`
- `dedup.md`
- `enrichment.md`
- `quality.md`
- `schemas.md`
