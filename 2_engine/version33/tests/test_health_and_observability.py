import json
from pathlib import Path

from pipeline.config import Config
from pipeline.run_context import RunContext
from pipeline.health.smoke_tests import run_smoke_tests
from pipeline.health.invariants import check_run_invariants
from pipeline.health.run_health import compute_run_health
from pipeline.observability.run_timeline import build_run_timeline
from pipeline.observability.dashboard import render_dashboard
from pipeline.eval.drift import analyze_drift


def test_smoke_tests_pass():
    config = Config.from_env()
    result = run_smoke_tests(config)
    assert result['ok'] is True
    assert result['failures'] == []


def test_invariants_detect_mismatch():
    manifest = {'status': 'completed', 'metrics': {'generated': 10, 'accepted': 7, 'duplicates': 1, 'acceptance_rate': 0.7}}
    errors = check_run_invariants(manifest)
    assert 'count_mismatch' in errors


def test_run_health_and_dashboard(tmp_path):
    run_dir = tmp_path / 'runs' / 'r1'
    ctx = RunContext.create('r1', 'algebra', run_dir)
    ctx.complete_step('01_scope', counts={'boundaries': 3})
    ctx.finalize(status='completed', metrics={'generated': 3, 'accepted': 3, 'duplicates': 0, 'acceptance_rate': 1.0})
    health = compute_run_health(ctx)
    assert health['score'] >= 80
    timeline = build_run_timeline(ctx)
    assert timeline['run_id'] == 'r1'
    dashboard = render_dashboard(run_dir)
    assert dashboard.exists()
    assert 'Run Dashboard' in dashboard.read_text(encoding='utf-8')


def test_drift_analysis(tmp_path):
    runs_dir = tmp_path / 'runs'
    for i, rate in enumerate([0.9, 0.85, 0.6], start=1):
        run_dir = runs_dir / f'run_{i}'
        run_dir.mkdir(parents=True)
        (run_dir / 'manifest.json').write_text(json.dumps({'run_id': f'run_{i}', 'metrics': {'acceptance_rate': rate}}), encoding='utf-8')
    drift = analyze_drift(runs_dir, last=3)
    assert len(drift['series']) == 3
    assert drift['alerts']
