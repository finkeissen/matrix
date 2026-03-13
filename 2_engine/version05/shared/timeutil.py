# 2.engine/version06/shared/timeutil.py
from __future__ import annotations

import time
from datetime import datetime, timezone


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def monotonic_ns() -> int:
    return time.monotonic_ns()
