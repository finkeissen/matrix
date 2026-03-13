# Contract — 05_validation

## Accepted Input
- `generated_problems` (list[problem_object], from 04_problem_generation)

## Rejected Input
- dedup hashes, registry state, ranking scores

## Operation
Apply schema validation, ingestion rules (failure_patterns, case_gates),
business rules, content checks, and quality checks.
Separate into accepted / rejected lists.

## Output
- `problems` (list[problem_object]) — accepted
- `rejected` (list[problem_object]) — failed with `_rejection_reason`

## Stop Conditions
- input list empty
- all problems rejected
- ingestion rule file malformed
