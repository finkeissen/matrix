"""Doctor/diagnostics report for the local installation."""
from __future__ import annotations
import shutil
from pathlib import Path
from .smoke_tests import run_smoke_tests

def run_diagnostics(config) -> dict:
    smoke = run_smoke_tests(config)
    usage = shutil.disk_usage(config.data_dir if Path(config.data_dir).exists() else Path('.'))
    return {
        'smoke': smoke,
        'paths': {
            'data_dir': str(config.data_dir),
            'runs_dir': str(config.runs_dir),
            'prompts_dir': str(config.prompts_dir),
            'schema_dir': str(config.schema_dir),
        },
        'disk': {'total': usage.total, 'used': usage.used, 'free': usage.free},
        'telemetry_enabled': config.telemetry_enabled,
    }
