from __future__ import annotations

from typing import Iterable


class GuardrailsError(Exception):
    """Base class for all real-time-guardrails errors."""


class ConfigError(GuardrailsError):
    """Required configuration (e.g. an env var) is missing or invalid."""


class EvaluatorInitError(GuardrailsError):
    """The underlying IBM watsonx.governance MetricsEvaluator could not be initialized."""


class UnknownMetricError(GuardrailsError):
    def __init__(self, metric_name: str, available: Iterable[str]) -> None:
        self.metric_name = metric_name
        self.available = sorted(available)
        super().__init__(
            f"Unknown metric {metric_name!r}. Available metrics: {self.available}"
        )


class UnknownCategoryError(GuardrailsError):
    def __init__(self, category: str, available: Iterable[str]) -> None:
        self.category = category
        self.available = sorted(available)
        super().__init__(
            f"Unknown category {category!r}. Available categories: {self.available}"
        )


class MissingFieldError(GuardrailsError):
    def __init__(self, metric_name: str, missing_field: str) -> None:
        self.metric_name = metric_name
        self.missing_field = missing_field
        super().__init__(
            f"Metric {metric_name!r} requires field {missing_field!r}, but it was not supplied."
        )


class InputShapeError(GuardrailsError):
    def __init__(self, field: str, received: object, expected: str) -> None:
        self.field = field
        self.received_type = type(received).__name__
        self.expected = expected
        super().__init__(
            f"Field {field!r} has unsupported shape: received {self.received_type!r}, expected {expected}."
        )


class MetricExecutionError(GuardrailsError):
    def __init__(self, metric_name: str, original: Exception) -> None:
        self.metric_name = metric_name
        self.original = original
        super().__init__(f"Metric {metric_name!r} failed during evaluation: {original!s}")
