"""
prompt_loader.py — Prompt versioning, loading, and hash resolution.

Prompts live in pipeline/prompts/<step_name>.md (active version)
and pipeline/prompts/<step_name>.v2.md etc. (variants for A/B tests).

Every prompt text is SHA256-hashed at load time. The hash becomes part of
the task_id for Novelty Guard — a prompt change causes a cache miss and
forces new generation, even if all data inputs are identical.

Usage:
    from prompt_loader import load_prompt, get_prompt_registry_entry

    text, meta = load_prompt("01_scope")
    prompt_str = text.format(subdomain_label="Algebra", ...)
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_PIPELINE_ROOT = Path(__file__).parent
_PROMPTS_DIR   = _PIPELINE_ROOT / "prompts"
_REGISTRY_PATH = _PIPELINE_ROOT / "prompt_registry.json"

# Optional env override for variant (e.g. PROMPT_VARIANT=v2 → loads <step>.v2.md)
_GLOBAL_VARIANT = os.environ.get("PROMPT_VARIANT", "").strip()

_prompt_cache: dict[str, tuple[str, dict]] = {}   # key → (text, meta)
_registry_cache: Optional[dict] = None


# ── Registry ──────────────────────────────────────────────────────────────────

def _load_registry() -> dict:
    global _registry_cache
    if _registry_cache is not None:
        return _registry_cache
    if _REGISTRY_PATH.exists():
        with open(_REGISTRY_PATH) as f:
            _registry_cache = json.load(f)
    else:
        _registry_cache = {"version": "14.0.0", "prompts": {}}
    return _registry_cache


def _save_registry(reg: dict) -> None:
    global _registry_cache
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_REGISTRY_PATH, "w") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
    _registry_cache = reg


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


# ── Prompt file resolution ────────────────────────────────────────────────────

def _resolve_prompt_path(step_name: str, variant: str = "") -> Path:
    """
    Resolution order:
    1. <step_name>.<variant>.md  if variant given
    2. <step_name>.md            (active version)
    Raises FileNotFoundError if neither exists.
    """
    v = variant or _GLOBAL_VARIANT
    if v:
        candidate = _PROMPTS_DIR / f"{step_name}.{v}.md"
        if candidate.exists():
            return candidate
        # Fall back to active version with a warning
        import sys
        print(f"  [prompt_loader] variant '{v}' not found for {step_name} — using active",
              file=sys.stderr)

    active = _PROMPTS_DIR / f"{step_name}.md"
    if not active.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {active}\n"
            f"Expected: pipeline/prompts/{step_name}.md\n"
            f"All LLM steps require a prompt file."
        )
    return active


# ── Main public API ───────────────────────────────────────────────────────────

def load_prompt(step_name: str, variant: str = "") -> tuple[str, dict]:
    """
    Load prompt text for a step. Returns (text, meta).

    meta = {
        "step":    step_name,
        "file":    "01_scope.md",
        "variant": "" | "v2" | ...,
        "hash":    "sha256:...",
        "loaded_at": "2026-03-07T...",
    }

    Result is cached in-process. Changing a .md file requires process restart
    (or call invalidate_prompt_cache()).
    """
    cache_key = f"{step_name}:{variant or _GLOBAL_VARIANT}"
    if cache_key in _prompt_cache:
        return _prompt_cache[cache_key]

    path = _resolve_prompt_path(step_name, variant)
    text = path.read_text(encoding="utf-8").strip()
    h    = _sha256_text(text)

    meta = {
        "step":       step_name,
        "file":       path.name,
        "variant":    variant or _GLOBAL_VARIANT or "active",
        "hash":       h,
        "loaded_at":  datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Update registry entry
    reg = _load_registry()
    reg.setdefault("prompts", {})[step_name] = {
        "active_file":   path.name,
        "active_hash":   h,
        "active_variant": meta["variant"],
        "last_loaded":   meta["loaded_at"],
    }
    _save_registry(reg)

    _prompt_cache[cache_key] = (text, meta)
    return text, meta


def get_prompt_hash(step_name: str, variant: str = "") -> str:
    """Return just the hash for task_id construction."""
    _, meta = load_prompt(step_name, variant)
    return meta["hash"]


def get_prompt_registry_entry(step_name: str) -> Optional[dict]:
    """Return registry metadata for a step (or None if never loaded)."""
    reg = _load_registry()
    return reg.get("prompts", {}).get(step_name)


def invalidate_prompt_cache() -> None:
    """Force reload of all prompts on next access (useful in tests)."""
    global _prompt_cache, _registry_cache
    _prompt_cache = {}
    _registry_cache = None


def build_prompt_versions(steps: list[str], variant: str = "") -> dict:
    """
    Build the prompt_versions dict for run_record.json.
    Called by orchestrator before dispatch.

    Returns: {step_name: {file, variant, hash}}
    """
    versions = {}
    for step in steps:
        try:
            _, meta = load_prompt(step, variant)
            versions[step] = {
                "file":    meta["file"],
                "variant": meta["variant"],
                "hash":    meta["hash"],
            }
        except FileNotFoundError:
            # Deterministic steps have no prompt file — skip silently
            pass
    return versions
