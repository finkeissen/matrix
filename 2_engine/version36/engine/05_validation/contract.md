# Contract — 05_validation

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "generated_problems": [ { "title": "...", "problem_statement": "...", ... } ],
  "problem_count": 42
}
```
| Field                | Type         | Required | Source                  |
|----------------------|--------------|----------|-------------------------|
| `domain`             | string       | yes      | run param               |
| `generated_problems` | list[object] | yes      | 04_problem_generation   |

## Forbidden Context
- dedup hashes, registry state, ranking scores
- any artifact from steps 06–08

## Operation
Per problem, run in order:
1. Schema / business rules (`validate_business_rules`)
2. Content checks (`run_content_checks`)
3. Quality checks (`run_quality_checks`)
4. Ingestion rules: `failure_patterns` (text triggers), `case_gates` (STOP gates)

Problems that fail any check are moved to `rejected` with `_rejection_reason`.

## Output Schema
```json
{
  "problems": [ { ...accepted problem... } ],
  "rejected": [
    { "item": { ...problem... }, "errors": ["matched_failure_pattern:X"] }
  ]
}
```
| Field      | Type         | Required |
|------------|--------------|----------|
| `problems` | list[object] | yes (may be empty) |
| `rejected` | list[object] | yes (may be empty) |

## Invariants
- `len(problems) + len(rejected) == input problem_count`
- Every item in `rejected` has an `errors` field (non-empty list)

## Stop Conditions
| Condition                     | Outcome |
|-------------------------------|---------|
| Input list empty              | FAIL    |
| All problems rejected         | FAIL    |
| Ingestion rules file malformed| WARN (rules skipped, not FAIL) |
