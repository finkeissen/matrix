# 01_atomic_problem_merge

## Purpose
Merge one or more AP candidate JSONL files into a shared APStore (numbered `ap_*.jsonl` files).
Deduplicates by `ap_id`, preserves version history via upsert.

## Boundary
Runs after 00_atomic_problem_curation (or standalone with any JSONL input).
Requires `ap_id`, `subdomain`, `problem_group`, `atomic_problem` per record.

## Local flow
`candidate_batches` → `01_atomic_problem_merge` → `ap_store`

## Runtime
```
runs/<run-id>/steps/01_atomic_problem_merge/run/
  input.json   — { "domain": "...", "input_files": [...], "output_dir": "..." }
  output.json  — { "domain": "...", "inserted": N, "updated": N, "unchanged": N,
                   "total": N, "output_dir": "...", "output_files": [...] }
  meta.json    — { "counts": {"total": N, "inserted": N, ...} }

runs/<run-id>/ap_store/
  ap_000001.jsonl
  ...
```

## CLI (standalone)
```
python pipeline/steps/01_atomic_problem_merge.py \
  --domain thermodynamics \
  --input data/runs/<run-id>/ap_candidates/thermodynamics_atomic_candidates_0001.jsonl \
  --output-dir data/ap_test_runs/thermodynamics
```
