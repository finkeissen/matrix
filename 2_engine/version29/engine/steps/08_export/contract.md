# Contract — 08_export

## Accepted Input
- `ranked_problems` (list[problem_object], from 07_ranking)

## Rejected Input
- registry mutations, validation side-effects

## Operation
Iterate ranked_problems; write one JSON object per line to
exports/atomic_problems.jsonl.
Record ingestion path metadata in output envelope.

## Output
- `exported` (int) — number of records written
- `ingestion` (object) — seeds_dir, rules_dir, taxonomy_dir paths

## Stop Conditions
- input list empty
- export directory not writable
