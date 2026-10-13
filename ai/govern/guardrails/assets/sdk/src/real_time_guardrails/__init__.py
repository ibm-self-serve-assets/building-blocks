"""real-time-guardrails: real-time AI guardrails over IBM watsonx.governance.

Three interfaces sharing one core:
    * Library — ``from real_time_guardrails import GuardrailsEvaluator``
    * REST API — ``real-time-guardrails serve``
    * MCP server — ``real-time-guardrails mcp``
"""

from real_time_guardrails._version import __version__
from real_time_guardrails.audit import AuditLogger
from real_time_guardrails.core.config import GuardrailsConfig
from real_time_guardrails.core.evaluator import GuardrailsEvaluator
from real_time_guardrails.core.exceptions import (
    ConfigError,
    EvaluatorInitError,
    GuardrailsError,
    InputShapeError,
    MetricExecutionError,
    MissingFieldError,
    UnknownCategoryError,
    UnknownMetricError,
)
from real_time_guardrails.core.registry import MetricEntry, MetricRegistry, known_categories
from real_time_guardrails.core.results import GuardrailResult, ResultBundle
from real_time_guardrails.core.thresholds import Direction, ThresholdSpec


__all__ = [
    "__version__",
    "AuditLogger",
    "ConfigError",
    "Direction",
    "EvaluatorInitError",
    "GuardrailResult",
    "GuardrailsConfig",
    "GuardrailsError",
    "GuardrailsEvaluator",
    "InputShapeError",
    "MetricEntry",
    "MetricExecutionError",
    "MetricRegistry",
    "MissingFieldError",
    "ResultBundle",
    "ThresholdSpec",
    "UnknownCategoryError",
    "UnknownMetricError",
    "known_categories",
]
