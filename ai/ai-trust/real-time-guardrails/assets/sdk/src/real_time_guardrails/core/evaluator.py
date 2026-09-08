"""The :class:`GuardrailsEvaluator` — public entry point for the library."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Mapping, Sequence

from .config import GuardrailsConfig
from .exceptions import EvaluatorInitError, MetricExecutionError
from .inputs import normalize_inputs
from .registry import MetricEntry, MetricRegistry
from .results import Category, GuardrailResult, ResultBundle
from .thresholds import ThresholdResolver, ThresholdSpec

if TYPE_CHECKING:
    import pandas as pd  # noqa: F401


logger = logging.getLogger(__name__)


class GuardrailsEvaluator:
    """High-level facade over IBM watsonx.governance ``MetricsEvaluator``.

    Construction loads credentials from environment variables (default) or from
    an explicit :class:`GuardrailsConfig`, then builds the registry of 28
    real-time guardrail metrics. All ``ibm_watsonx_gov`` SDK imports are
    deferred to construction time so importing this module is cheap.
    """

    def __init__(
        self,
        config: GuardrailsConfig | None = None,
        *,
        threshold_overrides: Mapping[str, float] | None = None,
        config_path: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._config = config or GuardrailsConfig.from_env(env=env)
        self._config.export_to_env()
        if not self._config.project_id:
            logger.warning(
                "WXG_PROJECT_ID not set — LLM-as-judge metrics disabled. "
                "Answer Completeness, Conciseness, and Tool Call Relevance "
                "will not be available. Set WXG_PROJECT_ID to enable them."
            )
        self._registry = self._build_registry(self._config)
        self._threshold_resolver = ThresholdResolver(
            constructor=threshold_overrides,
            config_path=config_path,
            env=env if env is not None else os.environ,
            known_metrics=set(self._registry.names),
        )
        self._sdk_evaluator = self._build_sdk_evaluator()

    # ----- constructors helpers (lazy imports) -----

    def _build_registry(self, config: GuardrailsConfig) -> MetricRegistry:
        try:
            from .metrics import build_registry

            return build_registry(config)
        except Exception as exc:  # ImportError or SDK construction failure
            raise EvaluatorInitError(f"Failed to build metric registry: {exc}") from exc

    def _build_sdk_evaluator(self) -> Any:
        try:
            from ibm_watsonx_gov.config import GenAIConfiguration  # type: ignore
            from ibm_watsonx_gov.evaluators import MetricsEvaluator  # type: ignore

            # Explicit default config so ``_run_sdk`` can restore it after
            # per-call field-routing swaps (see _run_sdk for details).
            self._default_config = GenAIConfiguration(
                input_fields=["input_text"],
                output_fields=["generated_text"],
                context_fields=["context"],
            )
            return MetricsEvaluator(configuration=self._default_config)
        except Exception as exc:
            raise EvaluatorInitError(
                f"Failed to initialize ibm_watsonx_gov MetricsEvaluator: {exc}"
            ) from exc

    # ----- public API -----

    @property
    def registry(self) -> MetricRegistry:
        return self._registry

    def list_metrics(self) -> dict[str, Any]:
        metrics: list[dict[str, Any]] = []
        for entry in self._registry:
            effective = self._threshold_resolver.effective_threshold(
                entry.name, entry.category, entry.threshold_spec
            )
            metrics.append(
                {
                    "name": entry.name,
                    "category": entry.category,
                    "column": entry.column_name,
                    "default_threshold": entry.threshold_spec.value,
                    "effective_threshold": effective,
                    "flag_threshold": entry.threshold_spec.flag_value,
                    "direction": entry.threshold_spec.direction.name,
                    "actionable": entry.threshold_spec.actionable,
                    "required_fields": sorted(entry.required_fields),
                    "accepts_fields": sorted(entry.accepts_fields),
                    "description": entry.description,
                }
            )
        return {"total": len(metrics), "metrics": metrics}

    def evaluate(
        self,
        *,
        input_text: str | list[str] | None = None,
        generated_text: str | list[str] | None = None,
        context: str | list[str] | None = None,
        system_prompt: str | None = None,
        tool_calls: list[dict] | None = None,
        available_tools: list[dict] | None = None,
        params: dict | None = None,
        metrics: Sequence[str] | None = None,
        categories: Sequence[str] | None = None,
        thresholds: Mapping[str, float] | None = None,
        flag_thresholds: Mapping[str, float] | None = None,
        fallback_messages: Mapping[str, str] | None = None,
        record_id: str = "eval_1",
    ) -> ResultBundle:
        """Evaluate a single record against the requested metrics.

        Selection precedence: ``metrics`` (explicit names) > ``categories``
        (group selection) > auto-select (every metric whose required fields are
        present in the supplied data).
        """
        raw_inputs = {
            "input_text": input_text,
            "generated_text": generated_text,
            "context": context,
            "system_prompt": system_prompt,
            "tool_calls": tool_calls,
            "available_tools": available_tools,
            "params": params,
        }
        normalized = normalize_inputs(raw_inputs)
        available_fields = set(normalized.keys())
        entries = self._select_entries(metrics, categories, available_fields)
        self._registry.validate_required(entries, available_fields)
        df = self._build_dataframe(normalized)
        sdk_metrics = self._materialize_metrics(entries, normalized)
        result_chunks = self._run_sdk(df, sdk_metrics, entries)
        return self._collect_results(
            result_chunks,
            record_id,
            per_call_thresholds=thresholds,
            per_call_flag_thresholds=flag_thresholds,
            fallback_messages=fallback_messages,
        )

    def evaluate_batch(
        self,
        items: Sequence[Mapping[str, Any]],
        *,
        metrics: Sequence[str] | None = None,
        categories: Sequence[str] | None = None,
        thresholds: Mapping[str, float] | None = None,
        flag_thresholds: Mapping[str, float] | None = None,
        fallback_messages: Mapping[str, str] | None = None,
    ) -> list[ResultBundle]:
        bundles: list[ResultBundle] = []
        for i, item in enumerate(items):
            bundles.append(
                self.evaluate(
                    metrics=metrics,
                    categories=categories,
                    thresholds=thresholds,
                    flag_thresholds=flag_thresholds,
                    fallback_messages=fallback_messages,
                    record_id=str(item.get("interaction_id", f"eval_{i + 1}")),
                    **{
                        k: v
                        for k, v in item.items()
                        if k != "interaction_id"
                    },
                )
            )
        return bundles

    # ----- internals -----

    def _select_entries(
        self,
        metrics: Sequence[str] | None,
        categories: Sequence[str] | None,
        available_fields: set[str],
    ) -> list[MetricEntry]:
        """Resolve which metrics to run.

        Explicit ``metrics=`` is strict: every named metric runs, and missing
        required fields raise. ``categories=`` and auto-select are lenient:
        they silently drop metrics in the chosen group(s) whose requirements
        aren't met by the supplied data.
        """
        if metrics:
            return self._registry.filter_by_name(metrics)
        if categories:
            in_category = self._registry.filter_by_category(categories)
            return [
                e for e in in_category if self._registry._satisfied(e, available_fields)
            ]
        return self._registry.auto_select(available_fields)

    @staticmethod
    def _build_dataframe(normalized: Mapping[str, Any]) -> "pd.DataFrame":
        import pandas as pd

        # Single-row DataFrame: every field becomes a one-element column.
        # Fields whose value is already a list (e.g. context, tool_calls) keep
        # their internal shape; pandas stores the list as a cell value.
        # ``params`` is metric-config, not a data column — exclude it from the row.
        row = {field: [value] for field, value in normalized.items() if field != "params"}
        return pd.DataFrame(row)

    def _materialize_metrics(
        self,
        entries: Sequence[MetricEntry],
        normalized: Mapping[str, Any],
    ) -> list[Any]:
        """Return the list of SDK metric objects to evaluate.

        Some SDK metrics take per-call configuration via constructor kwargs
        (not data columns) — when those inputs are present we re-instantiate
        with the caller's values so the registry holds reusable defaults but
        each call can be policy-tuned. Affects:

        * Pattern metrics (KeywordDetection, RegexDetection) — bind ``params``
        * System-prompt-bound metrics (PromptSafetyRisk, TopicRelevance) —
          bind ``system_prompt``
        """
        materialized: list[Any] = []
        params = normalized.get("params")
        system_prompt = normalized.get("system_prompt")
        for entry in entries:
            if entry.category == "pattern" and params is not None:
                materialized.append(self._reconfigure_pattern_metric(entry, params))
            elif entry.name in ("Prompt Safety Risk", "Topic Relevance") and system_prompt:
                materialized.append(
                    self._reconfigure_system_prompt_metric(entry, system_prompt)
                )
            else:
                materialized.append(entry.metric)
        return materialized

    @staticmethod
    def _reconfigure_pattern_metric(entry: MetricEntry, params: dict) -> Any:
        """Rebuild a Keyword/Regex metric with caller-supplied parameters."""
        if entry.name == "Keyword Detection":
            from ibm_watsonx_gov.metrics import KeywordDetectionMetric  # type: ignore

            keywords = params.get("keywords")
            if not keywords:
                raise MetricExecutionError(
                    entry.name,
                    ValueError("params['keywords'] is required for Keyword Detection"),
                )
            return KeywordDetectionMetric(
                keywords=list(keywords),
                case_sensitive=bool(params.get("case_sensitive", False)),
            )
        if entry.name == "Regex Detection":
            from ibm_watsonx_gov.metrics import RegexDetectionMetric  # type: ignore

            patterns = params.get("patterns") or (
                [params["pattern"]] if params.get("pattern") else None
            )
            if not patterns:
                raise MetricExecutionError(
                    entry.name,
                    ValueError(
                        "params['pattern'] or params['patterns'] is required for Regex Detection"
                    ),
                )
            return RegexDetectionMetric(regex_patterns=list(patterns))
        return entry.metric

    @staticmethod
    def _reconfigure_system_prompt_metric(entry: MetricEntry, system_prompt: str) -> Any:
        """Rebuild PromptSafetyRisk / TopicRelevance with the caller-supplied system_prompt.

        The SDK requires ``system_prompt`` at construction time; we pass a
        placeholder when building the registry, then re-instantiate here.
        """
        if entry.name == "Prompt Safety Risk":
            from ibm_watsonx_gov.metrics import PromptSafetyRiskMetric  # type: ignore

            return PromptSafetyRiskMetric(
                method="granite_guardian", system_prompt=system_prompt
            )
        if entry.name == "Topic Relevance":
            from ibm_watsonx_gov.metrics import TopicRelevanceMetric  # type: ignore

            return TopicRelevanceMetric(system_prompt=system_prompt)
        return entry.metric

    def _run_sdk(
        self,
        df: "pd.DataFrame",
        sdk_metrics: list[Any],
        entries: Sequence[MetricEntry],
    ) -> list[tuple["pd.DataFrame", list[MetricEntry], str]]:
        """Run SDK metric evaluation with per-call field routing.

        For single-field safety/quality metrics that accept either ``input_text``
        or ``generated_text`` (``accepts_fields=_EITHER_INPUT_OR_OUTPUT``), this
        method points the SDK at whichever field the partner populated. When
        BOTH fields are populated, the metric is run twice and its results are
        surfaced with suffixed names — ``"Harm (input)"`` and ``"Harm (output)"``
        — so partners see both scores and decide what to do (no merge imposed).

        Multi-field metrics (Faithfulness, Retrieval Precision, etc.) and
        explicitly-scoped ones (PII Detection, Output PII Detection, etc.) use
        their default/specific field bindings; the wrapper does not reroute them.

        Returns a list of ``(result_df, entries_in_chunk, name_suffix)`` tuples,
        one per SDK call made.
        """
        try:
            from ibm_watsonx_gov.config import GenAIConfiguration  # type: ignore
        except Exception as exc:
            raise EvaluatorInitError(
                f"Failed to import GenAIConfiguration: {exc}"
            ) from exc

        from .metrics import (
            _EITHER_INPUT_OR_OUTPUT,
            _INPUT_ONLY,
            _OUTPUT_ONLY,
        )

        def _is_populated(column: str) -> bool:
            if column not in df.columns:
                return False
            val = df[column].iloc[0]
            if val is None:
                return False
            if isinstance(val, str) and val == "":
                return False
            if isinstance(val, list) and len(val) == 0:
                return False
            return True

        has_input = _is_populated("input_text")
        has_output = _is_populated("generated_text")

        # Bucket (entry, metric) pairs by which field they should scan.
        input_group: list[tuple[MetricEntry, Any]] = []
        output_group: list[tuple[MetricEntry, Any]] = []
        default_group: list[tuple[MetricEntry, Any]] = []
        both_input_group: list[tuple[MetricEntry, Any]] = []
        both_output_group: list[tuple[MetricEntry, Any]] = []

        for entry, metric in zip(entries, sdk_metrics):
            af = entry.accepts_fields
            if af == _INPUT_ONLY:
                input_group.append((entry, metric))
            elif af == _OUTPUT_ONLY:
                output_group.append((entry, metric))
            elif af == _EITHER_INPUT_OR_OUTPUT:
                if has_input and has_output:
                    both_input_group.append((entry, metric))
                    both_output_group.append((entry, metric))
                elif has_output:
                    output_group.append((entry, metric))
                else:
                    # has_input or neither — default to input-side scanning
                    input_group.append((entry, metric))
            else:
                # Multi-field metrics (RAG generation/retrieval, system-prompt
                # bound, tool-call, etc.) — use the default config.
                default_group.append((entry, metric))

        cfg_input = GenAIConfiguration(
            input_fields=["input_text"],
            output_fields=["generated_text"],
            context_fields=["context"],
        )
        cfg_output = GenAIConfiguration(
            input_fields=["generated_text"],
            output_fields=["generated_text"],
            context_fields=["context"],
        )

        result_chunks: list[tuple["pd.DataFrame", list[MetricEntry], str]] = []

        def _run_group(group, config, suffix):
            if not group:
                return
            entries_in_group = [e for e, _ in group]
            metrics_in_group = [m for _, m in group]
            if config is not None:
                self._sdk_evaluator.configuration = config
            try:
                result = self._sdk_evaluator.evaluate(
                    data=df, metrics=metrics_in_group
                )
                result_chunks.append(
                    (result.to_df(), entries_in_group, suffix)
                )
            except Exception as exc:
                metric_names = [e.name for e in entries_in_group]
                raise MetricExecutionError(
                    ", ".join(metric_names), exc
                ) from exc

        try:
            _run_group(default_group, None, "")
            _run_group(input_group, cfg_input, "")
            _run_group(output_group, cfg_output, "")
            _run_group(both_input_group, cfg_input, " (input)")
            _run_group(both_output_group, cfg_output, " (output)")
        finally:
            # Restore default config so we don't leak per-call state.
            self._sdk_evaluator.configuration = self._default_config

        return result_chunks

    def _collect_results(
        self,
        result_chunks: list[tuple["pd.DataFrame", list[MetricEntry], str]],
        record_id: str,
        *,
        per_call_thresholds: Mapping[str, float] | None,
        per_call_flag_thresholds: Mapping[str, float] | None = None,
        fallback_messages: Mapping[str, str] | None = None,
    ) -> ResultBundle:
        results: dict[str, GuardrailResult] = {}
        for result_df, entries_in_chunk, suffix in result_chunks:
            columns = (
                set(result_df.columns) if hasattr(result_df, "columns") else set()
            )
            for entry in entries_in_chunk:
                spec = self._threshold_resolver.resolve(
                    entry.name,
                    entry.category,
                    entry.threshold_spec,
                    per_call=per_call_thresholds,
                    per_call_flag=per_call_flag_thresholds,
                )
                score = self._extract_score(result_df, entry, columns)
                passed, action = spec.apply(score)
                fallback = self._resolve_fallback(
                    entry, action, fallback_messages
                )
                key = entry.name + suffix
                results[key] = GuardrailResult(
                    metric=key,
                    category=entry.category,
                    score=score,
                    passed=passed,
                    action=action,
                    column=(
                        entry.column_name if entry.column_name in columns else None
                    ),
                    threshold=spec.value,
                    flag_threshold=spec.flag_value,
                    fallback_message=fallback,
                )
        return ResultBundle.from_mapping(record_id, results)

    @staticmethod
    def _resolve_fallback(
        entry: MetricEntry,
        action: str,
        fallback_messages: Mapping[str, str] | None,
    ) -> str | None:
        """Pick the right fallback message for a Block action.

        Precedence: per-call override (by metric name) > category default >
        ``None``. Returned ``None`` for non-Block actions.
        """
        if action != "Block":
            return None
        if fallback_messages and entry.name in fallback_messages:
            return fallback_messages[entry.name]
        # Category-level defaults from metrics module
        from .metrics import CATEGORY_FALLBACK_MESSAGES

        return CATEGORY_FALLBACK_MESSAGES.get(entry.category)

    @staticmethod
    def _extract_score(
        result_df: "pd.DataFrame",
        entry: MetricEntry,
        columns: set[str],
    ) -> float | None:
        if entry.column_name not in columns:
            logger.warning(
                "Expected column %r for metric %r not found in SDK output (have %s)",
                entry.column_name,
                entry.name,
                sorted(columns),
            )
            return None
        try:
            raw = result_df[entry.column_name].iloc[0]
            if raw is None:
                return None
            return float(raw)
        except (KeyError, IndexError, TypeError, ValueError):
            logger.warning("Could not coerce score for %r", entry.name, exc_info=True)
            return None
