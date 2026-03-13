#!/usr/bin/env python3
"""
cli.py — Command-Line Interface for the Atomic Problem Identification Pipeline v18.

Usage:
    pipeline run --domain thermodynamics
    pipeline run --domain algebra --prompt-variant v2 --dry-run
    pipeline resume --run-id run_2026_03_07_001
    pipeline validate --run-id run_2026_03_07_001
    pipeline report --run-id run_2026_03_07_001
    pipeline export --run-id run_2026_03_07_001 --format jsonl
    pipeline compare --run-a run_2026_03_07_001 --run-b run_2026_03_07_002
"""

import argparse
import sys
from pathlib import Path

# Ensure src is on path when called as script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pipeline.orchestrator import Orchestrator
from pipeline.config import Config
from pipeline.logging_setup import get_logger
from pipeline.eval.reports import ReportGenerator
from pipeline.storage.manifest_store import ManifestStore

logger = get_logger(__name__)


def cmd_run(args):
    """Start a new pipeline run for a domain."""
    config = Config.from_env()
    orchestrator = Orchestrator(config)

    run_id = orchestrator.run(
        domain=args.domain,
        prompt_variant=args.prompt_variant,
        steps=args.steps.split(",") if args.steps != "all" else None,
        dry_run=args.dry_run,
    )
    if run_id:
        print(f"\nRun completed: {run_id}")
        print(f"Report: data/runs/{run_id}/exports/summary_report.json")


def cmd_resume(args):
    """Resume an interrupted pipeline run."""
    config = Config.from_env()
    orchestrator = Orchestrator(config)
    orchestrator.resume(run_id=args.run_id)


def cmd_validate(args):
    """Validate all artifacts in a completed run."""
    config = Config.from_env()
    store = ManifestStore(config.runs_dir / args.run_id)
    manifest = store.load()
    if manifest is None:
        print(f"[error] Run not found: {args.run_id}")
        sys.exit(1)
    print(f"Run status: {manifest.get('status')}")
    steps = manifest.get("steps", [])
    for step in steps:
        status = step.get("status", "unknown")
        name = step.get("name", "?")
        icon = "✓" if status == "completed" else "✗" if status == "failed" else "○"
        print(f"  {icon} {name}: {status}")


def cmd_report(args):
    """Print a summary report for a completed run."""
    config = Config.from_env()
    generator = ReportGenerator(config)
    generator.print_summary(args.run_id)


def cmd_export(args):
    """Export problems from a completed run."""
    config = Config.from_env()
    run_dir = config.runs_dir / args.run_id / "exports"
    export_file = run_dir / f"atomic_problems.{args.format}"
    if export_file.exists():
        print(f"Export available at: {export_file}")
    else:
        print(f"[error] Export file not found. Was the run completed?")
        sys.exit(1)


def cmd_compare(args):
    """Compare two runs by their telemetry and metrics."""
    config = Config.from_env()
    generator = ReportGenerator(config)
    generator.compare_runs(args.run_a, args.run_b)


def main():
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Atomic Problem Identification Pipeline v18",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- run ---
    p_run = subparsers.add_parser("run", help="Start a new pipeline run")
    p_run.add_argument("--domain", required=True, help="Domain to process (e.g. thermodynamics)")
    p_run.add_argument("--prompt-variant", default="", help="Prompt variant for A/B testing (e.g. v2)")
    p_run.add_argument("--steps", default="all", help="Comma-separated steps or 'all'")
    p_run.add_argument("--dry-run", action="store_true", help="Show steps without executing")
    p_run.set_defaults(func=cmd_run)

    # --- resume ---
    p_resume = subparsers.add_parser("resume", help="Resume an interrupted run")
    p_resume.add_argument("--run-id", required=True, help="Run ID to resume")
    p_resume.set_defaults(func=cmd_resume)

    # --- validate ---
    p_val = subparsers.add_parser("validate", help="Validate all artifacts in a run")
    p_val.add_argument("--run-id", required=True)
    p_val.set_defaults(func=cmd_validate)

    # --- report ---
    p_rep = subparsers.add_parser("report", help="Print run summary report")
    p_rep.add_argument("--run-id", required=True)
    p_rep.set_defaults(func=cmd_report)

    # --- export ---
    p_exp = subparsers.add_parser("export", help="Export problems from a run")
    p_exp.add_argument("--run-id", required=True)
    p_exp.add_argument("--format", default="jsonl", choices=["jsonl", "json"])
    p_exp.set_defaults(func=cmd_export)

    # --- compare ---
    p_cmp = subparsers.add_parser("compare", help="Compare two runs")
    p_cmp.add_argument("--run-a", required=True)
    p_cmp.add_argument("--run-b", required=True)
    p_cmp.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
