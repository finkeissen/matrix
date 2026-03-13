# Contract — 07_ranking

## Accepted Input
- `deduplicated_problems` / `accepted` (list[problem_object], from 06_deduplication)

## Rejected Input
- export paths, registry writes

## Operation
Score = difficulty_weight (expert=4, hard=3, medium=2, easy=1) + word_count.
Sort descending. Preserve all fields unchanged.

## Invariants
- Input count == output count (no filtering in this step)
- Sort is deterministic for identical input

## Output
- list[problem_object] — sorted by score descending

## Stop Conditions
- input list empty
