from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, replace
from enum import Enum, auto
from pathlib import Path
from typing import Mapping

from .exceptions import ConfigError
from .results import Category, GuardrailAction


logger = logging.getLogger(__name__)


class Direction(Enum):
    HIGH_IS_RISK = auto()  # score >= threshold → Block (e.g. safety, pattern matches)
    LOW_IS_RISK = auto()   # score <= threshold → Block (e.g. RAG, quality)


@dataclass(frozen=True)
class ThresholdSpec:
    """Threshold policy for a single metric.

    Three-state model: a score that crosses ``value`` triggers ``Block``; one
    that crosses ``flag_value`` (but not ``value``) triggers ``Flag``; otherwise
    ``Pass``. ``flag_value=None`` disables the Flag state for binary metrics.

    For ``HIGH_IS_RISK``, ``flag_value`` should be **less than** ``value``
    (e.g. flag=0.4, block=0.65 — Safety default). For ``LOW_IS_RISK``,
    ``flag_value`` should be **greater than** ``value`` (e.g. flag=0.3,
    block=0.1 — RAG default). Inconsistent values raise ``ConfigError`` at
    construction.
    """

    value: float
    direction: Direction
    actionable: bool = True
    flag_value: float | None = None

    def __post_init__(self) -> None:
        # Validate flag/block ordering for the metric's direction.
        if self.flag_value is None:
            return
        if self.direction is Direction.HIGH_IS_RISK:
            if self.flag_value >= self.value:
                raise ConfigError(
                    f"ThresholdSpec for HIGH_IS_RISK: flag_value ({self.flag_value}) "
                    f"must be strictly less than block value ({self.value})."
                )
        else:
            if self.flag_value <= self.value:
                raise ConfigError(
                    f"ThresholdSpec for LOW_IS_RISK: flag_value ({self.flag_value}) "
                    f"must be strictly greater than block value ({self.value})."
                )

    def with_value(self, new_value: float) -> "ThresholdSpec":
        """Return a copy with a new block threshold.

        If the new block value invalidates the existing ``flag_value`` (e.g.
        the user lowered the block threshold below the flag threshold for a
        HIGH_IS_RISK metric), the flag state is silently disabled rather than
        raising. Override the flag explicitly via :meth:`with_flag_value` if
        you need a non-None flag at the new block level.
        """
        if self.flag_value is None:
            return replace(self, value=new_value)
        if self.direction is Direction.HIGH_IS_RISK:
            still_valid = self.flag_value < new_value
        else:
            still_valid = self.flag_value > new_value
        if still_valid:
            return replace(self, value=new_value)
        # Drop the flag state because it would conflict with the new block value.
        return replace(self, value=new_value, flag_value=None)

    def with_flag_value(self, new_flag_value: float | None) -> "ThresholdSpec":
        """Return a copy with a new flag threshold (``None`` disables Flag state)."""
        return replace(self, flag_value=new_flag_value)

    def apply(self, score: float | None) -> tuple[bool | None, GuardrailAction]:
        """Return ``(passed, action)`` for ``score`` under this spec.

        - Non-actionable: returns ``"---"``; ``passed`` reflects safe-side
          status only.
        - ``score is None``: returns ``(None, "Pass")`` — metric produced no value.
        - ``flag_value=None``: only two states, ``Pass`` or ``Block``.
        - ``flag_value`` set: three states — score on the risky side of
          ``value`` is ``Block``; on the risky side of ``flag_value`` but not
          ``value`` is ``Flag``; otherwise ``Pass``.
        """
        if score is None:
            return None, "Pass"
        if self.direction is Direction.HIGH_IS_RISK:
            is_blocked = score >= self.value
            is_flagged = (
                self.flag_value is not None and score >= self.flag_value and not is_blocked
            )
        else:
            is_blocked = score <= self.value
            is_flagged = (
                self.flag_value is not None and score <= self.flag_value and not is_blocked
            )
        passed = not is_blocked
        if not self.actionable:
            return passed, "---"
        if is_blocked:
            return False, "Block"
        if is_flagged:
            return True, "Flag"
        return True, "Pass"


# Default thresholds per category. `flag_value` is set when a meaningful
# borderline state exists for the metric category; binary metrics (pattern)
# have no flag state.
CATEGORY_DEFAULTS: dict[Category, ThresholdSpec] = {
    "safety": ThresholdSpec(0.65, Direction.HIGH_IS_RISK, flag_value=0.4),
    "rag_generation": ThresholdSpec(0.1, Direction.LOW_IS_RISK, flag_value=0.3),
    "rag_retrieval": ThresholdSpec(0.1, Direction.LOW_IS_RISK, flag_value=0.3),
    "quality": ThresholdSpec(0.1, Direction.LOW_IS_RISK, flag_value=0.3),
    "topic": ThresholdSpec(0.1, Direction.LOW_IS_RISK, flag_value=0.3),
    # Pattern metrics are binary (1.0 match / 0.0 no-match) — no flag state.
    "pattern": ThresholdSpec(0.5, Direction.HIGH_IS_RISK, flag_value=None),
    "tool_call": ThresholdSpec(0.1, Direction.LOW_IS_RISK, flag_value=0.3),
}


def metric_env_slug(metric_name: str) -> str:
    """Convert a metric display name to the env-var suffix form.

    e.g. ``"HAP (Hate, Abuse, Profanity)"`` → ``"HAP_HATE_ABUSE_PROFANITY"``.
    """
    slug = re.sub(r"[^A-Za-z0-9]+", "_", metric_name).strip("_").upper()
    return slug


def _coerce_float(raw: object, source: str) -> float:
    try:
        return float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Could not parse threshold value from {source}: {raw!r}") from exc


def _load_config_file(path: str | os.PathLike[str]) -> dict:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Threshold config file not found: {p}")
    text = p.read_text(encoding="utf-8")
    suffix = p.suffix.lower()
    if suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as exc:
            raise ConfigError(
                "PyYAML required to load YAML threshold configs. "
                "Install with `pip install pyyaml`."
            ) from exc
        return yaml.safe_load(text) or {}
    if suffix == ".json":
        return json.loads(text)
    raise ConfigError(
        f"Unsupported threshold config file extension {suffix!r} (expected .yaml/.yml/.json)."
    )


class ThresholdResolver:
    """Merges threshold overrides from 4 layers on top of registry defaults.

    Precedence (highest wins):

    1. ``per_call`` — passed to ``evaluate(..., thresholds={...})``
    2. ``constructor`` — passed to ``GuardrailsEvaluator(threshold_overrides={...})``
    3. ``config_path`` — YAML/JSON file (or auto-discovered via env)
    4. environment variables (``GUARDRAILS_THRESHOLD_<METRIC_SLUG>``, ``GUARDRAILS_THRESHOLD_DEFAULT_<CATEGORY>``)
    5. registry default per metric

    Per-call overrides are not stored on the resolver; they're merged at
    resolve time via the ``per_call`` argument to :meth:`resolve`.
    """

    def __init__(
        self,
        constructor: Mapping[str, float] | None = None,
        config_path: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
        known_metrics: set[str] | None = None,
    ) -> None:
        env_map = env if env is not None else os.environ
        self._known_metrics = set(known_metrics or ())
        self._constructor: dict[str, float] = dict(constructor or {})
        self._config_metric, self._config_category = self._parse_config_file(config_path, env_map)
        self._env_metric, self._env_category = self._parse_env(env_map)
        self._warn_unknown_keys(
            "constructor threshold overrides", self._constructor
        )
        self._warn_unknown_keys("config file metric overrides", self._config_metric)
        self._warn_unknown_keys("environment variable metric overrides", self._env_metric)

    # ----- public API -----

    def resolve(
        self,
        metric_name: str,
        category: Category,
        default_spec: ThresholdSpec,
        per_call: Mapping[str, float] | None = None,
        per_call_flag: Mapping[str, float] | None = None,
    ) -> ThresholdSpec:
        """Return the ThresholdSpec for a metric, applying all override layers.

        ``per_call`` overrides the block threshold; ``per_call_flag`` overrides
        the flag threshold. Other layers (constructor / config / env) only
        affect the block threshold — flag thresholds can be tuned via per-call
        or by replacing the default spec at registry build time.
        """
        block_value = self._resolve_value(metric_name, category, default_spec, per_call)
        spec = default_spec.with_value(block_value)
        if per_call_flag is not None and metric_name in per_call_flag:
            spec = spec.with_flag_value(per_call_flag[metric_name])
        return spec

    def effective_threshold(self, metric_name: str, category: Category, default_spec: ThresholdSpec) -> float:
        """Return the *block* threshold currently in force ignoring per-call layer."""
        return self._resolve_value(metric_name, category, default_spec, None)

    # ----- internals -----

    def _resolve_value(
        self,
        metric_name: str,
        category: Category,
        default_spec: ThresholdSpec,
        per_call: Mapping[str, float] | None,
    ) -> float:
        # per_call > constructor > config (metric > category) > env (metric > category) > default
        if per_call and metric_name in per_call:
            return float(per_call[metric_name])
        if metric_name in self._constructor:
            return self._constructor[metric_name]
        if metric_name in self._config_metric:
            return self._config_metric[metric_name]
        if category in self._config_category:
            return self._config_category[category]
        if metric_name in self._env_metric:
            return self._env_metric[metric_name]
        if category in self._env_category:
            return self._env_category[category]
        return default_spec.value

    def _parse_config_file(
        self,
        explicit_path: str | os.PathLike[str] | None,
        env_map: Mapping[str, str],
    ) -> tuple[dict[str, float], dict[Category, float]]:
        path = explicit_path or env_map.get("GUARDRAILS_CONFIG_PATH")
        if not path:
            return {}, {}
        data = _load_config_file(path)
        metric_overrides: dict[str, float] = {}
        category_overrides: dict[Category, float] = {}
        for name, value in (data.get("metrics") or {}).items():
            metric_overrides[name] = _coerce_float(value, f"config metric {name!r}")
        for cat, value in (data.get("defaults") or {}).items():
            if cat not in CATEGORY_DEFAULTS:
                logger.warning(
                    "Threshold config 'defaults.%s' is not a known category; valid: %s",
                    cat,
                    sorted(CATEGORY_DEFAULTS.keys()),
                )
                continue
            category_overrides[cat] = _coerce_float(value, f"config defaults.{cat}")
        return metric_overrides, category_overrides

    def _parse_env(
        self, env_map: Mapping[str, str]
    ) -> tuple[dict[str, float], dict[Category, float]]:
        metric_overrides: dict[str, float] = {}
        category_overrides: dict[Category, float] = {}
        category_prefix = "GUARDRAILS_THRESHOLD_DEFAULT_"
        metric_prefix = "GUARDRAILS_THRESHOLD_"
        slug_to_metric = {metric_env_slug(name): name for name in self._known_metrics}
        for key, raw in env_map.items():
            if key.startswith(category_prefix):
                cat_suffix = key[len(category_prefix):].lower()
                # Normalize: "RAG" → first match in {rag_generation, rag_retrieval}? We treat
                # explicit suffixes as the canonical category name.
                if cat_suffix in CATEGORY_DEFAULTS:
                    category_overrides[cat_suffix] = _coerce_float(raw, key)
                elif cat_suffix == "rag":
                    val = _coerce_float(raw, key)
                    category_overrides["rag_generation"] = val
                    category_overrides["rag_retrieval"] = val
                else:
                    logger.warning(
                        "Env var %s targets unknown category %r; valid: %s",
                        key,
                        cat_suffix,
                        sorted(CATEGORY_DEFAULTS.keys()),
                    )
                continue
            if not key.startswith(metric_prefix):
                continue
            slug = key[len(metric_prefix):]
            if slug in slug_to_metric:
                metric_overrides[slug_to_metric[slug]] = _coerce_float(raw, key)
            else:
                # Defer warning: known_metrics may not have been populated yet during early init.
                # We log later in _warn_unknown_keys.
                metric_overrides[slug] = _coerce_float(raw, key)
        # Replace any slug-keyed entries with name-keyed entries if known_metrics resolves them later.
        return metric_overrides, category_overrides

    def _warn_unknown_keys(self, source: str, mapping: Mapping[str, float]) -> None:
        if not self._known_metrics:
            return
        for name in mapping:
            if name not in self._known_metrics:
                logger.warning(
                    "%s contained unknown metric name %r; ignoring. Known metrics: %s",
                    source,
                    name,
                    sorted(self._known_metrics),
                )

    def attach_known_metrics(self, known_metrics: set[str]) -> None:
        """Late-bind the known metric set (called after registry is built).

        Re-runs unknown-key warnings and rewrites env-var slug keys to display names.
        """
        self._known_metrics = set(known_metrics)
        slug_to_metric = {metric_env_slug(name): name for name in self._known_metrics}
        rewritten: dict[str, float] = {}
        for key, value in self._env_metric.items():
            if key in self._known_metrics:
                rewritten[key] = value
            elif key in slug_to_metric:
                rewritten[slug_to_metric[key]] = value
            else:
                rewritten[key] = value
        self._env_metric = rewritten
        self._warn_unknown_keys("constructor threshold overrides", self._constructor)
        self._warn_unknown_keys("config file metric overrides", self._config_metric)
        self._warn_unknown_keys("environment variable metric overrides", self._env_metric)
