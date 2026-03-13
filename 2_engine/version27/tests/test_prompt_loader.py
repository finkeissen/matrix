"""
tests/test_prompt_loader.py — Tests for PromptLoader.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from pipeline.prompts.loader import PromptLoader


@pytest.fixture
def tmp_config(tmp_path):
    """Create a temporary config with fake prompt templates."""
    class FakeConfig:
        prompts_dir = tmp_path / "templates"
        schema_dir = tmp_path / "schema"

    # Create v1.md for step 01_scope
    step_dir = tmp_path / "templates" / "01_scope"
    step_dir.mkdir(parents=True)
    (step_dir / "v1.md").write_text("Define scope for domain: {domain}", encoding="utf-8")
    (step_dir / "v2.md").write_text("Carefully define scope for: {domain}", encoding="utf-8")

    return FakeConfig()


def test_loads_default_v1(tmp_config):
    loader = PromptLoader(tmp_config)
    text, version, h = loader.load("01_scope")
    assert version == "v1"
    assert "Define scope" in text
    assert h.startswith("sha256:")


def test_loads_variant_v2(tmp_config):
    loader = PromptLoader(tmp_config)
    text, version, h = loader.load("01_scope", variant="v2")
    assert version == "v2"
    assert "Carefully" in text


def test_different_versions_have_different_hashes(tmp_config):
    loader = PromptLoader(tmp_config)
    _, _, h1 = loader.load("01_scope", variant="v1")
    _, _, h2 = loader.load("01_scope", variant="v2")
    assert h1 != h2


def test_missing_step_raises(tmp_config):
    loader = PromptLoader(tmp_config)
    with pytest.raises(FileNotFoundError):
        loader.load("99_nonexistent")


def test_cache_is_used(tmp_config):
    loader = PromptLoader(tmp_config)
    _, _, h1 = loader.load("01_scope")
    # Modify file — cache should still return old value
    (tmp_config.prompts_dir / "01_scope" / "v1.md").write_text("CHANGED", encoding="utf-8")
    _, _, h2 = loader.load("01_scope")
    assert h1 == h2  # cache hit, file change ignored


def test_invalidate_cache_reloads(tmp_config):
    loader = PromptLoader(tmp_config)
    _, _, h1 = loader.load("01_scope")
    (tmp_config.prompts_dir / "01_scope" / "v1.md").write_text("CHANGED", encoding="utf-8")
    loader.invalidate_cache()
    _, _, h2 = loader.load("01_scope")
    assert h1 != h2  # reloaded after invalidation


def test_resolve_versions_skips_deterministic():
    class Cfg:
        prompts_dir = Path("/nonexistent")
    loader = PromptLoader(Cfg())
    versions, hashes = loader.resolve_versions(["06_deduplication"])
    assert "06_deduplication" not in versions
    assert "06_deduplication" not in hashes
