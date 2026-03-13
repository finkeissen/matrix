"""
config.py — All configuration via environment variables / .env file.
No hardcoded values anywhere in the codebase.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)

DATA_DIR = _PROJECT_ROOT / "data"


@dataclass
class Config:
    # LLM
    lm_url: str = "http://localhost:1234/v1/chat/completions"
    lm_model: str = "loaded"
    request_timeout: int = 120
    default_retries: int = 2

    # Thresholds
    scope_confidence_threshold: float = 0.70
    atomicity_failure_threshold: float = 0.20
    max_clarification_rounds: int = 2
    hallucination_sample_max: int = 60

    # Prompt
    prompt_variant: str = ""

    # Pipeline
    pipeline_version: str = "18.0.0"
    telemetry_enabled: bool = True

    # Paths
    data_dir: Path = DATA_DIR

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            lm_url=os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions"),
            lm_model=os.getenv("LM_STUDIO_MODEL", "loaded"),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "120")),
            default_retries=int(os.getenv("DEFAULT_RETRIES", "2")),
            scope_confidence_threshold=float(os.getenv("SCOPE_CONFIDENCE_THRESHOLD", "0.70")),
            atomicity_failure_threshold=float(os.getenv("ATOMICITY_FAILURE_THRESHOLD", "0.20")),
            max_clarification_rounds=int(os.getenv("MAX_CLARIFICATION_ROUNDS", "2")),
            hallucination_sample_max=int(os.getenv("HALLUCINATION_SAMPLE_MAX", "60")),
            prompt_variant=os.getenv("PROMPT_VARIANT", ""),
            telemetry_enabled=os.getenv("TELEMETRY_ENABLED", "true").lower() == "true",
            data_dir=Path(os.getenv("DATA_DIR", str(DATA_DIR))),
        )

    @property
    def runs_dir(self) -> Path:
        p = self.data_dir / "runs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def registry_dir(self) -> Path:
        return self.data_dir / "registry"

    @property
    def seeds_dir(self) -> Path:
        return self.data_dir / "seeds"

    @property
    def prompts_dir(self) -> Path:
        return Path(__file__).parent / "prompts" / "templates"

    @property
    def schema_dir(self) -> Path:
        return Path(__file__).parent / "schema"

    def model_config(self) -> dict:
        return {
            "model": self.lm_model,
            "url": self.lm_url,
            "timeout": self.request_timeout,
        }
