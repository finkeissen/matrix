"""
steps/01_scope.py — Step 01: Define subdomain boundaries.

Step contract:
  input:  domain name (str)
  output: scope.json with boundaries, exclusions, confidence_score
  schema: schema/scope.schema.json

Every step follows this pattern:
  1. load_prompt() → get text + hash
  2. call LLM
  3. validate output structure
  4. write to intermediate/<step>.json
  5. return {"data": ..., "output_path": ..., "counts": {...}}
"""

import json
from pathlib import Path

from ..logging_setup import get_logger

logger = get_logger(__name__)


def run(ctx, domain: str, config, prompt_loader) -> dict:
    """Execute step 01_scope. Returns result dict for orchestrator."""
    step_name = "01_scope"
    out_dir = ctx.intermediate_dir()
    out_path = out_dir / f"{step_name}.json"

    # Load prompt (versioned + hashed)
    prompt_text, version, prompt_hash = prompt_loader.load(step_name)
    prompt = prompt_text.format(domain=domain)

    logger.info("step.llm_call", step=step_name, prompt_version=version, prompt_hash=prompt_hash[:16])

    # LLM call (using config.lm_url etc.)
    scope = _call_llm(config, prompt)

    # Attach provenance
    scope["_prompt_version"] = version
    scope["_prompt_hash"] = prompt_hash
    scope["_domain"] = domain

    # Write output
    out_path.write_text(json.dumps(scope, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "data": scope,
        "output_path": str(out_path),
        "counts": {
            "boundaries": len(scope.get("boundaries", [])),
            "exclusions": len(scope.get("exclusions", [])),
        },
    }


def _call_llm(config, prompt: str) -> dict:
    """Call LLM endpoint and return parsed JSON response."""
    import requests

    payload = {
        "model": config.lm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    resp = requests.post(config.lm_url, json=payload, timeout=config.request_timeout)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    # Strip markdown fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content.strip())
