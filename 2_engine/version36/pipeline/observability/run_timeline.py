"""Generate a machine-readable run timeline from manifest steps."""
from __future__ import annotations
import json
from pathlib import Path

def build_run_timeline(ctx) -> dict:
    steps = []
    for step in ctx.manifest.steps:
        steps.append({
            'name': step.name,
            'status': step.status,
            'started_at': step.started_at,
            'finished_at': step.finished_at,
            'duration_ms': step.duration_ms,
            'counts': step.counts,
        })
    total_duration_ms = sum((s.get('duration_ms') or 0) for s in steps)
    return {'run_id': ctx.manifest.run_id, 'steps': steps, 'total_duration_ms': total_duration_ms}

def write_run_timeline(ctx) -> Path:
    payload = build_run_timeline(ctx)
    out = ctx.exports_dir() / 'run_timeline.json'
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    return out
