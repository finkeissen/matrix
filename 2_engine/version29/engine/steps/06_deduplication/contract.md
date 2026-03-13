# Contract — 06_deduplication

## Accepted Input
- `validated_problems` (list[problem_object], from 05_validation)
- registry `index.json` (optional, read-only)

## Rejected Input
- ranking scores, export paths

## Operation
Level 1 — exact SHA1 hash match against registry.
Level 2 — normalized text comparison.
Level 3 — semantic dedup (opt-in via SEMANTIC_DEDUP_ENABLED env).
Write rejected duplicates to rejected/duplicates.json.

## Output
- `accepted` (list[problem_object])
- `rejected_exact`, `rejected_normalized`, `rejected_semantic` (lists)
- `counts` (object with per-level tallies)

## Stop Conditions
- input list empty
- registry index.json malformed
