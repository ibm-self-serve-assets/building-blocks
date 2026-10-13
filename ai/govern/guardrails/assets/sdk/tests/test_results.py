from __future__ import annotations

import pytest

from real_time_guardrails.core.results import GuardrailResult, ResultBundle
from real_time_guardrails.core.thresholds import Direction, ThresholdSpec


# -------- ThresholdSpec.apply --------


def test_high_is_risk_blocks_at_or_above_threshold() -> None:
    spec = ThresholdSpec(value=0.65, direction=Direction.HIGH_IS_RISK)
    assert spec.apply(0.65) == (False, "Block")
    assert spec.apply(0.9) == (False, "Block")
    assert spec.apply(0.5) == (True, "Pass")


def test_low_is_risk_blocks_at_or_below_threshold() -> None:
    spec = ThresholdSpec(value=0.1, direction=Direction.LOW_IS_RISK)
    assert spec.apply(0.05) == (False, "Block")
    assert spec.apply(0.1) == (False, "Block")
    assert spec.apply(0.5) == (True, "Pass")


def test_non_actionable_returns_dashes_regardless_of_score() -> None:
    spec = ThresholdSpec(value=0.1, direction=Direction.LOW_IS_RISK, actionable=False)
    passed_low, action_low = spec.apply(0.05)
    passed_high, action_high = spec.apply(0.9)
    assert action_low == "---"
    assert action_high == "---"
    assert passed_low is False
    assert passed_high is True


def test_apply_on_none_score_returns_pass() -> None:
    spec = ThresholdSpec(value=0.65, direction=Direction.HIGH_IS_RISK)
    assert spec.apply(None) == (None, "Pass")


def test_with_value_preserves_direction_and_actionable() -> None:
    spec = ThresholdSpec(value=0.65, direction=Direction.HIGH_IS_RISK, actionable=True)
    updated = spec.with_value(0.5)
    assert updated.value == 0.5
    assert updated.direction is Direction.HIGH_IS_RISK
    assert updated.actionable is True


# -------- FLAG state: 3-state model --------


def test_flag_state_high_is_risk_three_regions() -> None:
    """Safety pattern: flag=0.4, block=0.65. Three regions: Pass / Flag / Block."""
    spec = ThresholdSpec(value=0.65, direction=Direction.HIGH_IS_RISK, flag_value=0.4)
    assert spec.apply(0.3) == (True, "Pass")
    assert spec.apply(0.4) == (True, "Flag")        # flag inclusive on the risky side
    assert spec.apply(0.5) == (True, "Flag")
    assert spec.apply(0.65) == (False, "Block")     # block inclusive on the risky side
    assert spec.apply(0.9) == (False, "Block")


def test_flag_state_low_is_risk_three_regions() -> None:
    """RAG pattern: block=0.1, flag=0.3. Inverted direction."""
    spec = ThresholdSpec(value=0.1, direction=Direction.LOW_IS_RISK, flag_value=0.3)
    assert spec.apply(0.5) == (True, "Pass")
    assert spec.apply(0.3) == (True, "Flag")
    assert spec.apply(0.2) == (True, "Flag")
    assert spec.apply(0.1) == (False, "Block")
    assert spec.apply(0.0) == (False, "Block")


def test_flag_value_none_collapses_to_two_state() -> None:
    """When flag_value=None, the metric is binary Pass/Block — no Flag state."""
    spec = ThresholdSpec(value=0.5, direction=Direction.HIGH_IS_RISK, flag_value=None)
    assert spec.apply(0.49) == (True, "Pass")
    assert spec.apply(0.5) == (False, "Block")


def test_with_value_drops_flag_when_override_invalidates_ordering() -> None:
    """Lowering the block threshold past the flag (HIGH_IS_RISK) drops the flag."""
    spec = ThresholdSpec(value=0.65, direction=Direction.HIGH_IS_RISK, flag_value=0.4)
    updated = spec.with_value(0.3)  # lower than flag=0.4
    assert updated.value == 0.3
    assert updated.flag_value is None     # auto-dropped


def test_with_value_keeps_flag_when_still_valid() -> None:
    """Raising the block threshold (HIGH_IS_RISK) keeps the existing flag."""
    spec = ThresholdSpec(value=0.65, direction=Direction.HIGH_IS_RISK, flag_value=0.4)
    updated = spec.with_value(0.9)
    assert updated.flag_value == 0.4


def test_with_flag_value_updates_in_place() -> None:
    spec = ThresholdSpec(value=0.65, direction=Direction.HIGH_IS_RISK, flag_value=0.4)
    updated = spec.with_flag_value(0.5)
    assert updated.flag_value == 0.5
    updated = spec.with_flag_value(None)
    assert updated.flag_value is None


def test_threshold_construction_rejects_bad_flag_ordering() -> None:
    """Constructing a spec with flag on the wrong side raises ConfigError."""
    from real_time_guardrails.core.exceptions import ConfigError

    with pytest.raises(ConfigError):
        ThresholdSpec(value=0.3, direction=Direction.HIGH_IS_RISK, flag_value=0.5)
    with pytest.raises(ConfigError):
        ThresholdSpec(value=0.5, direction=Direction.LOW_IS_RISK, flag_value=0.3)


def test_non_actionable_ignores_flag() -> None:
    """Non-actionable metrics always return action='---' regardless of flag config."""
    spec = ThresholdSpec(
        value=0.1, direction=Direction.LOW_IS_RISK, flag_value=0.3, actionable=False
    )
    _, action = spec.apply(0.05)
    assert action == "---"
    _, action = spec.apply(0.2)
    assert action == "---"


# -------- ResultBundle --------


def _make(metric: str, action: str = "Pass") -> GuardrailResult:
    return GuardrailResult(
        metric=metric,
        category="safety",
        score=0.1,
        passed=True,
        action=action,  # type: ignore[arg-type]
        column=metric.lower(),
        threshold=0.65,
    )


def test_result_bundle_indexing_and_iteration() -> None:
    a, b = _make("A"), _make("B", action="Block")
    bundle = ResultBundle.from_mapping("eval_1", {"A": a, "B": b})
    assert bundle["A"] is a
    assert list(bundle) == ["A", "B"]
    assert len(bundle) == 2
    assert "A" in bundle


def test_failed_returns_blocked_results() -> None:
    a = _make("A", action="Pass")
    b = _make("B", action="Block")
    c = _make("C", action="---")
    bundle = ResultBundle.from_mapping("eval_1", {"A": a, "B": b, "C": c})
    assert bundle.failed() == [b]
    assert bundle.passed_all() is False


def test_to_dict_roundtrips_keys() -> None:
    bundle = ResultBundle.from_mapping("eval_1", {"A": _make("A")})
    payload = bundle.to_dict()
    assert payload["record_id"] == "eval_1"
    assert payload["metrics_evaluated"] == ["A"]
    assert payload["results"]["A"]["metric"] == "A"


def test_passed_all_true_when_no_blocks() -> None:
    bundle = ResultBundle.from_mapping("eval_1", {"A": _make("A"), "B": _make("B", action="---")})
    assert bundle.passed_all() is True


def test_flagged_returns_only_flag_results() -> None:
    bundle = ResultBundle.from_mapping(
        "eval_1",
        {
            "A": _make("A", action="Pass"),
            "B": _make("B", action="Flag"),
            "C": _make("C", action="Block"),
            "D": _make("D", action="Flag"),
        },
    )
    flagged_names = [r.metric for r in bundle.flagged()]
    assert flagged_names == ["B", "D"]


def test_overall_action_priority_block_beats_flag_beats_pass() -> None:
    block_then_flag = ResultBundle.from_mapping(
        "eval_1",
        {
            "A": _make("A", action="Pass"),
            "B": _make("B", action="Flag"),
            "C": _make("C", action="Block"),
        },
    )
    assert block_then_flag.overall_action() == "Block"

    flag_only = ResultBundle.from_mapping(
        "eval_2", {"A": _make("A", action="Pass"), "B": _make("B", action="Flag")}
    )
    assert flag_only.overall_action() == "Flag"

    pass_only = ResultBundle.from_mapping(
        "eval_3", {"A": _make("A", action="Pass"), "B": _make("B", action="---")}
    )
    assert pass_only.overall_action() == "Pass"


def test_passed_all_treats_flag_as_passing() -> None:
    """Flag is borderline-but-allowed — partners must still serve the response."""
    bundle = ResultBundle.from_mapping(
        "eval_1", {"A": _make("A", action="Pass"), "B": _make("B", action="Flag")}
    )
    assert bundle.passed_all() is True
    bundle = ResultBundle.from_mapping(
        "eval_2", {"A": _make("A", action="Pass"), "B": _make("B", action="Block")}
    )
    assert bundle.passed_all() is False
