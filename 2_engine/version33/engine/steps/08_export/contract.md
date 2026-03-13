# Contract — 08_export

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "ranked_problems": [ { ...problem... } ],
  "problem_count": 30
}
```
| Field              | Type         | Required | Source      |
|--------------------|--------------|----------|-------------|
| `domain`           | string       | yes      | run param   |
| `ranked_problems`  | list[object] | yes      | 07_ranking  |

## Forbidden Context
- registry mutations, validation side-effects
- any re-reading of upstream steps (this step is terminal)

## Operation
Iterate `ranked_problems` in order.
Write one JSON object per line to `exports/atomic_problems.jsonl`.
Build output envelope with export metadata.

## Output Schema
```json
{
  "exported": 30,
  "ingestion": {
    "seeds_dir": "/path/to/ingestion/seeds",
    "rules_dir": "/path/to/ingestion/rules",
    "taxonomy_dir": "/path/to/ingestion/taxonomy"
  }
}
```
| Field              | Type   | Required |
|--------------------|--------|----------|
| `exported`         | int    | yes      |
| `ingestion`        | object | yes      |

## Invariants
- `exported == input problem_count`
- `exports/atomic_problems.jsonl` line count == `exported`
- This step does NOT modify any problem field

## Stop Conditions
| Condition                    | Outcome |
|------------------------------|---------|
| `ranked_problems` empty      | FAIL    |
| exports/ directory not writable | FAIL |
