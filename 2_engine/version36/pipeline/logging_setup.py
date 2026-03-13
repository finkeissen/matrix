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
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        base = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        # Merge extra fields attached by the caller
        for key, value in record.__dict__.items():
            if key not in (
                "args", "created", "exc_info", "exc_text", "filename",
                "funcName", "levelname", "levelno", "lineno", "message",
                "module", "msecs", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread",
                "threadName",
            ):
                base[key] = value
        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False, default=str)


class PipelineLogger(logging.Logger):
    """
    Logger subclass that supports structured keyword arguments.

    Usage:
        logger.info("step.completed", step="01_scope", duration_ms=1420)
    """

    def _log_structured(self, level: int, event: str, **kwargs):
        if self.isEnabledFor(level):
            record = self.makeRecord(
                self.name, level, "(structured)", 0, event, (), None
            )
            for k, v in kwargs.items():
                setattr(record, k, v)
            self.handle(record)

    def info(self, msg, *args, **kwargs):  # type: ignore[override]
        if args or not kwargs:
            super().info(msg, *args, **kwargs)
        else:
            self._log_structured(logging.INFO, msg, **kwargs)

    def error(self, msg, *args, **kwargs):  # type: ignore[override]
        if args or not kwargs:
            super().error(msg, *args, **kwargs)
        else:
            self._log_structured(logging.ERROR, msg, **kwargs)

    def warning(self, msg, *args, **kwargs):  # type: ignore[override]
        if args or not kwargs:
            super().warning(msg, *args, **kwargs)
        else:
            self._log_structured(logging.WARNING, msg, **kwargs)

    def debug(self, msg, *args, **kwargs):  # type: ignore[override]
        if args or not kwargs:
            super().debug(msg, *args, **kwargs)
        else:
            self._log_structured(logging.DEBUG, msg, **kwargs)


logging.setLoggerClass(PipelineLogger)

_configured = False
_file_handler: Optional[logging.FileHandler] = None


def configure_logging(log_file: Optional[Path] = None, level: int = logging.INFO):
    """Configure root pipeline logger. Call once at startup."""
    global _configured, _file_handler

    root = logging.getLogger("pipeline")
    root.setLevel(level)

    if not root.handlers:
        # Console handler (human-readable level + event)
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        root.addHandler(console)

    if log_file and not _file_handler:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        _file_handler = logging.FileHandler(log_file, encoding="utf-8")
        _file_handler.setLevel(level)
        _file_handler.setFormatter(JsonFormatter())
        root.addHandler(_file_handler)

    _configured = True


def get_logger(name: str) -> PipelineLogger:
    if not _configured:
    configure_logging()
    return logging.getLogger(name)  # type: ignore[return-value]


def attach_run_log(run_log_path: Path):
    """Attach a per-run log file after run directory is created."""
    configure_logging(log_file=run_log_path)
