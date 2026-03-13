# 2.engine/version06/shared/ids.py
from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone


def new_run_id() -> str:
    # Example: 2026-02-26_7f3a9c2b
    d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    r = secrets.token_hex(4)
    return f"{d}_{r}"


def new_task_id() -> str:
    # Non-deterministic baseline for phase 1.
    # Later: derive from normalized inputs for dedup.
    return secrets.token_hex(8)
