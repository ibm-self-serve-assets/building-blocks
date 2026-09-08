from __future__ import annotations

import sys
import types
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

from real_time_guardrails.core.config import GuardrailsConfig
from real_time_guardrails.core.exceptions import MissingFieldError


@pytest.fixture
def fake_sdk(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Stub every ibm_watsonx_gov module/class the evaluator imports."""

    def module(name: str) -> types.ModuleType:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        monkeypatch.setitem(sys.modules, name, mod)
        return mod

    pkg = module("ibm_watsonx_gov")
    entities = module("ibm_watsonx_gov.entities")
    fm_mod = module("ibm_watsonx_gov.entities.foundation_model")
    judge_mod = module("ibm_watsonx_gov.entities.llm_judge")
    criteria_mod = module("ibm_watsonx_gov.entities.criteria")
    metrics_mod = module("ibm_watsonx_gov.metrics")
    evaluators_mod = module("ibm_watsonx_gov.evaluators")

    fm_mod.WxAIFoundationModel = MagicMock(name="WxAIFoundationModel")
    judge_mod.LLMJudge = MagicMock(name="LLMJudge")
    criteria_mod.Option = MagicMock(name="Option")

    metric_names = (
        "AnswerRelevanceMetric ContextRelevanceMetric EvasivenessMetric FaithfulnessMetric "
        "HAPMetric HarmEngagementMetric HarmMetric HitRateMetric JailbreakMetric "
        "KeywordDetectionMetric PIIMetric ProfanityMetric PromptSafetyRiskMetric "
        "ReciprocalRankMetric RegexDetectionMetric RetrievalPrecisionMetric SexualContentMetric "
        "SocialBiasMetric TextGradeLevelMetric TextReadingEaseMetric ToolCallAccuracyMetric "
        "ToolCallRelevanceMetric TopicRelevanceMetric UnethicalBehaviorMetric "
        "UnsuccessfulRequestsMetric ViolenceMetric LLMAsJudgeMetric"
    ).split()
    for cls in metric_names:
        setattr(metrics_mod, cls, MagicMock(name=cls))

    pkg.entities = entities
    pkg.metrics = metrics_mod
    entities.foundation_model = fm_mod
    entities.llm_judge = judge_mod
    entities.criteria = criteria_mod

    # The MetricsEvaluator that the GuardrailsEvaluator constructs:
    evaluator_mock = MagicMock(name="MetricsEvaluator")
    sdk_evaluator_instance = MagicMock(name="MetricsEvaluatorInstance")
    evaluator_mock.return_value = sdk_evaluator_instance
    evaluators_mod.MetricsEvaluator = evaluator_mock

    return {
        "MetricsEvaluator": evaluator_mock,
        "instance": sdk_evaluator_instance,
        "metrics_module": metrics_mod,
    }


@pytest.fixture
def make_evaluator(fake_sdk: dict[str, Any], filled_env: dict[str, str]):
    """Factory: build a GuardrailsEvaluator whose SDK .evaluate() returns a known DataFrame."""
    from real_time_guardrails.core.evaluator import GuardrailsEvaluator

    def _make(
        scores: dict[str, float] | None = None,
        **eval_kwargs: Any,
    ) -> tuple[GuardrailsEvaluator, dict[str, Any]]:
        scores = scores or {}
        result_df = pd.DataFrame([scores]) if scores else pd.DataFrame()
        result_obj = MagicMock()
        result_obj.to_df.return_value = result_df
        fake_sdk["instance"].evaluate = MagicMock(return_value=result_obj)
        ev = GuardrailsEvaluator(**eval_kwargs)
        return ev, fake_sdk

    return _make


# -------- basic shape --------


def test_evaluator_builds_28_metric_registry(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={})
    assert len(ev.registry) == 28


def test_list_metrics_payload_shape(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={})
    payload = ev.list_metrics()
    assert payload["total"] == 28
    sample = next(m for m in payload["metrics"] if m["name"] == "PII Detection")
    assert sample["category"] == "safety"
    assert sample["default_threshold"] == 0.65
    assert sample["effective_threshold"] == 0.65
    assert sample["direction"] == "HIGH_IS_RISK"
    assert sample["actionable"] is True
    assert sample["accepts_fields"] == ["generated_text", "input_text"]


# -------- selection: explicit / category / auto --------


def test_explicit_metric_selection(make_evaluator) -> None:
    ev, sdk = make_evaluator(scores={"pii": 0.9})
    bundle = ev.evaluate(input_text="My SSN is 123-45-6789", metrics=["PII Detection"])
    assert list(bundle.results) == ["PII Detection"]
    assert bundle["PII Detection"].score == 0.9
    assert bundle["PII Detection"].action == "Block"


def test_category_selection_runs_only_that_group(make_evaluator) -> None:
    ev, sdk = make_evaluator(
        scores={
            "hap": 0.1,
            "pii": 0.1,
            "harm.granite_guardian": 0.1,
            "social_bias.granite_guardian": 0.1,
            "jailbreak.granite_guardian": 0.1,
            "violence.granite_guardian": 0.1,
            "profanity.granite_guardian": 0.1,
            "unethical_behavior.granite_guardian": 0.1,
            "sexual_content.granite_guardian": 0.1,
            "evasiveness.granite_guardian": 0.1,
        }
    )
    bundle = ev.evaluate(input_text="benign query", categories=["safety"])
    # 10 generic safety metrics fit; HarmEngagement requires input_text only too,
    # PromptSafetyRisk needs system_prompt and is filtered out by validate_required.
    selected = set(bundle.results.keys())
    assert "Prompt Safety Risk" not in selected
    # All 11 input-eligible safety metrics should run: 10 generic + HarmEngagement
    assert "Harm Engagement" in selected


def test_auto_select_picks_metrics_whose_fields_are_present(make_evaluator) -> None:
    ev, _ = make_evaluator(
        scores={
            "hap": 0.1,
            "pii": 0.1,
            "harm.granite_guardian": 0.1,
            "social_bias.granite_guardian": 0.1,
            "jailbreak.granite_guardian": 0.1,
            "violence.granite_guardian": 0.1,
            "profanity.granite_guardian": 0.1,
            "unethical_behavior.granite_guardian": 0.1,
            "sexual_content.granite_guardian": 0.1,
            "evasiveness.granite_guardian": 0.1,
            "harm_engagement.granite_guardian": 0.1,
        }
    )
    bundle = ev.evaluate(input_text="something")
    # Should select 11 input-only safety metrics (10 generic + harm_engagement)
    # and skip everything that needs context / system_prompt / params / tool_calls / generated_text.
    selected = set(bundle.results.keys())
    assert "Faithfulness" not in selected
    assert "Prompt Safety Risk" not in selected
    assert "Topic Relevance" not in selected
    assert "Keyword Detection" not in selected
    assert "Tool Call Accuracy" not in selected
    assert "HAP (Hate, Abuse, Profanity)" in selected
    assert "Harm Engagement" in selected


# -------- input validation --------


def test_rag_metric_without_context_raises_missing_field(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={})
    with pytest.raises(MissingFieldError) as exc:
        ev.evaluate(
            input_text="What is RAG?",
            generated_text="Retrieval Augmented Generation",
            metrics=["Faithfulness"],
        )
    assert exc.value.metric_name == "Faithfulness"
    assert exc.value.missing_field == "context"


def test_safety_metric_either_input_or_output(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={"pii": 0.1})
    # Only generated_text supplied — safety metrics accept it via accepts_fields
    bundle = ev.evaluate(generated_text="text", metrics=["PII Detection"])
    assert "PII Detection" in bundle.results


def test_safety_metric_neither_input_nor_output_raises(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={})
    with pytest.raises(MissingFieldError) as exc:
        ev.evaluate(metrics=["PII Detection"])  # no input, no output
    assert exc.value.metric_name == "PII Detection"


# -------- DataFrame shape passed to SDK --------


def test_dataframe_passes_symmetric_list_wrapping(make_evaluator) -> None:
    ev, sdk = make_evaluator(scores={"faithfulness.granite_guardian": 0.5})
    ev.evaluate(
        input_text="q",
        generated_text="a",
        context="c",
        metrics=["Faithfulness"],
    )
    called = sdk["instance"].evaluate.call_args
    df = called.kwargs["data"]
    # Every column must have exactly one row (single-record evaluation)
    assert len(df) == 1
    # input_text and generated_text: single strings in cell
    assert df["input_text"].iloc[0] == "q"
    assert df["generated_text"].iloc[0] == "a"
    # context: normalized into list[str], so the cell holds ["c"]
    assert df["context"].iloc[0] == ["c"]


def test_params_not_included_in_dataframe(make_evaluator) -> None:
    ev, sdk = make_evaluator(scores={"keyword_detection": 1.0})
    ev.evaluate(
        input_text="contains Project Phoenix",
        params={"keywords": ["Project Phoenix"]},
        metrics=["Keyword Detection"],
    )
    df = sdk["instance"].evaluate.call_args.kwargs["data"]
    assert "params" not in df.columns


def test_pattern_metric_reinstantiated_with_params(make_evaluator) -> None:
    ev, sdk = make_evaluator(scores={"keyword_detection": 1.0})
    ev.evaluate(
        input_text="contains Project Phoenix",
        params={"keywords": ["Project Phoenix"]},
        metrics=["Keyword Detection"],
    )
    keyword_cls = sdk["metrics_module"].KeywordDetectionMetric
    # Called twice total: once when registry built, once per evaluation with params
    assert keyword_cls.call_count >= 2
    last_call = keyword_cls.call_args
    assert last_call.kwargs["keywords"] == ["Project Phoenix"]
    assert last_call.kwargs["case_sensitive"] is False


# -------- threshold precedence end-to-end --------


def test_default_threshold_applied(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={"pii": 0.8})
    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    assert bundle["PII Detection"].threshold == 0.65
    assert bundle["PII Detection"].action == "Block"


def test_constructor_threshold_override_lowers_to_block(make_evaluator) -> None:
    ev, _ = make_evaluator(
        scores={"pii": 0.4},
        threshold_overrides={"PII Detection": 0.3},
    )
    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    assert bundle["PII Detection"].threshold == 0.3
    assert bundle["PII Detection"].action == "Block"


def test_per_call_threshold_beats_constructor(make_evaluator) -> None:
    # Score=0.5, per-call block=0.9 (more permissive than constructor's 0.3).
    # Block check: 0.5 < 0.9 → not blocked ✓.
    # Flag check: with the safety category default flag_value=0.4, score 0.5 ≥ 0.4
    # → Flag. Per-call override beat the constructor on block; flag wasn't
    # overridden so the default still fires. Result: action="Flag" (not Block).
    ev, _ = make_evaluator(
        scores={"pii": 0.5},
        threshold_overrides={"PII Detection": 0.3},
    )
    bundle = ev.evaluate(
        input_text="...",
        metrics=["PII Detection"],
        thresholds={"PII Detection": 0.9},
    )
    assert bundle["PII Detection"].threshold == 0.9
    assert bundle["PII Detection"].action == "Flag"


def test_per_call_threshold_with_flag_override_can_force_pass(make_evaluator) -> None:
    # Same scenario as above, but the partner also drops the flag threshold to None
    # to express "no flagging, only block." Result: action="Pass" (no flag fires).
    ev, _ = make_evaluator(
        scores={"pii": 0.5},
        threshold_overrides={"PII Detection": 0.3},
    )
    bundle = ev.evaluate(
        input_text="...",
        metrics=["PII Detection"],
        thresholds={"PII Detection": 0.9},
        flag_thresholds={"PII Detection": 0.8},  # flag also higher than score
    )
    assert bundle["PII Detection"].threshold == 0.9
    assert bundle["PII Detection"].flag_threshold == 0.8
    assert bundle["PII Detection"].action == "Pass"


def test_env_var_threshold_overrides_default(
    fake_sdk: dict[str, Any], filled_env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GUARDRAILS_THRESHOLD_PII_DETECTION", "0.3")
    from real_time_guardrails.core.evaluator import GuardrailsEvaluator

    result_df = pd.DataFrame([{"pii": 0.4}])
    result_obj = MagicMock()
    result_obj.to_df.return_value = result_df
    fake_sdk["instance"].evaluate = MagicMock(return_value=result_obj)
    ev = GuardrailsEvaluator()
    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    assert bundle["PII Detection"].threshold == 0.3


# -------- Unsuccessful Requests special-case --------


def test_unsuccessful_requests_never_blocks(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={"unsuccessful_requests": 0.05})
    bundle = ev.evaluate(generated_text="...", metrics=["Unsuccessful Requests"])
    assert bundle["Unsuccessful Requests"].action == "---"


# -------- missing column handling --------


def test_missing_column_in_sdk_output_returns_none_score(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={"unrelated_column": 0.5})
    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    assert bundle["PII Detection"].score is None
    assert bundle["PII Detection"].column is None


# -------- Fallback messages on Block --------


def test_fallback_message_uses_category_default_on_block(make_evaluator) -> None:
    """A safety Block emits the safety category default fallback."""
    from real_time_guardrails.core.metrics import CATEGORY_FALLBACK_MESSAGES

    ev, _ = make_evaluator(scores={"pii": 0.9})
    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    r = bundle["PII Detection"]
    assert r.action == "Block"
    assert r.fallback_message == CATEGORY_FALLBACK_MESSAGES["safety"]


def test_fallback_message_per_call_override_beats_category_default(make_evaluator) -> None:
    ev, _ = make_evaluator(scores={"pii": 0.9})
    bundle = ev.evaluate(
        input_text="...",
        metrics=["PII Detection"],
        fallback_messages={"PII Detection": "Custom partner message."},
    )
    assert bundle["PII Detection"].fallback_message == "Custom partner message."


def test_fallback_message_none_when_not_blocked(make_evaluator) -> None:
    """Pass and Flag actions never carry a fallback_message — only Block does."""
    ev, _ = make_evaluator(scores={"pii": 0.0})
    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    assert bundle["PII Detection"].action == "Pass"
    assert bundle["PII Detection"].fallback_message is None


def test_fallback_message_none_for_flag_state(make_evaluator) -> None:
    """Flag is not a refusal — no fallback message needed."""
    ev, _ = make_evaluator(scores={"pii": 0.5})  # between flag=0.4 and block=0.65
    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    assert bundle["PII Detection"].action == "Flag"
    assert bundle["PII Detection"].fallback_message is None


# -------- Optional WXG_PROJECT_ID: LLM-judge metrics gated cleanly --------


@pytest.fixture
def env_no_project_id(monkeypatch: pytest.MonkeyPatch, clean_env: None) -> dict[str, str]:
    env = {"WATSONX_APIKEY": "k", "WXG_SERVICE_INSTANCE_ID": "i"}
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return env


def test_evaluator_builds_without_project_id(
    fake_sdk: dict[str, Any], env_no_project_id: dict[str, str]
) -> None:
    from real_time_guardrails.core.evaluator import GuardrailsEvaluator

    ev = GuardrailsEvaluator()
    assert len(ev.registry) == 25
    payload = ev.list_metrics()
    assert payload["total"] == 25


def test_evaluator_without_project_id_logs_warning(
    fake_sdk: dict[str, Any],
    env_no_project_id: dict[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    import logging

    from real_time_guardrails.core.evaluator import GuardrailsEvaluator

    caplog.set_level(logging.WARNING)
    GuardrailsEvaluator()
    assert any(
        "WXG_PROJECT_ID" in rec.message and "disabled" in rec.message
        for rec in caplog.records
    )


def test_evaluator_with_project_id_does_not_warn(
    fake_sdk: dict[str, Any],
    filled_env: dict[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    import logging

    from real_time_guardrails.core.evaluator import GuardrailsEvaluator

    caplog.set_level(logging.WARNING)
    GuardrailsEvaluator()
    assert not any("WXG_PROJECT_ID" in rec.message for rec in caplog.records)


def test_unavailable_llm_judge_metric_raises_unknown(
    fake_sdk: dict[str, Any], env_no_project_id: dict[str, str]
) -> None:
    from real_time_guardrails.core.evaluator import GuardrailsEvaluator
    from real_time_guardrails.core.exceptions import UnknownMetricError

    ev = GuardrailsEvaluator()
    with pytest.raises(UnknownMetricError) as exc:
        ev.evaluate(
            input_text="q",
            generated_text="a",
            metrics=["Conciseness (LLM Judge)"],
        )
    assert "Conciseness (LLM Judge)" in str(exc.value)


def test_no_project_id_safety_metrics_still_work(
    fake_sdk: dict[str, Any], env_no_project_id: dict[str, str]
) -> None:
    """Confirm the 25 non-LLM-judge metrics evaluate normally without watsonx.ai."""
    import pandas as pd
    from unittest.mock import MagicMock

    from real_time_guardrails.core.evaluator import GuardrailsEvaluator

    result_df = pd.DataFrame([{"pii": 0.8}])
    result_obj = MagicMock()
    result_obj.to_df.return_value = result_df
    fake_sdk["instance"].evaluate = MagicMock(return_value=result_obj)
    ev = GuardrailsEvaluator()
    bundle = ev.evaluate(input_text="My SSN is 123-45-6789", metrics=["PII Detection"])
    assert bundle["PII Detection"].score == 0.8
    assert bundle["PII Detection"].action == "Block"
