"""Run invariants checked after validation and at run finalization."""
from __future__ import annotations


def check_run_invariants(manifest: dict) -> list[str]:
    metrics = manifest.get("metrics", {})
    generated = metrics.get("generated", 0) or 0
    accepted = metrics.get("accepted", 0) or 0
    duplicates = metrics.get("duplicates", 0) or 0
    acc_rate = metrics.get("acceptance_rate")

    status = manifest.get("status")
    steps = manifest.get("steps", [])

    errors: list[str] = []

    failed_steps = [step for step in steps if step.get("status") == "failed"]
    incomplete_steps = [
        step for step in steps if step.get("status") not in {"completed", "skipped", "failed"}
    ]

    if status == "completed" and failed_steps:
        errors.append("completed_with_failed_steps")

    if status == "completed" and incomplete_steps:
        errors.append("completed_with_incomplete_steps")

    if generated > 0 and accepted + duplicates != generated:
        errors.append("count_mismatch")

    if status == "completed" and generated == 0:
        errors.append("no_problems_generated")

    if acc_rate is not None and generated > 0 and acc_rate < 0.25:
        errors.append("low_acceptance_rate")

    return errors
