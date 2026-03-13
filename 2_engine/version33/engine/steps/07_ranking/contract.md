# Contract — 07_ranking

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "deduplicated_problems": [ { ...problem... } ],
  "problem_count": 30
}
```
| Field                    | Type         | Required | Source            |
|--------------------------|--------------|----------|-------------------|
| `domain`                 | string       | yes      | run param         |
| `deduplicated_problems`  | list[object] | yes      | 06_deduplication  |

## Forbidden Context
- export paths, registry mutations
- any artifact from step 08

## Operation
Score per problem:
```
score = DIFFICULTY_WEIGHTS.get(difficulty, 0) * 4 + len(problem_statement.split())
```
Where `DIFFICULTY_WEIGHTS = {expert: 4, hard: 3, medium: 2, easy: 1}`.

Sort descending by score. Preserve all fields unchanged.

## Output Schema
```json
[ { ...problem, "_rank_score": 24 }, ... ]
```
| Field         | Type         | Required |
|---------------|--------------|----------|
| (all input fields preserved) | | yes |
| `_rank_score` | int          | yes      |

## Invariants
- `len(output) == input problem_count` — no filtering in this step
- Sort is deterministic: identical input → identical order
- All input fields preserved unchanged

## Stop Conditions
| Condition               | Outcome |
|-------------------------|---------|
| Input list empty        | FAIL    |
