from __future__ import annotations

import datetime as dt
import logging
from typing import Any

from real_time_guardrails.core.evaluator import GuardrailsEvaluator
from real_time_guardrails.core.exceptions import (
    GuardrailsError,
    InputShapeError,
    MissingFieldError,
    UnknownCategoryError,
    UnknownMetricError,
)


logger = logging.getLogger(__name__)


_EVALUATE_KWARGS = (
    "input_text",
    "generated_text",
    "context",
    "system_prompt",
    "tool_calls",
    "available_tools",
    "params",
)


def _utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def register_routes(app: Any, evaluator: GuardrailsEvaluator | None) -> None:
    """Mount /api/* routes on ``app``. Lazily builds an evaluator if not supplied."""
    from flask import jsonify, request

    state: dict[str, GuardrailsEvaluator | None] = {"evaluator": evaluator}

    def get_evaluator() -> GuardrailsEvaluator:
        if state["evaluator"] is None:
            state["evaluator"] = GuardrailsEvaluator()
        return state["evaluator"]

    @app.route("/api/health", methods=["GET"])
    def health():  # type: ignore[no-redef]
        return jsonify({"status": "ok", "timestamp": _utcnow()})

    @app.route("/api/metrics", methods=["GET"])
    def metrics():  # type: ignore[no-redef]
        return jsonify(get_evaluator().list_metrics())

    @app.route("/api/evaluate", methods=["POST"])
    def evaluate():  # type: ignore[no-redef]
        body = request.get_json(silent=True) or {}
        try:
            bundle = get_evaluator().evaluate(
                metrics=body.get("metrics"),
                categories=body.get("categories"),
                thresholds=body.get("thresholds"),
                flag_thresholds=body.get("flag_thresholds"),
                fallback_messages=body.get("fallback_messages"),
                record_id=str(body.get("interaction_id", "eval_1")),
                **{k: body.get(k) for k in _EVALUATE_KWARGS},
            )
        except (MissingFieldError, InputShapeError, UnknownMetricError, UnknownCategoryError) as exc:
            return jsonify({"status": "error", "error": str(exc), "type": type(exc).__name__}), 400
        except GuardrailsError as exc:
            logger.exception("Evaluate failed")
            return jsonify({"status": "error", "error": str(exc), "type": type(exc).__name__}), 500
        return jsonify(_serialize_bundle(bundle, body))

    @app.route("/api/evaluate/batch", methods=["POST"])
    def evaluate_batch():  # type: ignore[no-redef]
        body = request.get_json(silent=True) or {}
        items = body.get("items") or []
        if not isinstance(items, list):
            return jsonify({"status": "error", "error": "'items' must be a list"}), 400
        try:
            bundles = get_evaluator().evaluate_batch(
                items,
                metrics=body.get("metrics"),
                categories=body.get("categories"),
                thresholds=body.get("thresholds"),
                flag_thresholds=body.get("flag_thresholds"),
                fallback_messages=body.get("fallback_messages"),
            )
        except (MissingFieldError, InputShapeError, UnknownMetricError, UnknownCategoryError) as exc:
            return jsonify({"status": "error", "error": str(exc), "type": type(exc).__name__}), 400
        except GuardrailsError as exc:
            logger.exception("Batch evaluate failed")
            return jsonify({"status": "error", "error": str(exc), "type": type(exc).__name__}), 500
        return jsonify(
            {
                "status": "success",
                "batch_results": [
                    _serialize_bundle(b, items[i] if i < len(items) else {})
                    for i, b in enumerate(bundles)
                ],
                "total_items": len(bundles),
                "timestamp": _utcnow(),
            }
        )


def _serialize_bundle(bundle: Any, input_payload: dict) -> dict:
    payload = bundle.to_dict()
    return {
        "status": "success",
        "interaction_id": payload["record_id"],
        "metrics_evaluated": payload["metrics_evaluated"],
        "results": {
            name: {
                "category": r["category"],
                "score": r["score"],
                "passed": r["passed"],
                "action": r["action"],
                "column": r["column"],
                "threshold": r["threshold"],
                "flag_threshold": r.get("flag_threshold"),
                "fallback_message": r.get("fallback_message"),
                "guardrail_action": r["action"],  # alias for backwards compat
            }
            for name, r in payload["results"].items()
        },
        "overall_action": bundle.overall_action(),
        "input": {
            k: v
            for k, v in input_payload.items()
            if k not in {"metrics", "categories", "thresholds", "interaction_id"}
        },
        "timestamp": _utcnow(),
    }
