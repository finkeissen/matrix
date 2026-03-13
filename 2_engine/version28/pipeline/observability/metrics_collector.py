"""Per-run observability metrics written alongside the manifest."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

class ObservabilityMetricsCollector:
    def __init__(self):
        self.metrics: dict[str, object] = {'recorded_at': _now_iso()}
    def record_step(self, step: str, duration_ms: int | None, status: str = 'completed'):
        self.metrics[f'step.{step}.duration_ms'] = duration_ms or 0
        self.metrics[f'step.{step}.status'] = status
    def record_count(self, name: str, value: int | float):
        self.metrics[name] = value
    def record_gauge(self, name: str, value: object):
        self.metrics[name] = value
    def snapshot(self) -> dict[str, object]:
        return dict(self.metrics)
    def write(self, run_dir: Path) -> Path:
        path = run_dir / 'exports' / 'metrics.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.metrics, indent=2, ensure_ascii=False), encoding='utf-8')
        return path
