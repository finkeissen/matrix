# Contract — 06_deduplication

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "validated_problems": [ { ...problem... } ],
  "problem_count": 35
}
```
| Field                 | Type         | Required | Source        |
|-----------------------|--------------|----------|---------------|
| `domain`              | string       | yes      | run param     |
| `validated_problems`  | list[object] | yes      | 05_validation |

## Forbidden Context
- ranking scores, export paths
- any artifact from steps 07–08

## External State (read-only)
- `data/registry/problems/index.json` — known hashes + normalized forms (optional)

## Operation
Level 1 — Exact: SHA1 hash match against registry `hashes` set.
Level 2 — Normalized: lowercase + stripped + regex-cleaned match against registry `normalized` set.
Level 3 — Semantic: embedding cosine similarity (only if `SEMANTIC_DEDUP_ENABLED=true`).

Rejected problems written to `rejected/duplicates.json`.

## Output Schema
```json
{
  "accepted": [ { ...problem... } ],
  "rejected_exact": [ { ...problem... } ],
  "rejected_normalized": [ { ...problem... } ],
  "rejected_semantic": [ { ...problem... } ],
  "counts": {
    "input": 35,
    "accepted": 30,
    "rejected_exact": 2,
    "rejected_normalized": 2,
    "rejected_semantic": 1
  }
}
```

## Invariants
- `counts.accepted + counts.rejected_exact + counts.rejected_normalized + counts.rejected_semantic == counts.input`
- No item appears in both `accepted` and any rejected list

## Stop Conditions
| Condition                       | Outcome   |
|---------------------------------|-----------|
| `validated_problems` empty      | FAIL      |
| Registry index.json malformed   | WARN (registry skipped) |
