"""Compare quality drift across recent runs."""
from __future__ import annotations
import json
from pathlib import Path

def analyze_drift(runs_dir: Path, last: int = 10) -> dict:
    manifests = []
    for path in sorted(runs_dir.glob('*/manifest.json'))[-last:]:
        try:
            manifests.append(json.loads(path.read_text(encoding='utf-8')))
        except Exception:
            continue
    series = []
    alerts = []
    prev = None
    for m in manifests:
        acc = m.get('metrics', {}).get('acceptance_rate', 0)
        series.append({'run_id': m.get('run_id'), 'acceptance_rate': acc})
        if prev is not None and prev - acc >= 0.15:
            alerts.append({'run_id': m.get('run_id'), 'type': 'acceptance_rate_drop', 'previous': prev, 'current': acc})
        prev = acc
    return {'series': series, 'alerts': alerts}
