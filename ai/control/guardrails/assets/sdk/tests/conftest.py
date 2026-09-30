from __future__ import annotations

import os
from typing import Iterator

import pytest


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Strip all WATSONX_*, WXG_*, GUARDRAILS_* env vars for the test."""
    for key in list(os.environ):
        if (
            key.startswith("WATSONX_")
            or key.startswith("WXG_")
            or key.startswith("GUARDRAILS_")
        ):
            monkeypatch.delenv(key, raising=False)
    yield


@pytest.fixture
def filled_env(monkeypatch: pytest.MonkeyPatch, clean_env: None) -> dict[str, str]:
    env = {
        "WATSONX_APIKEY": "test-key",
        "WXG_SERVICE_INSTANCE_ID": "test-instance",
        "WXG_PROJECT_ID": "test-project",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return env
