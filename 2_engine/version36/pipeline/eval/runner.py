from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io_utils import find_latest_run, load_run_artifacts


@dataclass
class EvalRunResult:
    returncode: int
    stdout: str
    stderr: str
    run_dir: str | None
    manifest: dict[str, Any]
    metrics: dict[str, Any]
    run_health: dict[str, Any]
    summary_report: dict[str, Any]


def execute_pipeline_run(
    *,
    domain: str,
    run_cmd_template: str,
    runs_dir: Path,
    extra_env: dict[str, str] | None = None,
    cwd: Path | None = None,
    timeout: int = 1800,
) -> EvalRunResult:
    env = os.environ.copy()
    if extra_env:
        env.update({k: str(v) for k, v in extra_env.items()})

    cmd = run_cmd_template.format(domain=domain)
    start = time.time()
    completed = subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    latest_run = find_latest_run(runs_dir, after_mtime=start - 1.0)
    if latest_run is None:
        return EvalRunResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            run_dir=None,
            manifest={},
            metrics={},
            run_health={},
            summary_report={},
        )

    artifacts = load_run_artifacts(latest_run)
    return EvalRunResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        run_dir=str(latest_run),
        manifest=artifacts["manifest"],
        metrics=artifacts["metrics"],
        run_health=artifacts["run_health"],
        summary_report=artifacts["summary_report"],
    )
