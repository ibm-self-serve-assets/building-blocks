from __future__ import annotations

import logging
import textwrap
from pathlib import Path

import pytest

from real_time_guardrails.core.thresholds import (
    CATEGORY_DEFAULTS,
    Direction,
    ThresholdResolver,
    ThresholdSpec,
    metric_env_slug,
)


KNOWN = {
    "HAP (Hate, Abuse, Profanity)",
    "PII Detection",
    "Faithfulness",
    "Answer Completeness (LLM Judge)",
}

SAFETY_DEFAULT = CATEGORY_DEFAULTS["safety"]


# -------- env-var slug encoding --------


@pytest.mark.parametrize(
    ("name", "slug"),
    [
        ("PII Detection", "PII_DETECTION"),
        ("HAP (Hate, Abuse, Profanity)", "HAP_HATE_ABUSE_PROFANITY"),
        ("Answer Completeness (LLM Judge)", "ANSWER_COMPLETENESS_LLM_JUDGE"),
        ("Faithfulness", "FAITHFULNESS"),
    ],
)
def test_metric_env_slug(name: str, slug: str) -> None:
    assert metric_env_slug(name) == slug


# -------- default layer (no overrides) --------


def test_default_returns_registry_default() -> None:
    resolver = ThresholdResolver(env={}, known_metrics=KNOWN)
    out = resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT)
    assert out.value == 0.65
    assert out.direction is Direction.HIGH_IS_RISK


# -------- env layer --------


def test_env_metric_override(filled_env: dict[str, str]) -> None:
    resolver = ThresholdResolver(
        env={"GUARDRAILS_THRESHOLD_PII_DETECTION": "0.3"},
        known_metrics=KNOWN,
    )
    spec = resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT)
    assert spec.value == 0.3


def test_env_category_shortcut() -> None:
    resolver = ThresholdResolver(
        env={"GUARDRAILS_THRESHOLD_DEFAULT_SAFETY": "0.5"},
        known_metrics=KNOWN,
    )
    spec = resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT)
    assert spec.value == 0.5


def test_env_rag_shortcut_applies_to_both_rag_categories() -> None:
    resolver = ThresholdResolver(
        env={"GUARDRAILS_THRESHOLD_DEFAULT_RAG": "0.2"},
        known_metrics=KNOWN,
    )
    rag_default = CATEGORY_DEFAULTS["rag_generation"]
    assert resolver.resolve("Faithfulness", "rag_generation", rag_default).value == 0.2
    assert resolver.resolve("Hit Rate", "rag_retrieval", rag_default).value == 0.2


def test_env_metric_beats_env_category() -> None:
    resolver = ThresholdResolver(
        env={
            "GUARDRAILS_THRESHOLD_DEFAULT_SAFETY": "0.5",
            "GUARDRAILS_THRESHOLD_PII_DETECTION": "0.2",
        },
        known_metrics=KNOWN,
    )
    assert resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT).value == 0.2
    assert resolver.resolve("HAP (Hate, Abuse, Profanity)", "safety", SAFETY_DEFAULT).value == 0.5


# -------- YAML config layer --------


def test_yaml_config_metric_and_category(tmp_path: Path) -> None:
    config = tmp_path / "thresholds.yaml"
    config.write_text(
        textwrap.dedent(
            """
            defaults:
              safety: 0.55
            metrics:
              "PII Detection": 0.25
            """
        ).strip()
    )
    resolver = ThresholdResolver(config_path=config, env={}, known_metrics=KNOWN)
    assert resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT).value == 0.25
    assert resolver.resolve("HAP (Hate, Abuse, Profanity)", "safety", SAFETY_DEFAULT).value == 0.55


def test_json_config_loads(tmp_path: Path) -> None:
    config = tmp_path / "thresholds.json"
    config.write_text('{"metrics": {"PII Detection": 0.4}}')
    resolver = ThresholdResolver(config_path=config, env={}, known_metrics=KNOWN)
    assert resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT).value == 0.4


def test_config_path_from_env(tmp_path: Path) -> None:
    config = tmp_path / "thresholds.yaml"
    config.write_text('metrics:\n  "PII Detection": 0.42\n')
    resolver = ThresholdResolver(env={"GUARDRAILS_CONFIG_PATH": str(config)}, known_metrics=KNOWN)
    assert resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT).value == 0.42


# -------- constructor layer --------


def test_constructor_overrides_beat_env(tmp_path: Path) -> None:
    resolver = ThresholdResolver(
        constructor={"PII Detection": 0.7},
        env={"GUARDRAILS_THRESHOLD_PII_DETECTION": "0.3"},
        known_metrics=KNOWN,
    )
    assert resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT).value == 0.7


# -------- per-call layer (passed at resolve time) --------


def test_per_call_overrides_constructor() -> None:
    resolver = ThresholdResolver(constructor={"PII Detection": 0.7}, env={}, known_metrics=KNOWN)
    spec = resolver.resolve(
        "PII Detection",
        "safety",
        SAFETY_DEFAULT,
        per_call={"PII Detection": 0.9},
    )
    assert spec.value == 0.9


# -------- full precedence chain --------


def test_full_precedence_chain(tmp_path: Path) -> None:
    config = tmp_path / "t.yaml"
    config.write_text('metrics:\n  "PII Detection": 0.5\n')
    resolver = ThresholdResolver(
        constructor={"PII Detection": 0.6},
        config_path=config,
        env={"GUARDRAILS_THRESHOLD_PII_DETECTION": "0.4"},
        known_metrics=KNOWN,
    )
    # No per_call: constructor wins
    assert resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT).value == 0.6
    # With per_call: per_call wins
    assert (
        resolver.resolve(
            "PII Detection",
            "safety",
            SAFETY_DEFAULT,
            per_call={"PII Detection": 0.8},
        ).value
        == 0.8
    )


def test_effective_threshold_ignores_per_call() -> None:
    resolver = ThresholdResolver(
        constructor={"PII Detection": 0.6}, env={}, known_metrics=KNOWN
    )
    assert resolver.effective_threshold("PII Detection", "safety", SAFETY_DEFAULT) == 0.6


# -------- unknown-key warnings --------


def test_unknown_metric_in_constructor_warns_not_raises(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING)
    resolver = ThresholdResolver(
        constructor={"Not A Real Metric": 0.5},
        env={},
        known_metrics=KNOWN,
    )
    spec = resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT)
    assert spec.value == 0.65  # falls back to default
    assert any("Not A Real Metric" in rec.message for rec in caplog.records)


def test_unknown_category_in_yaml_warns(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    config = tmp_path / "t.yaml"
    config.write_text("defaults:\n  bogus: 0.5\n")
    ThresholdResolver(config_path=config, env={}, known_metrics=KNOWN)
    assert any("bogus" in rec.message for rec in caplog.records)


def test_attach_known_metrics_late_binds_env_slugs() -> None:
    # When the env var is parsed before known_metrics is set, the slug is kept;
    # attach_known_metrics later resolves it to the display name.
    resolver = ThresholdResolver(
        env={"GUARDRAILS_THRESHOLD_PII_DETECTION": "0.3"},
        known_metrics=set(),
    )
    resolver.attach_known_metrics(KNOWN)
    assert resolver.resolve("PII Detection", "safety", SAFETY_DEFAULT).value == 0.3
