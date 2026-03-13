#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT_DIR="data/ap_test_runs/offline_smoke"
mkdir -p "$OUT_DIR"
python pipeline/steps/00_atomic_problem_curation.py \
  --domain thermodynamics \
  --input data/test_fixtures/subdomains_fixture.jsonl \
  --output-dir "$OUT_DIR" \
  --mode offline-template \
  --subdomains-per-call 5 \
  --atomic-per-subdomain 3 \
  --max-subdomains 25 \
  --records-per-file 1000
