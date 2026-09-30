from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from .exceptions import ConfigError


REQUIRED_ENV_VARS = (
    "WATSONX_APIKEY",
    "WXG_SERVICE_INSTANCE_ID",
)

# Required only to enable LLM-as-judge metrics (Answer Completeness, Conciseness,
# Tool Call Relevance). When unset, those 3 metrics are simply omitted from the
# registry and the remaining 25 metrics work normally.
OPTIONAL_ENV_VARS = ("WXG_PROJECT_ID",)


@dataclass(frozen=True)
class GuardrailsConfig:
    """Runtime configuration for the guardrails evaluator.

    ``project_id`` is optional: it gates the 3 LLM-as-judge metrics (which call
    watsonx.ai-hosted foundation models). When ``None``, those metrics are
    skipped during registry construction.

    The dataclass is structured so a future ``GuardrailsConfig(api_key=...,
    service_instance_id=..., project_id=...)`` constructor can be added without
    breaking the env-var path.
    """

    api_key: str
    service_instance_id: str
    project_id: str | None = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    judge_model_id: str = "llama-3-3-70b-instruct"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "GuardrailsConfig":
        env = env if env is not None else os.environ
        missing = [name for name in REQUIRED_ENV_VARS if not env.get(name)]
        if missing:
            raise ConfigError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
                + ". Set them before instantiating GuardrailsEvaluator."
            )
        return cls(
            api_key=env["WATSONX_APIKEY"],
            service_instance_id=env["WXG_SERVICE_INSTANCE_ID"],
            project_id=env.get("WXG_PROJECT_ID") or None,
            watsonx_url=env.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            judge_model_id=env.get("WXG_JUDGE_MODEL_ID", "llama-3-3-70b-instruct"),
        )

    def export_to_env(self) -> None:
        """Set the env vars the watsonx SDK reads internally.

        Called once at evaluator construction so downstream SDK code finds
        credentials without further plumbing.
        """
        os.environ["WATSONX_APIKEY"] = self.api_key
        os.environ["WXG_SERVICE_INSTANCE_ID"] = self.service_instance_id
