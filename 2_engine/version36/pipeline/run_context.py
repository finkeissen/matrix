"""
run_context.py — RunManifest and RunContext for Pipeline v18.

The RunManifest is the single source of truth for every run.
Every step reads from and writes to it atomically.

Key design decisions:
- RunManifest is written atomically (tmp → rename) to prevent corruption
- Each step entry contains status, timing, input/output paths, and error info
- Resume logic: completed steps are skipped; failed steps are retried
- All writes go through RunContext.update_step() to ensure consistency
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class StepRecord:
    name: str
    status: str = "pending"          # pending | running | completed | failed | skipped
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration_ms: Optional[int] = None
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    retry_count: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    counts: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None or k in ("status", "name", "retry_count")}


@dataclass
class RunManifest:
    """
    The canonical record of a single pipeline run.
    Written to manifest.json in the run directory.
    """
    run_id: str
    created_at: str
    domain: str
    pipeline_version: str = "34.0.0"
    status: str = "running"          # running | completed | failed | interrupted
    finished_at: Optional[str] = None

    model_config: dict = field(default_factory=dict)
    prompt_versions: dict = field(default_factory=dict)
    prompt_hashes: dict = field(default_factory=dict)

    steps: list[StepRecord] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def get_step(self, name: str) -> Optional[StepRecord]:
        for s in self.steps:
            if s.name == name:
                return s
        return None

    def upsert_step(self, record: StepRecord):
        for i, s in enumerate(self.steps):
            if s.name == record.name:
                self.steps[i] = record
                return
        self.steps.append(record)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["steps"] = [s.to_dict() for s in self.steps]
        return {k: v for k, v in d.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> "RunManifest":
        steps_raw = data.pop("steps", [])
        manifest = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        manifest.steps = [StepRecord(**s) for s in steps_raw]
        return manifest


class RunContext:
    """
    Wraps a RunManifest and provides atomic read/write access.
    The context is the single object passed through the entire pipeline.

    Atomic write pattern:
        write to .tmp file → fsync → rename over final file
    This guarantees manifest.json is never in a partially-written state.
    """

    def __init__(self, manifest: RunManifest, run_dir: Path):
        self.manifest = manifest
        self.run_dir = run_dir
        self._manifest_path = run_dir / "manifest.json"

    # ── Directory helpers ──────────────────────────────────────────────────

    # ── Step-local run artifact paths (new in v29) ─────────────────────────

    def step_dir(self, step_name: str) -> Path:
        """Return the step work-package dir inside this run."""
        from .step_registry import get_step_spec
        spec = get_step_spec(step_name)
        p = self.run_dir / "steps" / spec.slug
        p.mkdir(parents=True, exist_ok=True)
        return p

    def step_run_dir(self, step_name: str) -> Path:
        p = self.step_dir(step_name) / "run"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def step_input_path(self, step_name: str) -> Path:
        return self.step_run_dir(step_name) / "input.json"

    def step_output_path(self, step_name: str) -> Path:
        return self.step_run_dir(step_name) / "output.json"

    def step_meta_path(self, step_name: str) -> Path:
        return self.step_run_dir(step_name) / "meta.json"

    def write_step_payload(self, step_name: str, kind: str, payload: object) -> Path:
        """Write input / output / meta payload for a step.

        Args:
            step_name: e.g. '01_scope'
            kind: one of 'input', 'output', 'meta'
            payload: dict or JSON string

        Returns:
            Path where the payload was written.
        """
        if kind not in {"input", "output", "meta"}:
            raise ValueError(f"Unsupported step payload kind: {kind!r}. Use 'input', 'output', or 'meta'.")
        path: Path = getattr(self, f"step_{kind}_path")(step_name)
        data = payload if isinstance(payload, str) else json.dumps(payload, indent=2, ensure_ascii=False)
        path.write_text(data, encoding="utf-8")
        return path

    def read_step_payload(self, step_name: str, kind: str) -> dict:
        """Read a previously written step payload as a dict."""
        if kind not in {"input", "output", "meta"}:
            raise ValueError(f"Unsupported step payload kind: {kind!r}.")
        path: Path = getattr(self, f"step_{kind}_path")(step_name)
        if not path.exists():
            raise FileNotFoundError(f"Step payload not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    # ── Legacy directory helpers ───────────────────────────────────────────

    def intermediate_dir(self) -> Path:
        p = self.run_dir / "intermediate"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def validated_dir(self) -> Path:
        p = self.run_dir / "validated"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def rejected_dir(self) -> Path:
        p = self.run_dir / "rejected"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def exports_dir(self) -> Path:
        p = self.run_dir / "exports"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def logs_dir(self) -> Path:
        p = self.run_dir / "logs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # ── Step lifecycle ─────────────────────────────────────────────────────

    def start_step(self, step_name: str, input_path: Optional[str] = None) -> StepRecord:
        record = self.manifest.get_step(step_name) or StepRecord(name=step_name)
        record.status = "running"
        record.started_at = _now_iso()
        # Prefer explicit path; fall back to new step-local input path
        record.input_path = input_path or str(self.step_input_path(step_name))
        self.manifest.upsert_step(record)
        self.save()
        return record

    def complete_step(self, step_name: str, output_path: Optional[str] = None, counts: dict = None):
        record = self.manifest.get_step(step_name) or StepRecord(name=step_name)
        now = _now_iso()
        record.status = "completed"
        record.finished_at = now
        if record.started_at:
            start = datetime.fromisoformat(record.started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(now.replace("Z", "+00:00"))
            record.duration_ms = int((end - start).total_seconds() * 1000)
        record.output_path = output_path
        if counts:
            record.counts = counts
        self.manifest.upsert_step(record)
        self.save()

    def fail_step(self, step_name: str, error_type: str, error_message: str):
        record = self.manifest.get_step(step_name) or StepRecord(name=step_name)
        record.status = "failed"
        record_finished_at = _now_iso()
        record.error_type = error_type
        record.error_message = error_message
        record.retry_count += 1
        self.manifest.upsert_step(record)
        self.manifest.status = "failed"
        self.save()

    def skip_step(self, step_name: str, reason: str = "already completed"):
        record = self.manifest.get_step(step_name) or StepRecord(name=step_name)
        record.status = "skipped"
        self.manifest.upsert_step(record)
        self.save()

    def is_step_completed(self, step_name: str) -> bool:
        record = self.manifest.get_step(step_name)
        return record is not None and record.status == "completed"

    # ── Manifest persistence (atomic) ──────────────────────────────────────

    def save(self):
        """Atomically write manifest.json using tmp → rename pattern."""
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(self.manifest.to_dict(), indent=2, ensure_ascii=False)
        fd, tmp_path = tempfile.mkstemp(
            dir=self._manifest_path.parent,
            prefix=".manifest_",
            suffix=".tmp"
       )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._manifest_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def finalize(self, status: str = "completed", metrics: dict = None):
        self.manifest.status = status
        self.manifest.finished_at = _now_iso()
        if metrics:
            self.manifest.metrics = metrics
        self.save()

    @classmethod
    def create(cls, run_id: str, domain: str, run_dir: Path,
               model_config: dict = None, pipeline_version: str = "34.0.0") -> "RunContext":
        run_dir.mkdir(parents=True, exist_ok=True)
        manifest = RunManifest(
            run_id=run_id,
            created_at=_now_iso(),
            domain=domain,
            pipeline_version=pipeline_version,
            model_config=model_config or {},
        )
        ctx = cls(manifest, run_dir)
        ctx.save()
        return ctx

    @classmethod
    def load(cls, run_dir: Path) -> Optional["RunContext"]:
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.exists():
            return None
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        manifest = RunManifest.from_dict(data)
        return cls(manifest, run_dir)
