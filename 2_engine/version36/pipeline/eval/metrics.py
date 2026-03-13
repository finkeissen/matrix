"""Metrics collection after a completed run."""
from __future__ import annotations
import json
from collections import Counter
from ..config import Config
from ..logging_setup import get_logger

logger = get_logger(__name__)

class MetricsCollector:
    def __init__(self, config: Config):
        self.config = config

    def collect(self, ctx) -> dict:
        run_dir = ctx.run_dir
        metrics = {}
        gen_file = run_dir / 'intermediate' / '04_problem_generation.json'
        if gen_file.exists():
            problems = json.loads(gen_file.read_text(encoding='utf-8'))
            metrics['generated'] = len(problems)
            metrics['by_category'] = dict(Counter(p.get('category', 'unknown') for p in problems))
            metrics['by_difficulty'] = dict(Counter(p.get('difficulty', 'unknown') for p in problems))
        dedup_file = run_dir / 'intermediate' / '06_deduplication.json'
        if dedup_file.exists():
            data = json.loads(dedup_file.read_text(encoding='utf-8'))
            counts = data.get('counts', {})
            metrics['accepted'] = counts.get('accepted', 0)
            metrics['rejected_exact'] = counts.get('rejected_exact', 0)
            metrics['rejected_normalized'] = counts.get('rejected_normalized', 0)
            metrics['rejected_semantic'] = counts.get('rejected_semantic', 0)
            metrics['duplicates'] = metrics.get('rejected_exact', 0) + metrics.get('rejected_normalized', 0) + metrics.get('rejected_semantic', 0)
        for name, key in [('schema_errors.json','rejected_schema'), ('business_rule_failures.json','rejected_business'), ('content_failures.json','rejected_content'), ('quality_errors.json','rejected_quality')]:
            path = run_dir / 'rejected' / name
            if path.exists():
                data = json.loads(path.read_text(encoding='utf-8'))
                metrics[key] = len(data) if isinstance(data, list) else 0
        total = metrics.get('generated', 0)
        accepted = metrics.get('accepted', 0)
        metrics['acceptance_rate'] = round(accepted / total, 3) if total else 0.0
        logger.info('metrics.collected', **{k: v for k, v in metrics.items() if not isinstance(v, dict)})
        return metrics
