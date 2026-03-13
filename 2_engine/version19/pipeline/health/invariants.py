"""Run invariants checked after validation and at run finalization."""
from __future__ import annotations

def check_run_invariants(manifest: dict) -> list[str]:
    metrics = manifest.get('metrics', {})
    generated = metrics.get('generated', 0)
    accepted = metrics.get('accepted', 0)
    duplicates = metrics.get('duplicates', 0)
    errors: list[str] = []
    if generated and accepted + duplicates != generated:
        errors.append('count_mismatch')
    if generated == 0 and manifest.get('status') == 'completed':
        errors.append('no_problems_generated')
    acc_rate = metrics.get('acceptance_rate')
    if acc_rate is not None and generated and acc_rate < 0.25:
        errors.append('low_acceptance_rate')
    return errors
