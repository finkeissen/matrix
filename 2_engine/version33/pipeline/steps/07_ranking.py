"""steps/07_ranking.py — Step 07: Rank deduplicated problems by quality score.

Deterministic step — no LLM call.

Reads:  step_input["deduplicated_problems"]
Returns: sorted problem list as data dict
"""
from __future__ import annotations

from typing import Any

DIFFICULTY_WEIGHTS = {
    "expert": 4,
    "hard":   3,
    "medium": 2,
    "easy":   1,
}


def _problem_score(problem: dict[str, Any]) -> int:
    statement = str(problem.get("problem_statement", ""))
    difficulty = str(problem.get("difficulty", "")).lower()
    return DIFFICULTY_WEIGHTS.get(difficulty, 0) * 4 + len(statement.split())


def run(ctx, step_input: dict, config, prompt_loader):
    problems: list[dict[str, Any]] = step_input.get("deduplicated_problems", [])

    if not problems:
        raise ValueError("07_ranking: deduplicated_problems is empty — nothing to rank")

    ranked = sorted(problems, key=_problem_score, reverse=True)
    for p in ranked:
        p["_rank_score"] = _problem_score(p)

    return {
        "data": ranked,
        "counts": {"ranked": len(ranked)},
    }
