"""
config.py — all configuration via environment variables / .env file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)

DATA_DIR = _PROJECT_ROOT / "data"
INGESTION_DIR = _PROJECT_ROOT / "ingestion"


@dataclass
class Config:
    lm_url: str = "http://localhost:1234/v1/chat/completions"
    lm_model: str | None = None
    request_timeout: int = 120
    default_retries: int = 2

    scope_confidence_threshold: float = 0.70
    atomicity_failure_threshold: float = 0.20
    max_clarification_rounds: int = 2
    hallucination_sample_max: int = 60

    prompt_variant: str = ""
    pipeline_version: str = "19.0.0"
    telemetry_enabled: bool = True

    data_dir: Path = DATA_DIR
    ingestion_dir: Path = INGESTION_DIR

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            lm_url=os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions"),
            lm_model=os.getenv("LM_STUDIO_MODEL"),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "120")),
            default_retries=int(os.getenv("DEFAULT_RETRIES", "2")),
            scope_confidence_threshold=float(os.getenv("SCOPE_CONFIDENCE_THRESHOLD", "0.70")),
            atomicity_failure_threshold=float(os.getenv("ATOMICITY_FAILURE_THRESHOLD", "0.20")),
            max_clarification_rounds=int(os.getenv("MAX_CLARIFICATION_ROUNDS", "2")),
            hallucination_sample_max=int(os.getenv("HALLUCINATION_SAMPLE_MAX", "60")),
            prompt_variant=os.getenv("PROMPT_VARIANT", ""),
            telemetry_enabled=os.getenv("TELEMETRY_ENABLED", "true").lower() == "true",
            data_dir=Path(os.getenv("DATA_DIR", str(DATA_DIR))),
            ingestion_dir=Path(os.getenv("INGESTION_DIR", str(INGESTION_DIR))),
        )

    @property
    def runs_dir(self) -> Path:
        p = self.data_dir / "runs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def registry_dir(self) -> Path:
        p = self.data_dir / "registry"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def prompts_dir(self) -> Path:
        return Path(__file__).parent / "prompts" / "templates"

    @property
    def schema_dir(self) -> Path:
        return Path(__file__).parent / "schema"

    @property
    def ingestion_seeds_dir(self) -> Path:
        p = self.ingestion_dir / "seeds"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def ingestion_rules_dir(self) -> Path:
        p = self.ingestion_dir / "rules"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def ingestion_taxonomy_dir(self) -> Path:
        p = self.ingestion_dir / "taxonomy"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def ingestion_imports_dir(self) -> Path:
        p = self.ingestion_dir / "imports"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def model_config(self) -> dict:
        return {
            "model": self.lm_model,
            "url": self.lm_url,
            "timeout": self.request_timeout,
        }
