from __future__ import annotations
import os, tomllib
from typing import Any, Dict

def load_config(path: str) -> Dict[str, Any]:
    with open(path, "rb") as f:
        return tomllib.load(f)

def resolve_repo_root(cfg: Dict[str, Any], config_path: str) -> str:
    root = cfg.get("repo", {}).get("root", ".")
    base_dir = os.path.dirname(os.path.abspath(config_path))
    return os.path.abspath(os.path.join(base_dir, root))
