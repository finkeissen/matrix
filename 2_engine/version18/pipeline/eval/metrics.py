"""
eval/metrics.py — Metrics collection after a completed run.

Collected from: intermediate/, validated/, rejected/ directories.
Written into: manifest.metrics + exports/summary_report.json
"""

import json
from collections import Counter
from pathlib import Path

from ..config import Config
from ..logging_setup import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    def __init__(self, config: Config):
        self.config = config

    def collect(self, ctx) -> dict:
        """Collect metrics from a completed RunContext. Returns metrics dict."""
        run_dir = ctx.run_dir
        metrics = {}

        # Count generated problems
        gen_file = run_dir / "intermediate" / "04_problem_generation.json"
        if gen_file.exists():
            data = json.loads(gen_file.read_text())
            problems = data if isinstance(data, list) else data.get("problems", [])
            metrics["generated"] = len(problems)

            # Distribution by category
            cat_counts = Counter(p.get("category", "unknown") for p in problems)
            metrics["by_category"] = dict(cat_counts)

            # Distribution by difficulty
            diff_counts = Counter(p.get("difficulty", "unknown") for p in problems)
            metrics["by_difficulty"] = dict(diff_counts)

        # Count accepted after dedup
        dedup_file = run_dir / "intermediate" / "06_deduplication.json"
        if dedup_file.exists():
            data = json.loads(dedup_file.read_text())
            metrics["accepted"] = data.get("counts", {}).get("accepted", 0)
            metrics["rejected_exact"] = data.get("counts", {}).get("rejected_exact", 0)
            metrics["rejected_normalized"] = data.get("counts", {}).get("rejected_normalized", 0)
            metrics["duplicates"] = (
                metrics.get("rejected_exact", 0) + metrics.get("rejected_normalized", 0)
            )

        # Schema rejections
        schema_rej = run_dir / "rejected" / "schema_errors.json"
        if schema_rej.exists():
            data = json.loads(schema_rej.read_text())
            metrics["rejected_schema"] = len(data) if isinstance(data, list) else 0

        # Compute acceptance rate
        total = metrics.get("generated", 0)
        accepted = metrics.get("accepted", 0)
        metrics["acceptance_rate"] = round(accepted / total, 3) if total else 0.0

        logger.info("metrics.collected", **{k: v for k, v in metrics.items()
                                             if not isinstance(v, dict)})
        return metrics
