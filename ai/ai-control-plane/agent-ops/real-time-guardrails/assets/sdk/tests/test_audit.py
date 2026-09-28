from __future__ import annotations

import json
from pathlib import Path

import pytest

from real_time_guardrails import AuditLogger
from real_time_guardrails.audit import overall_action_priority
from real_time_guardrails.core.results import GuardrailResult, ResultBundle


def _r(name: str, action: str, score: float = 0.5) -> GuardrailResult:
    return GuardrailResult(
        metric=name,
        category="safety",
        score=score,
        passed=action != "Block",
        action=action,  # type: ignore[arg-type]
        column=name.lower(),
        threshold=0.65,
        flag_threshold=0.4,
    )


def test_logger_requires_path_or_sink() -> None:
    with pytest.raises(ValueError):
        AuditLogger()


def test_file_sink_writes_jsonl_lines(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(path=path)
    bundle = ResultBundle.from_mapping("eval_1", {"A": _r("A", "Pass"), "B": _r("B", "Block")})
    logger.record(bundle, input_payload={"input_text": "hello"}, request_id="req-1")
    bundle2 = ResultBundle.from_mapping("eval_2", {"A": _r("A", "Flag")})
    logger.record(bundle2, input_payload={"input_text": "world"}, request_id="req-2")
    logger.close()

    lines = path.read_text().strip().splitlines()
    assert len(lines) == 2
    rec1 = json.loads(lines[0])
    rec2 = json.loads(lines[1])
    assert rec1["request_id"] == "req-1"
    assert rec1["overall_action"] == "Block"
    assert rec1["blocked_metrics"] == ["B"]
    assert rec2["overall_action"] == "Flag"
    assert rec2["flagged_metrics"] == ["A"]


def test_pluggable_sink_receives_dict_directly() -> None:
    captured: list[dict] = []
    logger = AuditLogger(sink=captured.append)
    bundle = ResultBundle.from_mapping("eval_1", {"A": _r("A", "Block")})
    logger.record(bundle, input_payload={"input_text": "x"}, request_id="r")
    assert len(captured) == 1
    assert captured[0]["overall_action"] == "Block"
    assert captured[0]["request_id"] == "r"


def test_record_includes_per_metric_breakdown() -> None:
    captured: list[dict] = []
    logger = AuditLogger(sink=captured.append)
    bundle = ResultBundle.from_mapping(
        "eval_1",
        {"A": _r("A", "Pass", score=0.1), "B": _r("B", "Block", score=0.9)},
    )
    logger.record(bundle, input_payload={}, request_id="r")
    metrics = captured[0]["metrics"]
    assert set(metrics.keys()) == {"A", "B"}
    assert metrics["A"]["action"] == "Pass"
    assert metrics["A"]["score"] == 0.1
    assert metrics["B"]["threshold"] == 0.65
    assert metrics["B"]["flag_threshold"] == 0.4


def test_input_hash_is_stable_and_short() -> None:
    captured: list[dict] = []
    logger = AuditLogger(sink=captured.append)
    bundle = ResultBundle.from_mapping("eval_1", {"A": _r("A", "Pass")})
    logger.record(bundle, input_payload={"input_text": "abc"}, request_id="r")
    logger.record(bundle, input_payload={"input_text": "abc"}, request_id="r")
    logger.record(bundle, input_payload={"input_text": "different"}, request_id="r")
    assert captured[0]["input_hash"] == captured[1]["input_hash"]
    assert captured[0]["input_hash"] != captured[2]["input_hash"]
    assert len(captured[0]["input_hash"]) == 16


def test_exclude_inputs_drops_raw_payload(tmp_path: Path) -> None:
    captured: list[dict] = []
    logger = AuditLogger(sink=captured.append, include_inputs=False)
    bundle = ResultBundle.from_mapping("eval_1", {"A": _r("A", "Pass")})
    logger.record(bundle, input_payload={"input_text": "secret"}, request_id="r")
    assert "input" not in captured[0]
    # Hash is still present for joinability:
    assert captured[0]["input_hash"]


def test_context_manager_closes_file(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    with AuditLogger(path=path) as logger:
        logger.record(
            ResultBundle.from_mapping("e", {"A": _r("A", "Pass")}),
            input_payload={},
            request_id="r",
        )
    # After context exit the file is closed; another open should work
    assert path.read_text().count("\n") == 1


def test_overall_action_priority_helper() -> None:
    assert overall_action_priority(["Pass", "Flag", "Block"]) == "Block"
    assert overall_action_priority(["Pass", "Flag", "Pass"]) == "Flag"
    assert overall_action_priority(["Pass", "Pass"]) == "Pass"
    assert overall_action_priority(["---", "Pass"]) == "Pass"
