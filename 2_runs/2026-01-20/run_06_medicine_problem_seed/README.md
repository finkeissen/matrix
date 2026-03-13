# run_06_medicine_problem_seed

**Purpose**: Seed the Matrix with an initial **problem-first** medical slice (100–300 target; this run provides 120) suitable for structural testing (navigation, facets, drift/regression), **not** for medical advice or factual correctness.

## What this run does
- Produces a set of **problem records** in the medical domain.
- Uses ICD-11 classification material only as **seed provenance**, transforming it into **problem statements** (classification boundaries, ambiguity, scope, conflicts, uncertainty).

## What this run does NOT do
- No diagnosis, triage, treatment guidance, or action recommendations.
- No claim resolution, ranking, or “best answer”.
- No attempt at completeness or coverage.

## Outputs
- `problems.jsonl` — 120 problem records (problem-centric anchors)
- `sources.jsonl` — provenance anchors for the seed material and protocol
- `claims.jsonl`, `relations.jsonl`, `conflicts.jsonl` — present but intentionally empty for this seed phase

## Notes
- Problems are phrased to allow multiple competing claims later.
- Conflicts are expected to be introduced in subsequent runs when claims/relations are instantiated.
