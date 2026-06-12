"""Flask before/after_request hooks for auto-trigger guardrails.

Drop into your Flask app — route handlers don't need to change.
INPUT check fires in before_request, OUTPUT check in after_request.

Run::

    python middleware_flask.py
"""

from __future__ import annotations

import json
import os

from flask import Flask, g, jsonify, request

from real_time_guardrails import AuditLogger, GuardrailsEvaluator


# ----- One-time setup (RULE 16) -----

app = Flask(__name__)
ev = GuardrailsEvaluator()
audit = AuditLogger(
    path=os.environ.get("GUARDRAILS_AUDIT_PATH", "/tmp/guardrails-audit.jsonl")
)

INPUT_CATEGORIES = ["safety"]
OUTPUT_METRICS = ["PII Detection", "HAP (Hate, Abuse, Profanity)"]


# ----- PRE-HOOK: input check -----

@app.before_request
def _input_check():
    if request.method != "POST" or not request.is_json:
        return None
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "")
    if not query:
        return None

    # Stash for the after-hook
    g.request_id = request.headers.get("X-Request-ID", "anonymous")
    g.query = query

    try:
        bundle = ev.evaluate(input_text=query, categories=INPUT_CATEGORIES)
    except Exception as exc:
        app.logger.warning("guardrails input check failed: %s", exc)
        return None  # fail-open; switch to short-circuit refusal for fail-closed

    audit.record(bundle, input_payload={"stage": "input", "query": query}, request_id=g.request_id)
    if bundle.failed():
        msg = bundle.failed()[0].fallback_message
        return jsonify({"action": "Block", "text": msg, "request_id": g.request_id})

    return None  # let the request continue to the handler


# ----- POST-HOOK: output check -----

@app.after_request
def _output_check(response):
    # Only inspect JSON responses with a 'text' or 'response' field
    if response.mimetype != "application/json":
        return response
    data = response.get_json(silent=True) or {}
    output_text = data.get("text") or data.get("response", "")
    if not output_text:
        return response

    query = g.get("query", "")
    request_id = g.get("request_id", "anonymous")

    try:
        bundle = ev.evaluate(
            input_text=query, generated_text=output_text, metrics=OUTPUT_METRICS
        )
    except Exception as exc:
        app.logger.warning("guardrails output check failed: %s", exc)
        return response

    audit.record(
        bundle,
        input_payload={"stage": "output", "query": query, "generated_text": output_text},
        request_id=request_id,
    )
    if bundle.failed():
        msg = bundle.failed()[0].fallback_message
        response.set_data(json.dumps({"action": "Block", "text": msg, "request_id": request_id}))

    return response


# ----- Sample handler — your real agent goes here -----

@app.route("/api/chat", methods=["POST"])
def chat():
    """Replace with your real agent / LLM call."""
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "")
    return jsonify({"text": f"Echo: {query}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
