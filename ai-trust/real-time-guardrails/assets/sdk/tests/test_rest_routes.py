from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from real_time_guardrails.core.results import GuardrailResult, ResultBundle


flask = pytest.importorskip("flask")
flask_cors = pytest.importorskip("flask_cors")


@pytest.fixture
def fake_evaluator() -> MagicMock:
    ev = MagicMock()
    ev.list_metrics.return_value = {
        "total": 1,
        "metrics": [
            {
                "name": "PII Detection",
                "category": "safety",
                "column": "pii",
                "default_threshold": 0.65,
                "effective_threshold": 0.65,
                "direction": "HIGH_IS_RISK",
                "actionable": True,
                "required_fields": [],
                "accepts_fields": ["generated_text", "input_text"],
                "description": "PII",
            }
        ],
    }
    return ev


@pytest.fixture
def client(fake_evaluator: MagicMock):
    from real_time_guardrails.rest.server import create_app

    app = create_app(evaluator=fake_evaluator)
    app.testing = True
    return app.test_client()


def _bundle_with(metric_name: str, score: float, action: str = "Block") -> ResultBundle:
    result = GuardrailResult(
        metric=metric_name,
        category="safety",
        score=score,
        passed=action == "Pass",
        action=action,  # type: ignore[arg-type]
        column=metric_name.lower(),
        threshold=0.65,
    )
    return ResultBundle.from_mapping("eval_1", {metric_name: result})


def test_health_returns_ok(client) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert "timestamp" in body


def test_metrics_endpoint_returns_list(client) -> None:
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["metrics"][0]["name"] == "PII Detection"


def test_evaluate_happy_path(client, fake_evaluator: MagicMock) -> None:
    fake_evaluator.evaluate.return_value = _bundle_with("PII Detection", 0.9, "Block")
    resp = client.post(
        "/api/evaluate",
        json={"input_text": "My SSN is 123-45-6789", "metrics": ["PII Detection"]},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert body["results"]["PII Detection"]["score"] == 0.9
    assert body["results"]["PII Detection"]["action"] == "Block"
    assert body["results"]["PII Detection"]["guardrail_action"] == "Block"
    # input echo should be present (and not contain selection args)
    assert body["input"]["input_text"] == "My SSN is 123-45-6789"
    assert "metrics" not in body["input"]


def test_evaluate_passes_thresholds_through(client, fake_evaluator: MagicMock) -> None:
    fake_evaluator.evaluate.return_value = _bundle_with("PII Detection", 0.4, "Block")
    client.post(
        "/api/evaluate",
        json={
            "input_text": "x",
            "metrics": ["PII Detection"],
            "thresholds": {"PII Detection": 0.3},
        },
    )
    kwargs = fake_evaluator.evaluate.call_args.kwargs
    assert kwargs["thresholds"] == {"PII Detection": 0.3}


def test_evaluate_missing_field_returns_400(client, fake_evaluator: MagicMock) -> None:
    from real_time_guardrails.core.exceptions import MissingFieldError

    fake_evaluator.evaluate.side_effect = MissingFieldError("Faithfulness", "context")
    resp = client.post(
        "/api/evaluate",
        json={"input_text": "q", "generated_text": "a", "metrics": ["Faithfulness"]},
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["status"] == "error"
    assert body["type"] == "MissingFieldError"
    assert "context" in body["error"]


def test_evaluate_unknown_metric_returns_400(client, fake_evaluator: MagicMock) -> None:
    from real_time_guardrails.core.exceptions import UnknownMetricError

    fake_evaluator.evaluate.side_effect = UnknownMetricError("Bogus", ["PII Detection"])
    resp = client.post("/api/evaluate", json={"input_text": "x", "metrics": ["Bogus"]})
    assert resp.status_code == 400
    assert resp.get_json()["type"] == "UnknownMetricError"


def test_batch_endpoint(client, fake_evaluator: MagicMock) -> None:
    fake_evaluator.evaluate_batch.return_value = [
        _bundle_with("PII Detection", 0.9, "Block"),
        _bundle_with("PII Detection", 0.1, "Pass"),
    ]
    resp = client.post(
        "/api/evaluate/batch",
        json={
            "items": [
                {"input_text": "first", "interaction_id": "row-1"},
                {"input_text": "second", "interaction_id": "row-2"},
            ],
            "metrics": ["PII Detection"],
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total_items"] == 2
    assert body["batch_results"][0]["results"]["PII Detection"]["action"] == "Block"
    assert body["batch_results"][1]["results"]["PII Detection"]["action"] == "Pass"


def test_batch_endpoint_rejects_non_list_items(client) -> None:
    resp = client.post("/api/evaluate/batch", json={"items": "not a list"})
    assert resp.status_code == 400
