"""steps/01_scope.py — Step 01: Define subdomain boundaries."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from ..logging_setup import get_logger

logger = get_logger(__name__)


def run(ctx, step_input: dict, config, prompt_loader) -> dict:
    step_name = "01_scope"
    domain: str = step_input["domain"]

    prompt_text, version, prompt_hash = prompt_loader.load(step_name)
    prompt = prompt_text.format(domain=domain)

    logger.info(
        "step.llm_call",
        step=step_name,
        prompt_version=version,
        prompt_hash=prompt_hash[:16],
    )

    scope = _call_llm(config, prompt, domain)

    scope["_prompt_version"] = version
    scope["_prompt_hash"] = prompt_hash
    scope["_domain"] = domain

    return {
        "data": scope,
        "counts": {
            "boundaries": len(scope.get("boundaries", [])),
            "exclusions": len(scope.get("exclusions", [])),
        },
    }


def _call_llm(config, prompt: str, domain: str) -> dict:
    try:
        import requests

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

        if config.lm_model:
            payload["model"] = config.lm_model

        resp = requests.post(
            config.lm_url,
            json=payload,
            timeout=config.request_timeout,
        )
        resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"].strip()

        # Remove reasoning blocks (<think>...</think>)
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()

        # Remove markdown code fences
        content = re.sub(r"```json|```", "", content).strip()

        # Extract first JSON object
        m = re.search(r"\{.*\}", content, flags=re.S)
        if not m:
            raise ValueError("No JSON object found in LLM response")

        return json.loads(m.group(0))

    except Exception as exc:
        logger.warning("step.llm_fallback", reason=str(exc))

        return {
            "boundaries": [
                f"core principles of {domain}",
                f"canonical problem families in {domain}",
                f"assessment-ready tasks for {domain}",
            ],
            "exclusions": [
                f"history of {domain}",
                f"biographical content unrelated to {domain}",
            ],
            "confidence_score": 0.8,
            "generated_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        }
