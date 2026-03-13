"""
config.py v2.1 — Portable configuration via environment variables or .env file.

Priority: environment variable -> .env file -> default value

Copy .env.example to .env and edit for your setup.
"""

import os
from pathlib import Path

# Load .env if present
_ENV_FILE = Path(__file__).parent / ".env"
if _ENV_FILE.exists():
    with open(_ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

def _get(key, default):
    return os.environ.get(key, default)

def _path(key, default):
    return Path(_get(key, default))

# LM Studio
LM_STUDIO_URL   = _get("LM_STUDIO_URL",   "http://localhost:1234/v1/chat/completions")
LM_STUDIO_MODEL = _get("LM_STUDIO_MODEL", "loaded")
REQUEST_TIMEOUT = int(_get("REQUEST_TIMEOUT", "120"))

# Paths — defaults are relative to pipeline directory for portability
_PIPELINE_ROOT = Path(__file__).parent
BASE_INPUT = _path("BASE_INPUT", str(_PIPELINE_ROOT / "data" / "input"))
WORK_DIR   = _path("WORK_DIR",   str(_PIPELINE_ROOT / "data" / "runs"))
OUTPUT_DIR = _path("OUTPUT_DIR", str(_PIPELINE_ROOT / "data" / "registry"))
ARCHIVE    = _path("ARCHIVE",    str(_PIPELINE_ROOT / "data" / "archive"))

SEEDS_CSV        = _path("SEEDS_CSV",        str(BASE_INPUT / "seeds" / "seed_atomare_probleme.csv"))
SUBDOMAINS_JSONL = _path("SUBDOMAINS_JSONL", str(BASE_INPUT / "subdomains.jsonl"))

# Thresholds
ATOMICITY_FAILURE_THRESHOLD = float(_get("ATOMICITY_FAILURE_THRESHOLD", "0.20"))
SCOPE_CONFIDENCE_THRESHOLD  = float(_get("SCOPE_CONFIDENCE_THRESHOLD",  "0.70"))
MAX_CLARIFICATION_ROUNDS    = int(_get("MAX_CLARIFICATION_ROUNDS",      "2"))
HALLUCINATION_SAMPLE_MAX    = int(_get("HALLUCINATION_SAMPLE_MAX",       "60"))
DEFAULT_RETRIES             = int(_get("DEFAULT_RETRIES",                "1"))
