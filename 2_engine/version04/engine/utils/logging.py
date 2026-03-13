"""Engine logging utilities.

The engine is designed to run entirely within a RAM-backed run directory (e.g. tmpfs)
and then be archived to SSD after completion. For that workflow to be debuggable,
we write human-readable logs directly into:

    <run_dir>/logs/engine.log

Design goals:
- no dependence on /tmp (systemd PrivateTmp may be enabled)
- logs stay with the run folder and get archived together with outputs
- safe defaults for both interactive runs and the daemon
"""

from __future__ import annotations

import logging
from pathlib import Path


def setup_run_logger(run_dir: Path) -> logging.Logger:
    """Create/configure a per-run logger that writes to run_dir/logs/engine.log."""
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_path = logs_dir / "engine.log"

    logger = logging.getLogger(f"engine.{run_dir.name}")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if called twice.
    if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "") == str(log_path) for h in logger.handlers):
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
