# 00_atomic_problem_curation

## Purpose
Generate atomic problem candidates from a list of subdomains using an LLM provider
or deterministic offline template. Produces numbered JSONL candidate batches + manifest.

## Boundary
Pre-pipeline step. No upstream step dependency.
Reads from an external subdomains file and writes to `ap_candidates/` inside the run directory.

## Local flow
`domain + subdomains_file` → `00_atomic_problem_curation` → `candidate_batches`

## Runtime
```
runs/<run-id>/steps/00_atomic_problem_curation/run/
  input.json   — { "domain": "...", "subdomains_file": "...", "provider": "...",
                   "provider_config": {...}, "curation_params": {...} }
  output.json  — { "domain": "...", "subdomain_count": N, "total_candidates": N,
                   "output_dir": "...", "output_files": [...], "manifest": "..." }
  meta.json    — { "counts": {"total_candidates": N, "inserted": N, ...} }

runs/<run-id>/ap_candidates/
  <domain>_atomic_candidates_0001.jsonl
  ...
  _latest_manifest.json
```

## CLI (standalone)
```
python pipeline/steps/00_atomic_problem_curation.py \
  --domain thermodynamics \
  --input ingestion/seeds/thermodynamics_subdomains.jsonl \
  --output-dir data/runs/<run-id>/ap_candidates \
  --provider offline-template
```
