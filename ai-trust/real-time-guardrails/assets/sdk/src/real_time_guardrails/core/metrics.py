"""Construction of the 28-metric registry.

All ``ibm_watsonx_gov`` SDK imports happen inside :func:`build_registry` so the
package can be imported (and most tests run) without the SDK installed. The
import will fail at registry-build time with a clear error if the SDK is
missing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .config import GuardrailsConfig
from .registry import MetricEntry, MetricRegistry
from .thresholds import CATEGORY_DEFAULTS, Direction, ThresholdSpec

if TYPE_CHECKING:
    from .results import Category


# ---------- field-requirement shortcuts ----------

_EITHER_INPUT_OR_OUTPUT = frozenset({"input_text", "generated_text"})
_INPUT_ONLY = frozenset({"input_text"})
_OUTPUT_ONLY = frozenset({"generated_text"})
_INPUT_AND_OUTPUT = frozenset({"input_text", "generated_text"})
_RAG_GEN = frozenset({"input_text", "generated_text", "context"})
_RAG_RETRIEVAL = frozenset({"input_text", "context"})
_INPUT_AND_SYSTEM_PROMPT = frozenset({"input_text", "system_prompt"})
_INPUT_AND_PARAMS = frozenset({"input_text", "params"})
_INPUT_AND_TOOL_CALLS = frozenset({"input_text", "tool_calls"})
_INPUT_TOOL_CALLS_AVAILABLE = frozenset({"input_text", "tool_calls", "available_tools"})


_SAFETY_DEFAULT = CATEGORY_DEFAULTS["safety"]
_RAG_GEN_DEFAULT = CATEGORY_DEFAULTS["rag_generation"]
_RAG_RETR_DEFAULT = CATEGORY_DEFAULTS["rag_retrieval"]
_QUALITY_DEFAULT = CATEGORY_DEFAULTS["quality"]
_TOPIC_DEFAULT = CATEGORY_DEFAULTS["topic"]
_PATTERN_DEFAULT = CATEGORY_DEFAULTS["pattern"]
_TOOL_CALL_DEFAULT = CATEGORY_DEFAULTS["tool_call"]


def build_registry(config: GuardrailsConfig) -> MetricRegistry:
    """Instantiate every metric and return a populated :class:`MetricRegistry`.

    Imports the IBM SDK lazily so the package is import-clean without it. Any
    SDK import error is raised verbatim — install ``ibm-watsonx-gov==1.3.1``.
    """
    from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel  # type: ignore
    from ibm_watsonx_gov.entities.llm_judge import LLMJudge  # type: ignore
    from ibm_watsonx_gov.metrics import (  # type: ignore
        AnswerRelevanceMetric,
        ContextRelevanceMetric,
        EvasivenessMetric,
        FaithfulnessMetric,
        HAPMetric,
        HarmEngagementMetric,
        HarmMetric,
        HitRateMetric,
        JailbreakMetric,
        KeywordDetectionMetric,
        PIIMetric,
        ProfanityMetric,
        PromptSafetyRiskMetric,
        ReciprocalRankMetric,
        RegexDetectionMetric,
        RetrievalPrecisionMetric,
        SexualContentMetric,
        SocialBiasMetric,
        TextGradeLevelMetric,
        TextReadingEaseMetric,
        ToolCallAccuracyMetric,
        ToolCallRelevanceMetric,
        TopicRelevanceMetric,
        UnethicalBehaviorMetric,
        UnsuccessfulRequestsMetric,
        ViolenceMetric,
    )

    from .custom_metrics import build_answer_completeness, build_conciseness

    # LLM judge is built only when project_id is supplied. Without it, the 3
    # LLM-as-judge metrics are omitted from the registry and the remaining 25
    # metrics work normally.
    judge: object | None = None
    if config.project_id:
        judge_model = WxAIFoundationModel(
            model_id=config.judge_model_id,
            project_id=config.project_id,
        )
        judge = LLMJudge(model=judge_model)

    entries: list[MetricEntry] = []

    # ===== Safety (12) =====
    entries.extend(
        [
            MetricEntry(
                name="HAP (Hate, Abuse, Profanity)",
                metric=HAPMetric(),
                category="safety",
                column_name="hap",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Hate, Abuse, and Profanity detection.",
            ),
            MetricEntry(
                name="PII Detection",
                metric=PIIMetric(value=0.5),
                category="safety",
                column_name="pii",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Personally identifiable information detection.",
            ),
            MetricEntry(
                name="Harm",
                metric=HarmMetric(),
                category="safety",
                column_name="harm.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="General harm detection (Granite Guardian).",
            ),
            MetricEntry(
                name="Social Bias",
                metric=SocialBiasMetric(),
                category="safety",
                column_name="social_bias.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Social bias detection.",
            ),
            MetricEntry(
                name="Jailbreak Detection",
                metric=JailbreakMetric(),
                category="safety",
                column_name="jailbreak.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Detects prompt-injection / jailbreak attempts.",
            ),
            MetricEntry(
                name="Violence",
                metric=ViolenceMetric(),
                category="safety",
                column_name="violence.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Violence detection.",
            ),
            MetricEntry(
                name="Profanity",
                metric=ProfanityMetric(),
                category="safety",
                column_name="profanity.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Profanity detection.",
            ),
            MetricEntry(
                name="Unethical Behavior",
                metric=UnethicalBehaviorMetric(),
                category="safety",
                column_name="unethical_behavior.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Unethical behavior detection.",
            ),
            MetricEntry(
                name="Sexual Content",
                metric=SexualContentMetric(),
                category="safety",
                column_name="sexual_content.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Sexual content detection.",
            ),
            MetricEntry(
                name="Evasiveness",
                metric=EvasivenessMetric(),
                category="safety",
                column_name="evasiveness.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=frozenset(),
                accepts_fields=_EITHER_INPUT_OR_OUTPUT,
                description="Evasive-response detection.",
            ),
            MetricEntry(
                name="Harm Engagement",
                metric=HarmEngagementMetric(),
                category="safety",
                column_name="harm_engagement.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=_INPUT_ONLY,
                description="Measures engagement risk with harmful prompts.",
            ),
            MetricEntry(
                # system_prompt is re-bound at evaluate time (see
                # GuardrailsEvaluator._reconfigure_runtime_metric); placeholder
                # here just satisfies the pydantic constructor.
                name="Prompt Safety Risk",
                metric=PromptSafetyRiskMetric(
                    method="granite_guardian", system_prompt=" "
                ),
                category="safety",
                column_name="prompt_safety_risk.granite_guardian",
                threshold_spec=_SAFETY_DEFAULT,
                required_fields=_INPUT_AND_SYSTEM_PROMPT,
                description="Real-time prompt-safety risk evaluation given a system prompt.",
            ),
        ]
    )

    # ===== RAG generation (3) =====
    entries.extend(
        [
            MetricEntry(
                name="Answer Relevance",
                metric=AnswerRelevanceMetric(method="granite_guardian"),
                category="rag_generation",
                column_name="answer_relevance.granite_guardian",
                threshold_spec=_RAG_GEN_DEFAULT,
                required_fields=_RAG_GEN,
                description="How relevant the generated answer is to the input question.",
            ),
            MetricEntry(
                name="Context Relevance",
                metric=ContextRelevanceMetric(method="granite_guardian"),
                category="rag_generation",
                column_name="context_relevance.granite_guardian",
                threshold_spec=_RAG_GEN_DEFAULT,
                required_fields=_RAG_GEN,
                description="How relevant the retrieved context is to the input question.",
            ),
            MetricEntry(
                name="Faithfulness",
                metric=FaithfulnessMetric(method="granite_guardian"),
                category="rag_generation",
                column_name="faithfulness.granite_guardian",
                threshold_spec=_RAG_GEN_DEFAULT,
                required_fields=_RAG_GEN,
                description="Whether the generated answer is grounded in the retrieved context.",
            ),
        ]
    )

    # ===== RAG retrieval (3) =====
    entries.extend(
        [
            MetricEntry(
                name="Retrieval Precision",
                metric=RetrievalPrecisionMetric(),
                category="rag_retrieval",
                column_name="retrieval_precision",
                threshold_spec=_RAG_RETR_DEFAULT,
                required_fields=_RAG_RETRIEVAL,
                description="Fraction of retrieved contexts above the relevance threshold.",
            ),
            MetricEntry(
                name="Hit Rate",
                metric=HitRateMetric(),
                category="rag_retrieval",
                column_name="hit_rate",
                threshold_spec=_RAG_RETR_DEFAULT,
                required_fields=_RAG_RETRIEVAL,
                description="Binary: was at least one relevant context retrieved?",
            ),
            MetricEntry(
                name="Reciprocal Rank",
                metric=ReciprocalRankMetric(),
                category="rag_retrieval",
                column_name="reciprocal_rank",
                threshold_spec=_RAG_RETR_DEFAULT,
                required_fields=_RAG_RETRIEVAL,
                description="1/position of the first relevant retrieved context.",
            ),
        ]
    )

    # ===== Quality (5 with judge, 3 without) =====
    if judge is not None:
        entries.extend(
            [
                MetricEntry(
                    name="Answer Completeness (LLM Judge)",
                    metric=build_answer_completeness(judge),
                    category="quality",
                    column_name="answer_completeness",
                    threshold_spec=_QUALITY_DEFAULT,
                    required_fields=_INPUT_AND_OUTPUT,
                    description="LLM-judge score of how completely the response addresses the input.",
                ),
                MetricEntry(
                    name="Conciseness (LLM Judge)",
                    metric=build_conciseness(judge),
                    category="quality",
                    column_name="conciseness",
                    threshold_spec=_QUALITY_DEFAULT,
                    required_fields=_OUTPUT_ONLY,
                    description="LLM-judge score of response conciseness.",
                ),
            ]
        )
    entries.extend(
        [
            MetricEntry(
                name="Text Grade Level",
                metric=TextGradeLevelMetric(),
                category="quality",
                column_name="text_grade_level.flesch_kincaid_grade",
                threshold_spec=_QUALITY_DEFAULT,
                required_fields=_OUTPUT_ONLY,
                description="Flesch-Kincaid grade-level readability score for the response.",
            ),
            MetricEntry(
                name="Text Reading Ease",
                metric=TextReadingEaseMetric(),
                category="quality",
                column_name="text_reading_ease.flesch_reading_ease",
                threshold_spec=_QUALITY_DEFAULT,
                required_fields=_OUTPUT_ONLY,
                description="Flesch reading-ease score for the response.",
            ),
            MetricEntry(
                name="Unsuccessful Requests",
                metric=UnsuccessfulRequestsMetric(),
                category="quality",
                column_name="unsuccessful_requests",
                threshold_spec=ThresholdSpec(
                    value=_QUALITY_DEFAULT.value,
                    direction=Direction.LOW_IS_RISK,
                    actionable=False,
                ),
                required_fields=_OUTPUT_ONLY,
                description="Detects failed-response patterns; reports only (never blocks).",
            ),
        ]
    )

    # ===== Topic alignment (1) =====
    entries.append(
        MetricEntry(
            # system_prompt is re-bound at evaluate time; placeholder here just
            # satisfies the pydantic constructor.
            name="Topic Relevance",
            metric=TopicRelevanceMetric(system_prompt=" "),
            category="topic",
            column_name="topic_relevance",
            threshold_spec=_TOPIC_DEFAULT,
            required_fields=_INPUT_AND_SYSTEM_PROMPT,
            description="Whether the input aligns with the topic implied by the system prompt.",
        )
    )

    # ===== Pattern (2) =====
    entries.extend(
        [
            MetricEntry(
                # Placeholder keywords list at registry build; the real list is
                # supplied via params at evaluate time (see
                # GuardrailsEvaluator._reconfigure_pattern_metric).
                name="Keyword Detection",
                metric=KeywordDetectionMetric(keywords=["__placeholder__"]),
                category="pattern",
                column_name="keyword",
                threshold_spec=_PATTERN_DEFAULT,
                required_fields=_INPUT_AND_PARAMS,
                description="Detects user-supplied keywords in the input.",
            ),
            MetricEntry(
                # Placeholder pattern at registry build; real patterns come
                # from params at evaluate time.
                name="Regex Detection",
                metric=RegexDetectionMetric(regex_patterns=["__placeholder__"]),
                category="pattern",
                column_name="regex",
                threshold_spec=_PATTERN_DEFAULT,
                required_fields=_INPUT_AND_PARAMS,
                description="Detects user-supplied regex patterns in the input.",
            ),
        ]
    )

    # ===== Tool-call (2 with judge, 1 without) =====
    entries.append(
        MetricEntry(
            name="Tool Call Accuracy",
            metric=ToolCallAccuracyMetric(),  # method defaults to "syntactic"
            category="tool_call",
            column_name="tool_call_accuracy.syntactic",
            threshold_spec=_TOOL_CALL_DEFAULT,
            required_fields=_INPUT_AND_TOOL_CALLS,
            description="Validates tool call syntax / semantics against tool definitions.",
        )
    )
    if judge is not None:
        # Tool Call Relevance uses LLM-as-judge under the hood, so it needs
        # the watsonx.ai-backed judge to be available.
        entries.append(
            MetricEntry(
                name="Tool Call Relevance",
                metric=ToolCallRelevanceMetric(),
                category="tool_call",
                column_name="tool_call_relevance.llm_as_judge",
                threshold_spec=_TOOL_CALL_DEFAULT,
                required_fields=_INPUT_TOOL_CALLS_AVAILABLE,
                description="Assesses whether the selected tool matches the user intent.",
            )
        )

    return MetricRegistry(entries)


# Default user-facing fallback messages emitted on Block, keyed by category.
# Partners override per-metric via `fallback_messages={metric_name: ...}` on
# `evaluate(...)`. Kept short and neutral so partners ship them as-is if they
# don't override.
CATEGORY_FALLBACK_MESSAGES: dict[str, str] = {
    "safety": "Your request couldn't be processed. Please rephrase your question.",
    "rag_generation": "I'm not confident in my answer based on the available information. Let me connect you with a specialist who can help.",
    "rag_retrieval": "I don't have enough relevant information to answer that. Could you rephrase or provide more context?",
    "quality": "I wasn't able to generate a reliable response. Please try rephrasing your question.",
    "topic": "That question is outside the scope of what I can help with here.",
    "pattern": "Your request contains restricted content. Please rephrase.",
    "tool_call": "I couldn't determine the right action to take for your request. Please rephrase or try a different approach.",
}


# Names that must NOT be in the registry (regression guard for tests).
EXCLUDED_METRIC_NAMES: frozenset[str] = frozenset(
    {
        "Narrative Quality",
        "Narrative Quality (LLM Judge)",
        "Action Oriented Validator",
        "Helpfulness",
        "Helpfulness (LLM Judge)",
        "Average Precision",
        "NDCG",
        "Tool Call Parameter Accuracy",
        "Tool Call Syntactic Accuracy",
        "LLM Validation",
        "Answer Similarity",
    }
)
