"""Pipeline orchestrator v19 with smoke tests, quality gates, invariants, and observability."""
from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import Optional

from .config import Config
from .logging_setup import get_logger
from .run_context import RunContext
from .prompts.loader import PromptLoader
from .validation.schema_validator import SchemaValidator
from .validation.business_rules import validate_business_rules
from .validation.content_checks import run_content_checks
from .validation.result_quality import run_quality_checks
from .eval.reports import ReportGenerator
from .eval.metrics import MetricsCollector
from .health.smoke_tests import run_smoke_tests
from .health.invariants import check_run_invariants
from .health.run_health import write_run_health
from .observability.metrics_collector import ObservabilityMetricsCollector
from .observability.run_timeline import write_run_timeline
from .observability.dashboard import render_dashboard

from .step_registry import get_step_spec
from .step_chain import build_step_input

logger = get_logger(__name__)

# Pre-pipeline: atomic problem curation and store build.
# Run these before the main pipeline when subdomains_file is available.
PRE_PIPELINE_STEPS = [
    '00_atomic_problem_curation',
    '01_atomic_problem_merge',
]

# Main pipeline: scope → export.
MAIN_PIPELINE_STEPS = [
    '01_scope', '02_seed_expansion', '03_categories', '04_problem_generation',
    '05_validation', '06_deduplication', '07_ranking', '08_export',
]

# Default run = main pipeline only.
# Pass steps=PRE_PIPELINE_STEPS + MAIN_PIPELINE_STEPS for a full end-to-end run.
ALL_STEPS = MAIN_PIPELINE_STEPS


def _make_run_id(domain: str, config: Config) -> str:
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    existing = list(config.runs_dir.glob(f'{ts}_*_{domain}'))
    idx = len(existing) + 1
    return f'{ts}_{idx:03d}_{domain}'


class Orchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.prompt_loader = PromptLoader(config)
        self.validator = SchemaValidator(config)
        self.max_retries = config.default_retries

    def run(self, domain: str, prompt_variant: str = '', steps: Optional[list[str]] = None,
            dry_run: bool = False, run_id: Optional[str] = None,
            include_pre_pipeline: bool = False) -> Optional[str]:
        if steps is not None:
            active_steps = steps
        elif include_pre_pipeline:
            active_steps = PRE_PIPELINE_STEPS + MAIN_PIPELINE_STEPS
        else:
            active_steps = MAIN_PIPELINE_STEPS[:]
        run_id = run_id or _make_run_id(domain, self.config)
        if dry_run:
            print(f"[dry-run] Would execute {len(active_steps)} steps for domain '{domain}':")
            for s in active_steps:
                print(f'  → {s}')
            return None
        smoke = run_smoke_tests(self.config)
        if not smoke['ok']:
            print('[error] Smoke tests failed before run start:')
            for failure in smoke['failures']:
                print(f'  - {failure}')
            return None
        prompt_versions, prompt_hashes = self.prompt_loader.resolve_versions(active_steps, variant=prompt_variant)
        ctx = RunContext.create(run_id=run_id, domain=domain, run_dir=self.config.runs_dir / run_id, model_config=self.config.model_config(), pipeline_version=self.config.pipeline_version)
        ctx.manifest.prompt_versions = prompt_versions
        ctx.manifest.prompt_hashes = prompt_hashes
        ctx.save()
        return self._dispatch_steps(ctx, active_steps)

    def resume(self, run_id: str) -> Optional[str]:
        ctx = RunContext.load(self.config.runs_dir / run_id)
        if ctx is None:
            print(f'[error] Run not found: {run_id}')
            return None
        completed = [s.name for s in ctx.manifest.steps if s.status == 'completed']
        remaining = [s for s in ALL_STEPS if s not in completed]
        ctx.manifest.status = 'running'
        ctx.save()
        return self._dispatch_steps(ctx, remaining)

    def _dispatch_steps(self, ctx: RunContext, steps: list[str]) -> Optional[str]:
        obs = ObservabilityMetricsCollector()
        for step_name in steps:
            if ctx.is_step_completed(step_name):
                logger.info('step.skipped', step=step_name, reason='already_completed')
                continue
            success = self._run_step_with_retry(ctx, step_name, ctx.manifest.domain)
            step = ctx.manifest.get_step(step_name)
            obs.record_step(step_name, step.duration_ms if step else 0, status=step.status if step else 'unknown')
            if not success:
                ctx.finalize(status='failed')
                obs.record_gauge('run.status', 'failed')
                obs.write(ctx.run_dir)
                write_run_timeline(ctx)
                write_run_health(ctx)
                render_dashboard(ctx.run_dir)
                return None
        metrics = MetricsCollector(self.config).collect(ctx)
        ctx.finalize(status='completed', metrics=metrics)
        invariant_errors = check_run_invariants(ctx.manifest.to_dict())
        if invariant_errors:
            ctx.manifest.metrics['invariant_errors'] = invariant_errors
            ctx.manifest.status = 'completed_with_warnings'
            ctx.save()
        for k, v in metrics.items():
            if not isinstance(v, dict):
                obs.record_count(k, v)
        obs.record_gauge('run.status', ctx.manifest.status)
        obs.write(ctx.run_dir)
        write_run_timeline(ctx)
        write_run_health(ctx)
        ReportGenerator(self.config).generate(ctx)
        render_dashboard(ctx.run_dir)
        return ctx.manifest.run_id

    def _run_step_with_retry(self, ctx: RunContext, step_name: str, domain: str) -> bool:
        existing = ctx.manifest.get_step(step_name)
        retry_count = existing.retry_count if existing else 0
        while retry_count <= self.max_retries:
            try:
                # Build and write step-local input (orchestrator is sole writer of artifacts)
                step_input = build_step_input(ctx, step_name, domain)
                input_path = str(ctx.write_step_payload(step_name, "input", step_input))
                ctx.start_step(step_name, input_path=input_path)
                step_fn = self._load_step(step_name)
                result = step_fn(ctx, step_input, self.config, self.prompt_loader)
                errors = self._validate_result(step_name, result)
                if errors:
                    raise ValueError('; '.join(errors))
                # Orchestrator writes output.json and meta.json — steps do not write these
                output_path_obj = ctx.write_step_payload(step_name, "output", result.get("data", {}))
                ctx.write_step_payload(step_name, "meta", {"counts": result.get("counts", {})})
                ctx.complete_step(step_name, output_path=str(output_path_obj), counts=result.get("counts", {}))
                logger.info("step.completed", step=step_name, counts=result.get("counts", {}))
                return True
            except Exception as exc:
                retry_count += 1
                ctx.fail_step(step_name, type(exc).__name__, str(exc))
                if retry_count > self.max_retries:
                    logger.error('step.failed_permanently', step=step_name, error=str(exc))
                    return False
                record = ctx.manifest.get_step(step_name)
                if record:
                    record.status = 'pending'
                    ctx.manifest.status = 'running'
                    ctx.manifest.upsert_step(record)
                    ctx.save()
        return False

    def _validate_result(self, step_name: str, result: dict) -> list[str]:
        data = result.get('data')
        errors: list[str] = []
        errors.extend(self.validator.validate_step_output(step_name, result))
        errors.extend(validate_business_rules(step_name, data))
        errors.extend(run_content_checks(step_name, data))
        errors.extend(run_quality_checks(step_name, data))
        return errors

    def _load_step(self, step_name: str):
        """Load step module via step_registry — registry is the single source of truth."""
        spec = get_step_spec(step_name)
        mod = importlib.import_module(spec.module_path)
        return mod.run
