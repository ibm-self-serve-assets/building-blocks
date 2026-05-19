"""Tests for the LLM-as-judge metric factory functions.

Both factories ultimately call ``LLMAsJudgeMetric`` from the IBM SDK. Tests
mock the SDK so we can verify the kwargs we pass without needing watsonx.ai
credentials.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def stub_sdk(monkeypatch: pytest.MonkeyPatch):
    """Stub the few ibm_watsonx_gov symbols custom_metrics imports."""
    # Set up dummy modules
    for name in (
        "ibm_watsonx_gov",
        "ibm_watsonx_gov.entities",
        "ibm_watsonx_gov.entities.criteria",
        "ibm_watsonx_gov.metrics",
    ):
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        monkeypatch.setitem(sys.modules, name, mod)

    sys.modules["ibm_watsonx_gov.entities.criteria"].Option = MagicMock(name="Option")
    sys.modules["ibm_watsonx_gov.metrics"].LLMAsJudgeMetric = MagicMock(name="LLMAsJudgeMetric")
    return sys.modules["ibm_watsonx_gov.metrics"].LLMAsJudgeMetric


def test_build_answer_completeness_kwargs(stub_sdk) -> None:
    from real_time_guardrails.core.custom_metrics import build_answer_completeness

    judge = MagicMock(name="judge")
    build_answer_completeness(judge)
    call = stub_sdk.call_args
    assert call.kwargs["name"] == "answer_completeness"
    assert call.kwargs["llm_judge"] is judge
    assert call.kwargs["input_fields"] == ["input_text", "generated_text"]
    # Uses prompt_template style
    assert "prompt_template" in call.kwargs


def test_build_conciseness_kwargs(stub_sdk) -> None:
    from real_time_guardrails.core.custom_metrics import build_conciseness

    judge = MagicMock(name="judge")
    build_conciseness(judge)
    call = stub_sdk.call_args
    assert call.kwargs["name"] == "conciseness"
    assert call.kwargs["input_fields"] == ["generated_text"]


def test_build_criteria_judge_uses_criteria_style(stub_sdk) -> None:
    """build_criteria_judge passes criteria_description (not prompt_template)."""
    from real_time_guardrails.core.custom_metrics import build_criteria_judge

    judge = MagicMock(name="judge")
    Option = sys.modules["ibm_watsonx_gov.entities.criteria"].Option
    options = [
        Option(name="Yes", description="ok", value=1.0),
        Option(name="No", description="no", value=0.0),
    ]
    build_criteria_judge(
        name="helpfulness",
        display_name="Helpfulness",
        criteria_description="How helpful is the {generated_text}?",
        options=options,
        judge=judge,
    )
    call = stub_sdk.call_args
    assert call.kwargs["name"] == "helpfulness"
    assert call.kwargs["display_name"] == "Helpfulness"
    assert call.kwargs["criteria_description"] == "How helpful is the {generated_text}?"
    assert call.kwargs["options"] == options
    assert call.kwargs["output_field"] == "generated_text"
    assert call.kwargs["llm_judge"] is judge
    # criteria style does NOT use prompt_template
    assert "prompt_template" not in call.kwargs


def test_build_criteria_judge_custom_output_field(stub_sdk) -> None:
    from real_time_guardrails.core.custom_metrics import build_criteria_judge

    judge = MagicMock(name="judge")
    build_criteria_judge(
        name="custom",
        display_name="Custom",
        criteria_description="Does {input_text} make sense?",
        options=[],
        judge=judge,
        output_field="input_text",
    )
    assert stub_sdk.call_args.kwargs["output_field"] == "input_text"
