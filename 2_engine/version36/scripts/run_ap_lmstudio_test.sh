#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT_DIR="data/ap_test_runs/lmstudio_smoke"
mkdir -p "$OUT_DIR"
python pipeline/steps/00_atomic_problem_curation.py \
  --domain thermodynamics \
  --input /mnt/data/subsubdomains-merged-dedup+medicine.jsonl.zip \
  --output-dir "$OUT_DIR" \
  --mode lmstudio \
  --subdomains-per-call 8 \
  --atomic-per-subdomain 4 \
  --max-subdomains 24 \
  --records-per-file 1000
