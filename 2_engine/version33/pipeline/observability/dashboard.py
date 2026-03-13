"""Simple HTML dashboard for run status and health."""
from __future__ import annotations
import json
from pathlib import Path

def render_dashboard(run_dir: Path) -> Path:
    manifest_path = run_dir / 'manifest.json'
    if not manifest_path.exists():
        raise FileNotFoundError(f'No manifest found at {manifest_path}')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    metrics = manifest.get('metrics', {})
    steps = manifest.get('steps', [])
    health = {}
    health_path = run_dir / 'exports' / 'run_health.json'
    if health_path.exists():
        health = json.loads(health_path.read_text(encoding='utf-8'))
    rows = ''.join(
        f"<tr><td>{s.get('name')}</td><td>{s.get('status')}</td><td>{s.get('duration_ms','')}</td><td><pre>{json.dumps(s.get('counts',{}), ensure_ascii=False)}</pre></td></tr>"
        for s in steps
    )
    metric_rows = ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in metrics.items() if not isinstance(v, dict))
    html = f'''<!doctype html>
<html><head><meta charset="utf-8"><title>Run Dashboard {manifest.get('run_id')}</title>
<style>body{{font-family:Arial,sans-serif;margin:24px}} table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ccc;padding:8px;vertical-align:top}} .card{{margin:16px 0;padding:16px;border:1px solid #ddd;border-radius:12px}}</style>
</head><body>
<h1>Run Dashboard</h1>
<div class="card"><strong>Run ID:</strong> {manifest.get('run_id')}<br><strong>Status:</strong> {manifest.get('status')}<br><strong>Health score:</strong> {health.get('score','n/a')}</div>
<div class="card"><h2>Metrics</h2><table><tr><th>Name</th><th>Value</th></tr>{metric_rows}</table></div>
<div class="card"><h2>Steps</h2><table><tr><th>Step</th><th>Status</th><th>Duration (ms)</th><th>Counts</th></tr>{rows}</table></div>
</body></html>'''
    out = run_dir / 'exports' / 'dashboard.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return out
