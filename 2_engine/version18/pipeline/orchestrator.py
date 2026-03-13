"""
orchestrator.py — Pipeline Orchestrator v18.

Core responsibilities:
1. Build RunContext (new run or resume)
2. Dispatch steps in order, respecting resume state
3. Enforce: validate output after every step before proceeding
4. Finalize run with metrics and report

Resume logic:
- completed steps → skipped
- failed steps → retried (up to MAX_RETRIES)
- pending/running steps → executed
"""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import Config
from .logging_setup import get_logger
from .run_context import RunContext
from .prompts.loader import PromptLoader
from .validation.schema_validator import SchemaValidator
from .eval.reports import ReportGenerator
from .eval.metrics import MetricsCollector

logger = get_logger(__name__)

ALL_STEPS = [
    "01_scope",
    "02_seed_expansion",
    "03_categories",
    "04_problem_generation",
    "05_validation",
    "06_deduplication",
    "07_ranking",
    "08_export",
]

MAX_RETRIES = 2


def _make_run_id(domain: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Find next available index
    from .config import Config
    config = Config.from_env()
    existing = list(config.runs_dir.glob(f"{ts}_*_{domain}"))
    idx = len(existing) + 1
    return f"{ts}_{idx:03d}_{domain}"


class Orchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.prompt_loader = PromptLoader(config)
        self.validator = SchemaValidator(config)

    def run(
        self,
        domain: str,
        prompt_variant: str = "",
        steps: Optional[list[str]] = None,
        dry_run: bool = False,
        run_id: Optional[str] = None,
    ) -> Optional[str]:
        active_steps = steps or ALL_STEPS[:]
        run_id = run_id or _make_run_id(domain)
        run_dir = self.config.runs_dir / run_id

        if dry_run:
            print(f"[dry-run] Would execute {len(active_steps)} steps for domain '{domain}':")
            for s in active_steps:
                print(f"  → {s}")
            return None

        logger.info("run.start", run_id=run_id, domain=domain, steps=active_steps)

        # Load prompt versions before execution
        prompt_versions, prompt_hashes = self.prompt_loader.resolve_versions(
            active_steps, variant=prompt_variant
        )

        ctx = RunContext.create(
            run_id=run_id,
            domain=domain,
            run_dir=run_dir,
            model_config=self.config.model_config(),
        )
        ctx.manifest.prompt_versions = prompt_versions
        ctx.manifest.prompt_hashes = prompt_hashes
        ctx.save()

        return self._dispatch_steps(ctx, active_steps)

    def resume(self, run_id: str) -> Optional[str]:
        run_dir = self.config.runs_dir / run_id
        ctx = RunContext.load(run_dir)
        if ctx is None:
            logger.error("resume.not_found", run_id=run_id)
            print(f"[error] Run not found: {run_id}")
            return None

        domain = ctx.manifest.domain
        logger.info("run.resume", run_id=run_id, domain=domain)
        print(f"\nResuming run: {run_id} (domain: {domain})")

        completed = [s.name for s in ctx.manifest.steps if s.status == "completed"]
        remaining = [s for s in ALL_STEPS if s not in completed]
        print(f"Skipping completed steps: {completed}")
        print(f"Resuming from: {remaining[0] if remaining else '(all done)'}")

        ctx.manifest.status = "running"
        ctx.save()

        return self._dispatch_steps(ctx, remaining)

    def _dispatch_steps(self, ctx: RunContext, steps: list[str]) -> Optional[str]:
        run_id = ctx.manifest.run_id
        domain = ctx.manifest.domain

        for step_name in steps:
            # Resume: skip if already completed
            if ctx.is_step_completed(step_name):
                ctx.skip_step(step_name)
                logger.info("step.skipped", step=step_name, reason="already_completed")
                print(f"  ○ {step_name}: skipped (already completed)")
                continue

            print(f"\n{'='*60}")
            print(f"  STEP: {step_name}")
            print(f"{'='*60}")

            success = self._run_step_with_retry(ctx, step_name, domain)
            if not success:
                logger.error("pipeline.halted", step=step_name)
                ctx.finalize(status="failed")
                print(f"\n[HALT] Pipeline stopped at: {step_name}")
                return None

        # All steps done — generate final metrics and report
        metrics = MetricsCollector(self.config).collect(ctx)
        ctx.finalize(status="completed", metrics=metrics)
        ReportGenerator(self.config).generate(ctx)

        logger.info("run.completed", run_id=run_id, metrics=metrics)
        return run_id

    def _run_step_with_retry(self, ctx: RunContext, step_name: str, domain: str) -> bool:
        existing = ctx.manifest.get_step(step_name)
        retry_count = existing.retry_count if existing else 0

        while retry_count <= MAX_RETRIES:
            try:
                step_fn = self._load_step(step_name)
                result = step_fn(ctx, domain, self.config, self.prompt_loader)

                # Hard validation after every step
                errors = self.validator.validate_step_output(step_name, result)
                if errors:
                    raise ValueError(f"Output validation failed: {errors}")

                output_path = result.get("output_path")
                counts = result.get("counts", {})
                ctx.complete_step(step_name, output_path=output_path, counts=counts)

                logger.info(
                    "step.completed",
                    step=step_name,
                    counts=counts,
                    output=output_path,
                )
                print(f"  ✓ {step_name}: completed {counts}")
                return True

            except Exception as e:
                retry_count += 1
                error_type = type(e).__name__
                error_msg = str(e)
                logger.error(
                    "step.failed",
                    step=step_name,
                    error_type=error_type,
                    error_message=error_msg,
                    retry=retry_count,
                )
                if retry_count <= MAX_RETRIES:
                    print(f"  ✗ {step_name}: {error_type} — retrying ({retry_count}/{MAX_RETRIES})")
                    ctx.fail_step(step_name, error_type, error_msg)
                    # Reset status for retry
                    record = ctx.manifest.get_step(step_name)
                    if record:
                        record.status = "pending"
                        ctx.manifest.upsert_step(record)
                        ctx.save()
                else:
                    ctx.fail_step(step_name, error_type, error_msg)
                    print(f"  ✗ {step_name}: failed after {MAX_RETRIES} retries — {error_msg}")
                    return False

        return False

    def _load_step(self, step_name: str):
        """Dynamically import step module and return its run() function."""
        import importlib
        module_name = f"pipeline.steps.{step_name.replace('-', '_')}"
        try:
            mod = importlib.import_module(module_name)
            return mod.run
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Cannot load step '{step_name}': {e}")
