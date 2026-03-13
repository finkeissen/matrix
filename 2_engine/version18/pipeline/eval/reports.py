"""
eval/reports.py — Automatic run report generation and cross-run comparison.

Every completed run gets an exports/summary_report.json.
The compare_runs() function produces a side-by-side diff of two run metrics.
"""

import json
from pathlib import Path

from ..config import Config
from ..logging_setup import get_logger
from ..storage.manifest_store import ManifestStore

logger = get_logger(__name__)


class ReportGenerator:
    def __init__(self, config: Config):
        self.config = config

    def generate(self, ctx) -> Path:
        """Generate summary_report.json for a completed run."""
        manifest = ctx.manifest
        report = {
            "run_id": manifest.run_id,
            "domain": manifest.domain,
            "pipeline_version": manifest.pipeline_version,
            "status": manifest.status,
            "created_at": manifest.created_at,
            "finished_at": manifest.finished_at,
            "prompt_versions": manifest.prompt_versions,
            "prompt_hashes": {k: v[:16] + "..." for k, v in manifest.prompt_hashes.items()},
            "model": manifest.model_config.get("model"),
            "metrics": manifest.metrics,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration_ms": s.duration_ms,
                    "counts": s.counts,
                    "error_type": s.error_type,
                }
                for s in manifest.steps
            ],
        }

        out = ctx.exports_dir() / "summary_report.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("report.generated", path=str(out))
        return out

    def print_summary(self, run_id: str):
        """Print a human-readable summary for a completed run."""
        run_dir = self.config.runs_dir / run_id
        report_path = run_dir / "exports" / "summary_report.json"

        if not report_path.exists():
            # Try manifest directly
            store = ManifestStore(run_dir)
            manifest = store.load()
            if manifest is None:
                print(f"[error] No report or manifest found for run: {run_id}")
                return
            metrics = manifest.get("metrics", {})
            status = manifest.get("status", "unknown")
        else:
            with open(report_path) as f:
                report = json.load(f)
            metrics = report.get("metrics", {})
            status = report.get("status", "unknown")

        print(f"\n{'='*55}")
        print(f"  Run Report: {run_id}")
        print(f"{'='*55}")
        print(f"  Status:       {status}")
        print(f"  Generated:    {metrics.get('generated', 'n/a')}")
        print(f"  Accepted:     {metrics.get('accepted', 'n/a')}")
        print(f"  Duplicates:   {metrics.get('duplicates', 'n/a')}")
        print(f"  Acceptance:   {metrics.get('acceptance_rate', 0):.1%}")
        if "by_difficulty" in metrics:
            print(f"  By difficulty: {metrics['by_difficulty']}")
        if "by_category" in metrics:
            print(f"  Categories:   {len(metrics['by_category'])} categories")
        print(f"{'='*55}\n")

    def compare_runs(self, run_a: str, run_b: str):
        """Side-by-side metric comparison of two runs."""

        def load(run_id: str) -> dict:
            path = self.config.runs_dir / run_id / "exports" / "summary_report.json"
            if path.exists():
                return json.loads(path.read_text())
            return {}

        a = load(run_a)
        b = load(run_b)

        if not a or not b:
            print("[error] One or both runs have no summary_report.json")
            return

        print(f"\n{'='*65}")
        print(f"  Comparison: {run_a}  vs  {run_b}")
        print(f"{'='*65}")
        print(f"  {'Metric':<25} {'Run A':>15} {'Run B':>15}")
        print(f"  {'-'*55}")

        metrics_a = a.get("metrics", {})
        metrics_b = b.get("metrics", {})
        scalar_keys = ["generated", "accepted", "duplicates", "acceptance_rate",
                       "rejected_exact", "rejected_normalized", "rejected_schema"]

        for k in scalar_keys:
            va = metrics_a.get(k, "-")
            vb = metrics_b.get(k, "-")
            if isinstance(va, float):
                va = f"{va:.1%}"
            if isinstance(vb, float):
                vb = f"{vb:.1%}"
            print(f"  {k:<25} {str(va):>15} {str(vb):>15}")

        # Prompt version comparison
        pv_a = a.get("prompt_versions", {})
        pv_b = b.get("prompt_versions", {})
        all_steps = sorted(set(pv_a) | set(pv_b))
        print(f"\n  {'Step':<25} {'Prompt A':>15} {'Prompt B':>15}")
        print(f"  {'-'*55}")
        for step in all_steps:
            va = pv_a.get(step, "-")
            vb = pv_b.get(step, "-")
            marker = " ←" if va != vb else ""
            print(f"  {step:<25} {va:>15} {vb:>15}{marker}")
        print(f"{'='*65}\n")
