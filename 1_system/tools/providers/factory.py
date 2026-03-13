from __future__ import annotations
from typing import Any, Dict
from .lm_studio_openai_compat import LmStudioOpenAICompatProvider

def make_provider(cfg: Dict[str, Any]):
    p = cfg.get("provider", {})
    ptype = p.get("type")
    if ptype == "lm_studio_openai_compat":
        return LmStudioOpenAICompatProvider(
            base_url=p["base_url"],
            api_key=p.get("api_key",""),
            timeout_seconds=int(p.get("timeout_seconds",120)),
        )
    raise ValueError(f"Unknown provider.type: {ptype}")
