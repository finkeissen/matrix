"""
prompts/loader.py — Prompt loading, hashing, and variant resolution for v18.

Key design:
- Prompts live in prompts/templates/<step>/<version>.md
- Every prompt is SHA256-hashed at load time
- Hash becomes part of task_id for novelty guard → prompt change = cache miss
- Variant resolution: v2.md > v1.md (active) > FileNotFoundError
- All loaded prompts are cached in-process

prompt_versions dict format (written into run manifest):
    {"01_scope": "v1", "03_categories": "v1", ...}

prompt_hashes dict format:
    {"01_scope": "sha256:abc123...", ...}
"""

import hashlib
from pathlib import Path
from typing import Optional

from ..config import Config
from ..logging_setup import get_logger

logger = get_logger(__name__)

# Steps that have no prompt (deterministic logic only)
DETERMINISTIC_STEPS = {"06_deduplication"}


class PromptLoader:
    def __init__(self, config: Config):
        self._templates_dir = config.prompts_dir
        self._cache: dict[str, tuple[str, str, str]] = {}  # key → (text, version, hash)

    # ── Public API ─────────────────────────────────────────────────────────

    def load(self, step_name: str, variant: str = "") -> tuple[str, str, str]:
        """
        Load prompt for a step. Returns (text, version, sha256_hash).

        Resolution order:
          1. <step>/<variant>.md   if variant given
          2. <step>/v1.md          (default active version)

        Raises FileNotFoundError if no prompt file exists.
        """
        cache_key = f"{step_name}:{variant}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        path, version = self._resolve(step_name, variant)
        text = path.read_text(encoding="utf-8").strip()
        h = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

        self._cache[cache_key] = (text, version, h)
        logger.info("prompt.loaded", step=step_name, version=version, hash=h[:16] + "...")
        return text, version, h

    def get_hash(self, step_name: str, variant: str = "") -> str:
        _, _, h = self.load(step_name, variant)
        return h

    def resolve_versions(
        self, steps: list[str], variant: str = ""
    ) -> tuple[dict, dict]:
        """
        Build prompt_versions and prompt_hashes dicts for the run manifest.
        Deterministic steps are silently skipped.
        """
        versions: dict = {}
        hashes: dict = {}
        for step in steps:
            if step in DETERMINISTIC_STEPS:
                continue
            try:
                _, ver, h = self.load(step, variant)
                versions[step] = ver
                hashes[step] = h
            except FileNotFoundError:
                logger.warning("prompt.not_found", step=step)
        return versions, hashes

    def invalidate_cache(self):
        self._cache.clear()

    # ── Internal ───────────────────────────────────────────────────────────

    def _resolve(self, step_name: str, variant: str) -> tuple[Path, str]:
        step_dir = self._templates_dir / step_name

        if variant:
            candidate = step_dir / f"{variant}.md"
            if candidate.exists():
                return candidate, variant
            logger.warning("prompt.variant_not_found", step=step_name, variant=variant,
                           fallback="v1")

        # Default: v1.md
        default = step_dir / "v1.md"
        if default.exists():
            return default, "v1"

        raise FileNotFoundError(
            f"No prompt file found for step '{step_name}' in {step_dir}.\n"
            f"Expected: {step_dir}/v1.md (or {step_dir}/{variant}.md)"
        )
