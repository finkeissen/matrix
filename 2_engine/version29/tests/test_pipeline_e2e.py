from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DummyManifest:
    run_id = "test_run_e2e"


class DummyCtx:
    def __init__(self, root: Path):
        self.root = root
        self.manifest = DummyManifest()

    def intermediate_dir(self) -> Path:
        path = self.root / "intermediate"
        path.mkdir(parents=True, exist_ok=True)
        return path


def test_categories_to_problem_generation_e2e(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]

    categories_module = _load_module(
        "step_03_categories",
        repo_root / "pipeline" / "steps" / "03_categories.py",
    )
    problem_generation_module = _load_module(
        "step_04_problem_generation",
        repo_root / "pipeline" / "steps" / "04_problem_generation.py",
    )

    def fake_load_taxonomy(self, domain):
        return []

    monkeypatch.setattr(
        categories_module.IngestionLoader,
        "load_taxonomy",
        fake_load_taxonomy,
    )

    ctx = DummyCtx(tmp_path)
    domain = "thermodynamics"
    config = None
    prompt_loader = None

    categories_result = categories_module.run(ctx, domain, config, prompt_loader)
    categories_path = Path(categories_result["output_path"])
    categories_payload = json.loads(categories_path.read_text(encoding="utf-8"))

    problem_result = problem_generation_module.run(ctx, domain, config, prompt_loader)
    problems_path = Path(problem_result["output_path"])
    problems = json.loads(problems_path.read_text(encoding="utf-8"))

    assert isinstance(problems, list)
    assert len(problems) == 3
    assert problem_result["counts"]["generated"] == 3
    assert problem_result["counts"]["categories"] == 3
    assert problem_result["counts"]["problems_per_category"] == 1

    statements = set()
    for problem in problems:
        assert problem["problem_id"].startswith("ap_")
        assert problem["category"] in categories_payload["categories"]
        assert problem["source_run_id"] == "test_run_e2e"
        assert problem["title"]
        assert problem["problem_statement"]
        assert problem["created_at"]
        assert problem["difficulty"] in {"easy", "medium", "hard", "expert"}
        statements.add(problem["problem_statement"])

    assert len(statements) == len(problems)


def test_problem_generation_rejects_invalid_problem_count_env(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    problem_generation_module = _load_module(
        "step_04_problem_generation_invalid_env",
        repo_root / "pipeline" / "steps" / "04_problem_generation.py",
    )

    ctx = DummyCtx(tmp_path)
    monkeypatch.setenv("PROBLEMS_PER_CATEGORY", "0")

    with pytest.raises(ValueError, match="PROBLEMS_PER_CATEGORY"):
        problem_generation_module.run(ctx, "thermodynamics", None, None)
