from __future__ import annotations

import pytest

from real_time_guardrails.core.config import REQUIRED_ENV_VARS, GuardrailsConfig
from real_time_guardrails.core.exceptions import ConfigError


def test_from_env_loads_required_vars(filled_env: dict[str, str]) -> None:
    cfg = GuardrailsConfig.from_env()
    assert cfg.api_key == filled_env["WATSONX_APIKEY"]
    assert cfg.service_instance_id == filled_env["WXG_SERVICE_INSTANCE_ID"]
    assert cfg.project_id == filled_env["WXG_PROJECT_ID"]
    assert cfg.watsonx_url == "https://us-south.ml.cloud.ibm.com"
    assert cfg.judge_model_id == "llama-3-3-70b-instruct"


@pytest.mark.parametrize("missing", REQUIRED_ENV_VARS)
def test_from_env_raises_on_missing(
    missing: str, monkeypatch: pytest.MonkeyPatch, filled_env: dict[str, str]
) -> None:
    monkeypatch.delenv(missing, raising=False)
    with pytest.raises(ConfigError) as excinfo:
        GuardrailsConfig.from_env()
    assert missing in str(excinfo.value)


def test_from_env_accepts_optional_overrides(
    monkeypatch: pytest.MonkeyPatch, filled_env: dict[str, str]
) -> None:
    monkeypatch.setenv("WATSONX_URL", "https://custom.example.com")
    monkeypatch.setenv("WXG_JUDGE_MODEL_ID", "custom-model")
    cfg = GuardrailsConfig.from_env()
    assert cfg.watsonx_url == "https://custom.example.com"
    assert cfg.judge_model_id == "custom-model"


def test_from_env_accepts_explicit_mapping(clean_env: None) -> None:
    cfg = GuardrailsConfig.from_env(
        env={
            "WATSONX_APIKEY": "x",
            "WXG_SERVICE_INSTANCE_ID": "y",
            "WXG_PROJECT_ID": "z",
        }
    )
    assert (cfg.api_key, cfg.service_instance_id, cfg.project_id) == ("x", "y", "z")


def test_from_env_treats_empty_string_as_missing(clean_env: None) -> None:
    with pytest.raises(ConfigError):
        GuardrailsConfig.from_env(
            env={
                "WATSONX_APIKEY": "",
                "WXG_SERVICE_INSTANCE_ID": "y",
                "WXG_PROJECT_ID": "z",
            }
        )


def test_project_id_is_optional(clean_env: None) -> None:
    cfg = GuardrailsConfig.from_env(
        env={"WATSONX_APIKEY": "x", "WXG_SERVICE_INSTANCE_ID": "y"}
    )
    assert cfg.project_id is None
    assert cfg.api_key == "x"


def test_project_id_empty_string_treated_as_none(clean_env: None) -> None:
    cfg = GuardrailsConfig.from_env(
        env={
            "WATSONX_APIKEY": "x",
            "WXG_SERVICE_INSTANCE_ID": "y",
            "WXG_PROJECT_ID": "",
        }
    )
    assert cfg.project_id is None


def test_project_id_not_in_required_env_vars() -> None:
    assert "WXG_PROJECT_ID" not in REQUIRED_ENV_VARS
