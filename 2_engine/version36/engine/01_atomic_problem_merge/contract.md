# Contract — 01_atomic_problem_merge

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "input_files": ["/path/to/thermodynamics_atomic_candidates_0001.jsonl"],
  "output_dir": "/path/to/ap_store",
  "records_per_file": 1000
}
```
| Field             | Type         | Required | Source                          |
|-------------------|--------------|----------|---------------------------------|
| `domain`          | string       | yes      | run param                       |
| `input_files`     | list[string] | yes      | 00_atomic_problem_curation output_files |
| `output_dir`      | string       | no       | `<run>/ap_store`                |
| `records_per_file`| int          | no       | 1000                            |

## Forbidden Context
- 01_scope through 08_export artifacts
- Registry dedup state, validation results

## Required Input Record Fields
Each line in input_files must contain:
| Field           | Required | Notes |
|-----------------|----------|-------|
| `subdomain`     | yes      |       |
| `atomic_problem`| yes      |       |
| `problem_group` | no       | Derived from `subdomain` when absent — no records discarded |
| `domain`        | no       | Defaulted to slugified domain arg if missing |
| `ap_id`         | no       | Computed via `canonical_ap_id()` if missing |

**00→01 contract**: `00_atomic_problem_curation` does not produce `problem_group`.
`01_atomic_problem_merge` handles this by deriving `problem_group = subdomain`.
This is the canonical bridge between the two steps.

## Operation
1. Read all records from `input_files`
2. Skip records missing `subdomain`, `problem_group`, or `atomic_problem`
3. Compute `ap_id` via `canonical_ap_id()` if not present
4. Upsert into APStore (insert new / update changed / skip unchanged)
5. Rewrite numbered `ap_*.jsonl` files atomically

## Output Schema
```json
{
  "domain": "thermodynamics",
  "inserted": 270,
  "updated": 0,
  "unchanged": 0,
  "total": 270,
  "output_dir": "/path/to/ap_store",
  "output_files": ["/path/to/ap_store/ap_000001.jsonl"]
}
```

## Invariants
- `inserted + updated + unchanged == total`
- Every output record has a unique `ap_id`
- `total` == records in APStore after merge (may exceed input if store had prior data)

## Stop Conditions
| Condition                        | Outcome |
|----------------------------------|---------|
| `input_files` empty              | FAIL    |
| Any input file not found         | FAIL    |
| All records missing required fields | WARN (0 records merged, not FAIL) |
