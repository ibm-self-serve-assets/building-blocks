from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from real_time_guardrails.core.config import GuardrailsConfig
from real_time_guardrails.core.exceptions import (
    MissingFieldError,
    UnknownCategoryError,
    UnknownMetricError,
)
from real_time_guardrails.core.registry import MetricEntry, MetricRegistry, known_categories
from real_time_guardrails.core.results import Category
from real_time_guardrails.core.thresholds import Direction, ThresholdSpec


# -------- registry shape: build the real 28-metric registry with the SDK fully mocked --------


@pytest.fixture
def fake_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub every ibm_watsonx_gov import build_registry() reaches for."""
    import sys
    import types

    def _module(name: str) -> types.ModuleType:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

    pkg = _module("ibm_watsonx_gov")
    entities = _module("ibm_watsonx_gov.entities")
    fm_mod = _module("ibm_watsonx_gov.entities.foundation_model")
    judge_mod = _module("ibm_watsonx_gov.entities.llm_judge")
    criteria_mod = _module("ibm_watsonx_gov.entities.criteria")
    metrics_mod = _module("ibm_watsonx_gov.metrics")

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


@pytest.fixture
def registry(fake_sdk: None) -> MetricRegistry:
    from real_time_guardrails.core.metrics import build_registry

    cfg = GuardrailsConfig(
        api_key="x", service_instance_id="y", project_id="z"
    )
    return build_registry(cfg)


@pytest.fixture
def registry_no_judge(fake_sdk: None) -> MetricRegistry:
    """Registry built without project_id — LLM-judge metrics omitted."""
    from real_time_guardrails.core.metrics import build_registry

    cfg = GuardrailsConfig(api_key="x", service_instance_id="y", project_id=None)
    return build_registry(cfg)


EXPECTED_COUNT = 28
EXPECTED_COUNT_NO_JUDGE = 25


def test_registry_has_exactly_28_metrics(registry: MetricRegistry) -> None:
    assert len(registry) == EXPECTED_COUNT


def test_registry_category_breakdown(registry: MetricRegistry) -> None:
    by_category: dict[str, int] = {}
    for entry in registry:
        by_category[entry.category] = by_category.get(entry.category, 0) + 1
    assert by_category == {
        "safety": 12,
        "rag_generation": 3,
        "rag_retrieval": 3,
        "quality": 5,
        "topic": 1,
        "pattern": 2,
        "tool_call": 2,
    }


# -------- LLM-judge gating: project_id absent → 3 metrics dropped --------

LLM_JUDGE_METRIC_NAMES = (
    "Answer Completeness (LLM Judge)",
    "Conciseness (LLM Judge)",
    "Tool Call Relevance",
)


def test_registry_without_project_id_has_25_metrics(
    registry_no_judge: MetricRegistry,
) -> None:
    assert len(registry_no_judge) == EXPECTED_COUNT_NO_JUDGE


def test_registry_without_project_id_omits_llm_judge_metrics(
    registry_no_judge: MetricRegistry,
) -> None:
    for name in LLM_JUDGE_METRIC_NAMES:
        assert name not in registry_no_judge


def test_registry_without_project_id_category_breakdown(
    registry_no_judge: MetricRegistry,
) -> None:
    by_category: dict[str, int] = {}
    for entry in registry_no_judge:
        by_category[entry.category] = by_category.get(entry.category, 0) + 1
    assert by_category == {
        "safety": 12,
        "rag_generation": 3,
        "rag_retrieval": 3,
        "quality": 3,        # was 5; loses Answer Completeness + Conciseness
        "topic": 1,
        "pattern": 2,
        "tool_call": 1,       # was 2; loses Tool Call Relevance
    }


def test_registry_without_project_id_keeps_deterministic_quality_metrics(
    registry_no_judge: MetricRegistry,
) -> None:
    # Pure-Python quality metrics don't need a judge — should still be present.
    for name in ("Text Grade Level", "Text Reading Ease", "Unsuccessful Requests"):
        assert name in registry_no_judge


def test_known_categories_constant_matches_registry(registry: MetricRegistry) -> None:
    assert set(known_categories()) == registry.categories


def test_excluded_metrics_not_registered(registry: MetricRegistry) -> None:
    from real_time_guardrails.core.metrics import EXCLUDED_METRIC_NAMES

    for name in EXCLUDED_METRIC_NAMES:
        assert name not in registry, f"{name} should not be in the registry"


def test_rag_generation_metrics_require_context(registry: MetricRegistry) -> None:
    for name in ("Answer Relevance", "Faithfulness", "Context Relevance"):
        assert "context" in registry.get(name).required_fields
        assert "generated_text" in registry.get(name).required_fields


def test_rag_retrieval_metrics_require_context_not_generated(registry: MetricRegistry) -> None:
    for name in ("Retrieval Precision", "Hit Rate", "Reciprocal Rank"):
        entry = registry.get(name)
        assert "context" in entry.required_fields
        assert "generated_text" not in entry.required_fields


def test_prompt_safety_risk_requires_system_prompt(registry: MetricRegistry) -> None:
    assert "system_prompt" in registry.get("Prompt Safety Risk").required_fields


def test_topic_relevance_requires_system_prompt(registry: MetricRegistry) -> None:
    assert "system_prompt" in registry.get("Topic Relevance").required_fields


def test_pattern_metrics_require_params(registry: MetricRegistry) -> None:
    for name in ("Keyword Detection", "Regex Detection"):
        assert "params" in registry.get(name).required_fields


def test_tool_call_metrics_require_tool_calls(registry: MetricRegistry) -> None:
    assert "tool_calls" in registry.get("Tool Call Accuracy").required_fields
    relevance = registry.get("Tool Call Relevance")
    assert "tool_calls" in relevance.required_fields
    assert "available_tools" in relevance.required_fields


def test_safety_metrics_accept_either_input_or_output(registry: MetricRegistry) -> None:
    # Generic safety metrics — accept either field, require neither absolutely
    hap = registry.get("HAP (Hate, Abuse, Profanity)")
    assert hap.required_fields == frozenset()
    assert hap.accepts_fields == frozenset({"input_text", "generated_text"})


def test_harm_engagement_is_input_only(registry: MetricRegistry) -> None:
    entry = registry.get("Harm Engagement")
    assert entry.required_fields == frozenset({"input_text"})
    assert entry.accepts_fields == frozenset()


def test_unsuccessful_requests_is_non_actionable(registry: MetricRegistry) -> None:
    entry = registry.get("Unsuccessful Requests")
    assert entry.threshold_spec.actionable is False


def test_unknown_metric_raises(registry: MetricRegistry) -> None:
    with pytest.raises(UnknownMetricError):
        registry.get("Not A Real Metric")


# -------- Registry: validation + filtering + auto-select --------


def _entry(
    name: str,
    *,
    category: Category = "safety",
    required: frozenset[str] = frozenset(),
    accepts: frozenset[str] = frozenset(),
) -> MetricEntry:
    return MetricEntry(
        name=name,
        metric=object(),
        category=category,
        column_name=name.lower().replace(" ", "_"),
        threshold_spec=ThresholdSpec(0.5, Direction.HIGH_IS_RISK),
        required_fields=required,
        accepts_fields=accepts,
        description="",
    )


def test_validate_required_passes_when_all_present() -> None:
    r = MetricRegistry([_entry("M", required=frozenset({"input_text"}))])
    r.validate_required(list(r), {"input_text"})  # no raise


def test_validate_required_raises_when_missing() -> None:
    r = MetricRegistry([_entry("M", required=frozenset({"context"}))])
    with pytest.raises(MissingFieldError) as exc:
        r.validate_required(list(r), {"input_text"})
    assert exc.value.metric_name == "M"
    assert exc.value.missing_field == "context"


def test_validate_required_either_semantics() -> None:
    r = MetricRegistry([_entry("M", accepts=frozenset({"input_text", "generated_text"}))])
    r.validate_required(list(r), {"input_text"})  # one is enough
    r.validate_required(list(r), {"generated_text"})
    with pytest.raises(MissingFieldError) as exc:
        r.validate_required(list(r), {"context"})
    assert "at least one of" in exc.value.missing_field


def test_filter_by_category_returns_only_matching() -> None:
    r = MetricRegistry(
        [
            _entry("Safety1", category="safety"),
            _entry("Quality1", category="quality"),
            _entry("Quality2", category="quality"),
        ]
    )
    out = r.filter_by_category(["quality"])
    assert [e.name for e in out] == ["Quality1", "Quality2"]


def test_filter_by_unknown_category_raises() -> None:
    r = MetricRegistry([_entry("M", category="safety")])
    with pytest.raises(UnknownCategoryError):
        r.filter_by_category(["bogus"])


def test_auto_select_picks_metrics_whose_requirements_are_met() -> None:
    r = MetricRegistry(
        [
            _entry("InOnly", required=frozenset({"input_text"})),
            _entry("OutOnly", required=frozenset({"generated_text"})),
            _entry("Either", accepts=frozenset({"input_text", "generated_text"})),
            _entry("RAG", required=frozenset({"input_text", "context"})),
        ]
    )
    selected = {e.name for e in r.auto_select({"input_text"})}
    assert selected == {"InOnly", "Either"}
    selected = {e.name for e in r.auto_select({"input_text", "context"})}
    assert selected == {"InOnly", "Either", "RAG"}
