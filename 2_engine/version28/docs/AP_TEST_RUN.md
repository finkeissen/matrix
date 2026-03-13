# AP Test Run Package

This package adds a minimal, testable atomic-problem workflow on top of `version26`.

## What is included

- `pipeline/steps/00_atomic_problem_curation.py`
  - Writes revision-friendly AP records directly into `ap_*.jsonl`
  - Supports `offline-template` mode for reproducible smoke tests
  - Supports `lmstudio` mode for a real generation run
- `pipeline/steps/01_atomic_problem_merge.py`
  - Merges one or more JSONL files into the shared AP store
- `pipeline/ap_store.py`
  - Stable `ap_id`
  - Update / merge logic
  - `1,000` records per file by default
- `scripts/run_ap_fixture_test.sh`
  - Offline smoke test
- `scripts/run_ap_lmstudio_test.sh`
  - Real LM Studio test run
- `tests/test_ap_store.py`
- `tests/test_atomic_problem_curation_workflow.py`

## AP record shape

Each record is written into a shared store and is intended to be revision-friendly.

```json
{
  "ap_id": "ap_1234abcd5678ef90",
  "domain": "thermodynamics",
  "subdomain": "open-system energy balance",
  "problem_group": "state estimation",
  "atomic_problem": "Estimate the missing state variable from a minimal consistent set of given quantities",
  "kind": "estimation",
  "tags": ["state", "consistency"],
  "status": "candidate",
  "version": 1,
  "parent_ap_id": null,
  "children_ap_ids": [],
  "created_at": "2026-03-09T00:00:00Z",
  "updated_at": "2026-03-09T00:00:00Z"
}
```

## Quick start

### 1. Offline smoke test

```bash
bash scripts/run_ap_fixture_test.sh
```

Expected outcome:
- `data/ap_test_runs/offline_smoke/ap_000001.jsonl`
- `data/ap_test_runs/offline_smoke/_latest_manifest.json`

Run the same script twice to confirm update safety.
On the second run, the manifest stats should show:
- `inserted: 0`
- `updated: 0`
- `unchanged: > 0`

### 2. LM Studio run

Start LM Studio with an OpenAI-compatible endpoint, then:

```bash
export LM_STUDIO_URL="http://localhost:1234/v1/chat/completions"
export LM_STUDIO_MODEL="your-loaded-model"
bash scripts/run_ap_lmstudio_test.sh
```

## Real input file

The workflow accepts `.jsonl`, `.json`, `.txt`, or `.zip`.
For your current session, you can point the script at the uploaded ZIP file:

```bash
python pipeline/steps/00_atomic_problem_curation.py \
  --domain thermodynamics \
  --input /mnt/data/subsubdomains-merged-dedup+medicine.jsonl.zip \
  --output-dir data/ap_test_runs/session_real_input \
  --mode offline-template \
  --max-subdomains 30
```

Switch `--mode` to `lmstudio` for the real model-backed run.

## Why this is enough for a first test run

Yes for a first AP smoke test, no for the full long-term system.
This package is enough to validate:
- shared `ap_*.jsonl` storage
- stable IDs
- update-safe reruns
- `1,000` AP per file
- a future-ready schema for later splitting

Later steps can still add:
- better merge heuristics
- near-duplicate detection
- `needs_split` promotion rules
- parent/child rewrite workflows
