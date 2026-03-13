"""
tests/test_run_context.py — Tests for RunContext and RunManifest.
"""

import json
import pytest
from pathlib import Path

from pipeline.run_context import RunContext, RunManifest, StepRecord


@pytest.fixture
def run_dir(tmp_path):
    return tmp_path / "runs" / "test_run_001"


def test_create_writes_manifest(run_dir):
    ctx = RunContext.create("test_run_001", "algebra", run_dir)
    assert (run_dir / "manifest.json").exists()
    data = json.loads((run_dir / "manifest.json").read_text())
    assert data["run_id"] == "test_run_001"
    assert data["domain"] == "algebra"
    assert data["status"] == "running"


def test_start_and_complete_step(run_dir):
    ctx = RunContext.create("r001", "algebra", run_dir)
    ctx.start_step("01_scope")
    assert ctx.manifest.get_step("01_scope").status == "running"
    ctx.complete_step("01_scope", output_path="/tmp/scope.json", counts={"boundaries": 5})
    step = ctx.manifest.get_step("01_scope")
    assert step.status == "completed"
    assert step.counts == {"boundaries": 5}
    assert step.duration_ms is not None


def test_is_step_completed(run_dir):
    ctx = RunContext.create("r002", "algebra", run_dir)
    assert not ctx.is_step_completed("01_scope")
    ctx.start_step("01_scope")
    ctx.complete_step("01_scope")
    assert ctx.is_step_completed("01_scope")


def test_fail_step(run_dir):
    ctx = RunContext.create("r003", "algebra", run_dir)
    ctx.fail_step("01_scope", "ValueError", "LLM returned invalid JSON")
    step = ctx.manifest.get_step("01_scope")
    assert step.status == "failed"
    assert step.error_type == "ValueError"
    assert ctx.manifest.status == "failed"


def test_manifest_persists_across_load(run_dir):
    ctx = RunContext.create("r004", "algebra", run_dir)
    ctx.complete_step("01_scope", counts={"boundaries": 3})

    # Load fresh context
    ctx2 = RunContext.load(run_dir)
    assert ctx2 is not None
    step = ctx2.manifest.get_step("01_scope")
    assert step.status == "completed"
    assert step.counts == {"boundaries": 3}


def test_atomic_write_no_partial_state(run_dir):
    """Simulate concurrent write — final manifest must be valid JSON."""
    ctx = RunContext.create("r005", "algebra", run_dir)
    for i in range(10):
        ctx.complete_step(f"step_{i:02d}", counts={"n": i})
    data = json.loads((run_dir / "manifest.json").read_text())
    assert len(data["steps"]) == 10


def test_load_returns_none_for_missing_dir(tmp_path):
    ctx = RunContext.load(tmp_path / "nonexistent")
    assert ctx is None


def test_finalize(run_dir):
    ctx = RunContext.create("r006", "algebra", run_dir)
    ctx.finalize(status="completed", metrics={"generated": 100, "accepted": 85})
    assert ctx.manifest.status == "completed"
    assert ctx.manifest.metrics["generated"] == 100
    assert ctx.manifest.finished_at is not None
