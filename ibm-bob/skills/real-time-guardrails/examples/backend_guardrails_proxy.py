"""Backend proxy that sits between a browser chat widget and the guardrails service.

Two endpoints:

  POST /api/chat          — input check → call agent → output check → return
                            (called by frontend_chat_integration.jsx)
  GET  /api/audit/recent  — serve recent audit records to a dashboard
                            (called by dashboard_skeleton.jsx)

Why a proxy and not direct browser → guardrails:
  - WATSONX_APIKEY must never reach the browser.
  - Audit log lives server-side.
  - Per-tenant policy lookup is a backend concern.
  - Fail-open / fail-closed policy is a backend concern.

Replace `call_my_agent()` with your real LLM / agent client.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, abort, jsonify, request

from real_time_guardrails import AuditLogger, GuardrailsEvaluator


# ----- One-time setup at startup -----

app = Flask(__name__)

# RULE 16: build the evaluator ONCE at startup, share across requests.
ev = GuardrailsEvaluator()

# Audit log path — adjust for your deployment (write-protected dir, rotated daily, etc.)
AUDIT_PATH = Path(os.environ.get("GUARDRAILS_AUDIT_PATH", "/var/log/guardrails/audit.jsonl"))
AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
audit = AuditLogger(path=AUDIT_PATH)


# ----- Replace this with your real agent / LLM client -----

def call_my_agent(query: str) -> str:
    """Stand-in. Replace with your actual model call."""
    return f"Echo: {query}"


# ----- Endpoint: chat with guardrails -----

@app.route("/api/chat", methods=["POST"])
def chat():
    """Browser-facing endpoint. Wraps the agent with input + output guardrails."""
    body = request.get_json(silent=True) or {}
    query = body.get("query", "").strip()
    request_id = (
        request.headers.get("X-Request-ID")
        or body.get("request_id")
        or "anonymous"
    )

    if not query:
        return jsonify({"action": "Error", "text": "Empty query.", "request_id": request_id}), 400

    # === Stage 1: INPUT guardrail ===
    try:
        input_bundle = ev.evaluate(input_text=query, categories=["safety"])
    except Exception as exc:
        # Fail-open: log and continue (alternatively, fail-closed: refuse).
        # Partner-specific policy decision.
        app.logger.exception("Guardrails input check failed: %s", exc)
        input_bundle = None

    if input_bundle is not None:
        audit.record(input_bundle, input_payload={"stage": "input", "query": query}, request_id=request_id)
        if input_bundle.failed():
            # Never leak which metric tripped to the browser.
            msg = (
                input_bundle.failed()[0].fallback_message
                or "Your request couldn't be processed. Please rephrase."
            )
            return jsonify({"action": "Block", "text": msg, "request_id": request_id})

    # === Stage 2: call the agent ===
    agent_output = call_my_agent(query)

    # === Stage 3: OUTPUT guardrail ===
    try:
        output_bundle = ev.evaluate(
            input_text=query,
            generated_text=agent_output,
            # Reserve output-stage checks for things that ONLY the output can reveal —
            # PII leaks, profanity in generated text, hallucinations vs context, etc.
            metrics=["PII Detection", "HAP (Hate, Abuse, Profanity)", "Profanity"],
        )
    except Exception as exc:
        app.logger.exception("Guardrails output check failed: %s", exc)
        output_bundle = None

    if output_bundle is not None:
        audit.record(
            output_bundle,
            input_payload={"stage": "output", "query": query, "generated_text": agent_output},
            request_id=request_id,
        )
        if output_bundle.failed():
            msg = (
                output_bundle.failed()[0].fallback_message
                or "I wasn't able to generate a reliable answer."
            )
            return jsonify({"action": "Block", "text": msg, "request_id": request_id})

        # Flag → return the response but signal the action to the browser
        if output_bundle.flagged():
            return jsonify({"action": "Flag", "text": agent_output, "request_id": request_id})

    return jsonify({"action": "Pass", "text": agent_output, "request_id": request_id})


# ----- Endpoint: serve audit records to the dashboard -----

@app.route("/api/audit/recent", methods=["GET"])
def audit_recent():
    """Return the last N audit records as a JSON array.

    Called by dashboard_skeleton.jsx. In production: add authentication
    (this endpoint should be restricted to compliance dashboard users), add
    pagination, add date filtering. This reference is intentionally minimal.
    """
    limit = min(int(request.args.get("limit", "500")), 5000)
    if not AUDIT_PATH.exists():
        return jsonify({"records": [], "count": 0})

    # Tail the JSONL file. For high-volume deployments, replace with a real
    # log store query (Elasticsearch, Splunk, BigQuery, etc.).
    records: list[dict] = []
    with AUDIT_PATH.open("r", encoding="utf-8") as f:
        # Read all and take last `limit` — fine for typical audit log sizes.
        # For very large logs use a reverse-tail or external store.
        lines = f.readlines()[-limit:]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # skip corrupt lines

    return jsonify({"records": records, "count": len(records)})


# ----- Main -----

if __name__ == "__main__":
    # Production: use a real WSGI/ASGI server (gunicorn, uvicorn, etc.)
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
