"""
logging_setup.py — Structured JSON logging for Pipeline v18.

Every log entry is a JSON object containing at minimum:
  - timestamp (ISO 8601)
  - level
  - logger name
  - event (the message)
  - any additional keyword arguments

This enables post-run analysis with jq, log aggregators, and dashboards.

Usage:
    from pipeline.logging_setup import get_logger
    logger = get_logger(__name__)
    logger.info("step.completed", step="01_scope", counts={"generated": 12})
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing.