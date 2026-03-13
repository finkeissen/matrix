from __future__ import annotations

import json
from typing import Any


DIFFICULTY_WEIGHTS = {
    "expert": 4,
    "hard": 3,
    "medium": 2,
    "easy": 1,
}


def _problem_score(problem: dict[str, Any]) -> tuple[int, int, str, str]:
    statement = str(problem.get("problem_statement", ""))
    difficulty = str(problem.get("difficulty", "")).lower()
    return (
        DIFFICULTY_WEIGHTS.get(difficulty, 0),
        len(statement.split()),
        str(problem.get("category", "")),
        str(problem.get("title", "")),
    )


def run(ctx, domain, config, prompt_loader):
    input_path = ctx.intermediate_dir() / "06_deduplication.json"
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    accepted = payload.get("accepted", []) if isinstance(payload, dict) else payload

    ranked = sorted(accepted, key=_problem_score, reverse=True)

    output_path = ctx.intermediate_dir() / "07_ranking.json"
    output_path.write_text(json.dumps(ranked, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "data": ranked,
        "output_path": str(output_path),
        "counts": {"ranked": len(ranked)},
    }
