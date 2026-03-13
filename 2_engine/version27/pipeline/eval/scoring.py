from __future__ import annotations

from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _safe_ratio(num: float, den: float) -> float:
    return 0.0 if den <= 0 else num / den


def score_step(step: str, metrics: dict[str, Any], run_health: dict[str, Any]) -> float:
    """
    Step-specific pragmatic scoring based on the available run artifacts.

    This function does not score polished prose. It scores output that is useful downstream.
    """
    status = str(run_health.get("status", "")).lower()
    health_score = float(run_health.get("score", 0)) / 100.0

    generated = float(metrics.get("generated", 0) or 0)
    accepted = float(metrics.get("accepted", 0) or 0)
    duplicates = float(metrics.get("duplicates", 0) or 0)
    rejected_content = float(metrics.get("rejected_content", 0) or 0)
    acceptance_rate = metrics.get("acceptance_rate")
    acceptance_rate = float(acceptance_rate) if acceptance_rate is not None else _safe_ratio(accepted, generated)
    duplicate_rate = _safe_ratio(duplicates, generated)
    rejection_rate = _safe_ratio(rejected_content, generated)

    if status == "healthy":
        status_score = 1.0
    elif status == "degraded":
        status_score = 0.6
    else:
        status_score = 0.0

    if step == "01_scope":
        score = (
            0.45 * status_score +
            0.35 * health_score +
            0.20 * acceptance_rate
        )
    elif step == "02_seed_expansion":
        coverage_proxy = clamp(_safe_ratio(generated, 3.0))
        score = (
            0.30 * status_score +
            0.25 * health_score +
            0.25 * coverage_proxy +
            0.20 * clamp(1.0 - duplicate_rate)
        )
    elif step == "03_categories":
        category_proxy = clamp(_safe_ratio(generated, 3.0))
        score = (
            0.35 * status_score +
            0.30 * health_score +
            0.20 * category_proxy +
            0.15 * acceptance_rate
        )
    elif step == "04_problem_generation":
        score = (
            0.25 * status_score +
            0.20 * health_score +
            0.30 * acceptance_rate +
            0.15 * clamp(1.0 - duplicate_rate) +
            0.10 * clamp(1.0 - rejection_rate)
        )
    elif step == "05_validation":
        score = (
            0.35 * status_score +
            0.25 * health_score +
            0.25 * acceptance_rate +
            0.15 * clamp(1.0 - rejection_rate)
        )
    else:
        score = (
            0.50 * status_score +
            0.50 * health_score
        )

    return round(clamp(score), 4)


def summarize_unsuitability(step: str, score: float, metrics: dict[str, Any], run_health: dict[str, Any]) -> str:
    status = str(run_health.get("status", "")).lower()
    generated = float(metrics.get("generated", 0) or 0)
    accepted = float(metrics.get("accepted", 0) or 0)
    duplicates = float(metrics.get("duplicates", 0) or 0)
    rejected_content = float(metrics.get("rejected_content", 0) or 0)
    acceptance_rate = metrics.get("acceptance_rate")
    acceptance_rate = float(acceptance_rate) if acceptance_rate is not None else _safe_ratio(accepted, generated)

    reasons: list[str] = []
    if status not in {"healthy", "degraded"}:
        reasons.append("run_status_unhealthy")
    if acceptance_rate < 0.5:
        reasons.append("low_acceptance_rate")
    if generated > 0 and duplicates / generated > 0.3:
        reasons.append("high_duplicate_rate")
    if generated > 0 and rejected_content / generated > 0.3:
        reasons.append("high_rejection_rate")
    if score < 0.4:
        reasons.append("overall_score_too_low")

    return ", ".join(reasons) if reasons else "step_under_threshold"
