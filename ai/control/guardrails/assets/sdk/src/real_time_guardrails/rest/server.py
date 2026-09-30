from __future__ import annotations

import os
from typing import Any

from real_time_guardrails.core.evaluator import GuardrailsEvaluator


def create_app(evaluator: GuardrailsEvaluator | None = None) -> "Any":
    """Build a Flask app exposing the guardrails REST API.

    Pass a pre-built ``evaluator`` (useful for tests with a mocked SDK).
    Otherwise one is constructed from env vars at first call.
    """
    try:
        from flask import Flask
        from flask_cors import CORS
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "REST extras not installed. Install with `pip install real-time-guardrails[rest]`."
        ) from exc

    app = Flask("real_time_guardrails")

    cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
    origins = [o.strip() for o in cors_origins.split(",")] if cors_origins != "*" else "*"
    CORS(app, resources={r"/api/*": {"origins": origins}})

    from .routes import register_routes

    register_routes(app, evaluator)
    return app
