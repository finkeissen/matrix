"""Run orchestration (single run + daemon loop).

Directory contract (within MATRIX_RUNS_ROOT):

  incoming/   - drop new run directories here (prepared by user or upstream tools)
  active/     - claimed runs currently being executed
  done/       - finished runs (admissible + executed successfully)
  failed/     - finished runs (inadmissible, STOP, or execution failed)
  .state/     - daemon heartbeat (small status file for monitoring)

The orchestrator deliberately avoids using /tmp. All runtime artifacts (including logs)
are written into the run directory so they can be archived verbatim to SSD later.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from engine.utils.fs import read_json
from engine.utils.logging import setup_run_logger
from engine.stages import intake, validate, execute, update, self_control


def _ensure_dirs(runs_root: Path) -> None:
    for p in ["incoming", "active", "done", "failed", ".state"]:
        (runs_root / p).mkdir(parents=True, exist_ok=True)


def _incoming(runs_root: Path) -> list[Path]:
    inc = runs_root / "incoming"
    runs = [p for p in inc.iterdir() if p.is_dir() and not p.name.startswith(".")]
    return sorted(runs, key=lambda p: p.stat().st_mtime)


def _claim(runs_root: Path, run_dir: Path) -> Path | None:
    """Atomically move a run from incoming/ to active/.

    Returns the new path under active/ or None if claiming failed.
    """
    dest = runs_root / "active" / run_dir.name
    try:
        run_dir.rename(dest)
        return dest
    except Exception:
        return None


def _finalize(runs_root: Path, run_dir: Path, ok: bool) -> None:
    """Move run from active/ to done/ or failed/.

    Uses rename() when possible (fast on same filesystem). Falls back to copytree
    if rename fails (e.g. cross-device move).
    """
    target = runs_root / ("done" if ok else "failed") / run_dir.name
    try:
        run_dir.rename(target)
    except Exception:
        shutil.copytree(run_dir, target, dirs_exist_ok=True)
        shutil.rmtree(run_dir, ignore_errors=True)


def run_single(run_dir: Path) -> int:
    """Execute the pipeline for a single run directory.

    Return code semantics:
      0 - executed successfully
      1 - inadmissible/STOP or execution failure
    """
    started = time.time()
    logger = setup_run_logger(run_dir)
    logger.info("run.start run_id=%s", run_dir.name)

    try:
        intake.run(run_dir)
        logger.info("stage.intake ok")
        validate.run(run_dir)
        logger.info("stage.validate ok")

        decision = read_json(run_dir / "decision.json")
        approved = bool(decision.get("approved"))
        outcome = decision.get("outcome", "inadmissible")
        logger.info("decision approved=%s outcome=%s", approved, outcome)

        rc = 1
        if approved and outcome == "admissible":
            rc = execute.run(run_dir)
            logger.info("stage.execute rc=%s", rc)
            if rc == 0:
                update.run(run_dir)
                logger.info("stage.update ok")

        self_control.run(run_dir, started_at=started)
        logger.info("stage.self_control ok")
        logger.info("run.finish rc=%s", 0 if rc == 0 else 1)
        return 0 if rc == 0 else 1
    except Exception as e:
        logger.exception("run.crash err=%r", e)
        # best-effort self control, so duration is always recorded
        try:
            self_control.run(run_dir, started_at=started)
        except Exception:
            pass
        return 1


def daemon_loop(runs_root: Path, poll_sec: float = 1.0) -> int:
    """Forever loop: claim runs from incoming/ and process them."""
    _ensure_dirs(runs_root)
    hb = runs_root / ".state" / "engine.heartbeat"

    while True:
        hb.write_text(json.dumps({"ts": time.time(), "status": "idle"}) + "\n", encoding="utf-8")

        inc = _incoming(runs_root)
        if not inc:
            time.sleep(poll_sec)
            continue

        claimed = _claim(runs_root, inc[0])
        if not claimed:
            time.sleep(poll_sec)
            continue

        hb.write_text(
            json.dumps({"ts": time.time(), "status": f"running:{claimed.name}"}) + "\n",
            encoding="utf-8",
        )
        rc = run_single(claimed)
        _finalize(runs_root, claimed, ok=(rc == 0))
