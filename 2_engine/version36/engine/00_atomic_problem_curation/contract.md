# Contract — 00_atomic_problem_curation

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "subdomains_file": "/path/to/subdomains.jsonl",
  "provider": "offline-template",
  "output_dir": "/path/to/ap_candidates",
  "provider_config": {
    "model": "local-model",
    "base_url": "http://127.0.0.1:1234/v1",
    "temperature": 0.2,
    "max_tokens": 4000,
    "timeout": 120,
    "seed": 7
  },
  "curation_params": {
    "records_per_file": 1000,
    "subdomains_per_call": 12,
    "atomic_per_subdomain": 6,
    "sleep_seconds": 0.0,
    "limit_subdomains": 0
  }
}
```
| Field              | Type   | Required | Default           |
|--------------------|--------|----------|-------------------|
| `domain`           | string | yes      |                   |
| `subdomains_file`  | string | yes      |                   |
| `provider`         | string | no       | `offline-template`|
| `output_dir`       | string | no       | `<run>/ap_candidates` |
| `provider_config`  | object | no       | see defaults      |
| `curation_params`  | object | no       | see defaults      |

## Forbidden Context
- Any artifact from 01_scope through 08_export
- Pipeline validation, ranking, or dedup state

## Operation
1. Load subdomains from file (supports .jsonl / .json / .txt / .zip)
2. For each batch of subdomains, call provider (LM Studio or offline template)
3. Normalize and merge candidates with existing `output_dir` state (upsert)
4. Write numbered JSONL batch files + `_latest_manifest.json`

## Output Schema
```json
{
  "domain": "thermodynamics",
  "subdomain_count": 45,
  "total_candidates": 270,
  "inserted": 270,
  "updated": 0,
  "unchanged": 0,
  "output_dir": "/path/to/ap_candidates",
  "output_files": ["thermodynamics_atomic_candidates_0001.jsonl"],
  "manifest": "/path/to/_latest_manifest.json"
}
```

## Invariants
- `total_candidates == inserted + updated + unchanged`
- Every output record has `candidate_id`, `domain`, `subdomain`, `atomic_problem`
- Batch files are sorted by subdomain + atomic_problem

## Stop Conditions
| Condition                          | Outcome  |
|------------------------------------|----------|
| `domain` missing                   | FAIL     |
| `subdomains_file` not found        | FAIL     |
| No subdomains extracted from file  | FAIL     |
| LLM provider unreachable           | FAIL (no fallback for lm-studio) |
| `provider=offline-template`        | always succeeds deterministically |
