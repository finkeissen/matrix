#!/usr/bin/env python3
"""CLI for pipeline v19."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pipeline.config import Config
from pipeline.orchestrator import Orchestrator
from pipeline.eval.reports import ReportGenerator
from pipeline.eval.drift import analyze_drift
from pipeline.health.diagnostics import run_diagnostics
from pipeline.health.smoke_tests import run_smoke_tests
from pipeline.observability.dashboard import render_dashboard


def cmd_run(args):
    config = Config.from_env()
    run_id = Orchestrator(config).run(domain=args.domain, prompt_variant=args.prompt_variant, steps=args.steps.split(',') if args.steps != 'all' else None, dry_run=args.dry_run)
    if run_id:
        print(f'Run completed: {run_id}')
        print(f'Report: {config.runs_dir / run_id / "exports" / "summary_report.json"}')


def cmd_resume(args):
    config = Config.from_env()
    Orchestrator(config).resume(args.run_id)


def cmd_validate(args):
    config = Config.from_env()
    run_dir = config.runs_dir / args.run_id
    manifest = run_dir / 'manifest.json'
    if not manifest.exists():
        print(f'[error] Run not found: {args.run_id}')
        return
    print(json.dumps(json.loads(manifest.read_text(encoding='utf-8')), indent=2, ensure_ascii=False))


def cmd_report(args):
    ReportGenerator(Config.from_env()).print_summary(args.run_id)


def cmd_compare(args):
    ReportGenerator(Config.from_env()).compare_runs(args.run_a, args.run_b)


def cmd_doctor(args):
    config = Config.from_env()
    payload = run_diagnostics(config)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_smoke(args):
    print(json.dumps(run_smoke_tests(Config.from_env()), indent=2, ensure_ascii=False))


def cmd_dashboard(args):
    config = Config.from_env()
    path = render_dashboard(config.runs_dir / args.run_id)
    print(path)


def cmd_drift(args):
    config = Config.from_env()
    print(json.dumps(analyze_drift(config.runs_dir, last=args.last), indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='pipeline')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('run'); p.add_argument('--domain', required=True); p.add_argument('--prompt-variant', default=''); p.add_argument('--steps', default='all'); p.add_argument('--dry-run', action='store_true'); p.set_defaults(func=cmd_run)
    p = sub.add_parser('resume'); p.add_argument('--run-id', required=True); p.set_defaults(func=cmd_resume)
    p = sub.add_parser('validate'); p.add_argument('--run-id', required=True); p.set_defaults(func=cmd_validate)
    p = sub.add_parser('report'); p.add_argument('--run-id', required=True); p.set_defaults(func=cmd_report)
    p = sub.add_parser('compare'); p.add_argument('--run-a', required=True); p.add_argument('--run-b', required=True); p.set_defaults(func=cmd_compare)
    p = sub.add_parser('doctor'); p.set_defaults(func=cmd_doctor)
    p = sub.add_parser('smoke'); p.set_defaults(func=cmd_smoke)
    p = sub.add_parser('dashboard'); p.add_argument('--run-id', required=True); p.set_defaults(func=cmd_dashboard)
    p = sub.add_parser('drift'); p.add_argument('--last', type=int, default=10); p.set_defaults(func=cmd_drift)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    main()
