"""
config.py — Atomic Problem Identification Pipeline
Central configuration. Edit paths and endpoint here.
"""

from pathlib import Path

# ── LM Studio ─────────────────────────────────────────────────────────────────
LM_STUDIO_URL   = "http://localhost:1234/v1/chat/completions"
# Model is selected manually in LM Studio — we target whatever is loaded.
LM_STUDIO_MODEL = "loaded"
REQUEST_TIMEOUT = 120  # seconds per LLM call

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_INPUT = Path("/home/ef/Beruflich/GitHub/3_matrix_artifacts/2_engine/version10")
WORK_DIR   = Path("/home/ef/ram/runs")
OUTPUT_DIR = Path("/home/ef/Beruflich/GitHub/3_matrix_artifacts/2_engine/version11/data/registry")
ARCHIVE    = Path("/home/ef/Beruflich/GitHub/3_matrix_artifacts/2_engine/version11/data/runs")

SEEDS_CSV        = BASE_INPUT / "seeds" / "seed_atomare_probleme.csv"
SUBDOMAINS_JSONL = BASE_INPUT / "subdomains.jsonl"

# ── Pipeline version ───────────────────────────────────────────────────────────
PIPELINE_VERSION = "2.0.0"
SYSTEM_VERSION   = "2.0.0"

# ── Validation thresholds ──────────────────────────────────────────────────────
ATOMICITY_FAILURE_THRESHOLD = 0.20
SCOPE_CONFIDENCE_THRESHOLD  = 0.70
MAX_CLARIFICATION_ROUNDS    = 2
HALLUCINATION_SAMPLE_MAX    = 60

# ── Retry policy ───────────────────────────────────────────────────────────────
# retries = additional attempts after first failure (total calls = retries + 1)
DEFAULT_RETRIES = 1
