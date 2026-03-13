"""Aggregate health scoring for a completed run."""
from __future__ import annotations
import json
from pathlib import Path
from .invariants import check_run_invariants

def compute_run_health(ctx) -> dict:
    manifest = ctx.manifest.to_dict() if hasattr(ctx.manifest, 'to_dict') else ctx.manifest
    invariant_errors = check_run_invariants(manifest)
    schema_errors = 0
    quality_errors = 0
    run_dir = ctx.run_dir if hasattr(ctx, 'run_dir') else Path(ctx['run_dir'])
    rejected = run_dir / 'rejected'
    for name in ['schema_errors.json', 'quality_errors.json', 'business_rule_failures.json', 'content_failures.json']:
        path = rejected / name
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
            count = len(data) if isinstance(data, list) else len(data.get('errors', []))
            if 'schema' in name:
                schema_errors += count
            else:
                quality_errors += count
    score = 100 - (len(invariant_errors) * 20) - min(schema_errors, 20) - min(quality_errors, 20)
    score = max(0, score)
    return {
        'run_id': manifest.get('run_id'),
        'score': score,
        'invariant_errors': invariant_errors,
        'schema_errors': schema_errors,
        'quality_errors': quality_errors,
        'status': 'healthy' if score >= 80 and not invariant_errors else 'degraded' if score >= 50 else 'unhealthy',
    }

def write_run_health(ctx) -> Path:
    payload = compute_run_health(ctx)
    out = ctx.exports_dir() / 'run_health.json'
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    return out
