from __future__ import annotations

import json
from pathlib import Path

from pipeline.steps import __path__  # noqa: F401
import importlib


class DummyCtx:
    def __init__(self, root: Path):
        self.root = root

    def intermediate_dir(self) -> Path:
        path = self.root / "intermediate"
        path.mkdir(parents=True, exist_ok=True)
        return path


def test_ranking_prefers_higher_difficulty_and_richer_statement(tmp_path):
    ranking = importlib.import_module("pipeline.steps.07_ranking")
    ctx = DummyCtx(tmp_path)
    payload = {
        "accepted": [
            {
                "problem_id": "ap_easy",
                "title": "Easy item",
                "category": "alpha",
                "difficulty": "easy",
                "problem_statement": "short statement",
            },
            {
                "problem_id": "ap_expert",
                "title": "Expert item",
                "category": "alpha",
                "difficulty": "expert",
                "problem_statement": "this statement is much longer and should rank above the easy one",
            },
            {
                "problem_id": "ap_hard",
                "title": "Hard item",
                "category": "beta",
                "difficulty": "hard",
                "problem_statement": "a medium length statement for a hard problem",
            },
        ]
    }
    input_path = ctx.intermediate_dir() / "06_deduplication.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    result = ranking.run(ctx, "thermodynamics", None, None)
    ranked = result["data"]

    assert [item["problem_id"] for item in ranked] == ["ap_expert", "ap_hard", "ap_easy"]
