"""FastAPI middleware that auto-triggers guardrails on every HTTP request.

Drop this into your FastAPI app — your route handlers don't need to change.
Every request gets:
  - INPUT check (pre-hook) before the handler runs. Block → 200 + fallback.
  - OUTPUT check (post-hook) on the response body. Block → 200 + fallback.

Tune which metrics fire by editing INPUT_CATEGORIES and OUTPUT_METRICS.

Run::

    uvicorn middleware_fastapi:app --port 8000
"""

from __future__ import annotations

import json
import os

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from real_time_guardrails import AuditLogger, GuardrailsEvaluator


# ----- One-time setup at startup (RULE 16: build once, share across requests) -----

app = FastAPI()
ev = GuardrailsEvaluator()
audit = AuditLogger(
    path=os.environ.get("GUARDRAILS_AUDIT_PATH", "/tmp/guardrails-audit.jsonl")
)

INPUT_CATEGORIES = ["safety"]                       # what to check on input
OUTPUT_METRICS = ["PII Detection", "HAP (Hate, Abuse, Profanity)"]  # output-only concerns


# ----- The middleware -----

@app.middleware("http")
async def guardrail_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "anonymous")
    body = await request.body()
    payload: dict = {}
    if body:
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {}

    query = payload.get("query", "")

    # === PRE-HOOK: input check (cheap, no LLM cost yet) ===
    if query:
        try:
            in_bundle = ev.evaluate(input_text=query, categories=INPUT_CATEGORIES)
        except Exception as exc:
            # Failure-mode policy: choose fail-open or fail-closed for your environment
            app.logger.warning("guardrails input check failed: %s", exc) if hasattr(app, "logger") else None
            in_bundle = None
        if in_bundle is not None:
            audit.record(in_bundle, input_payload={"stage": "input", "query": query}, request_id=request_id)
            if in_bundle.failed():
                msg = in_bundle.failed()[0].fallback_message
                return JSONResponse(
                    {"action": "Block", "text": msg, "request_id": request_id}
                )

    # Restore the request body so the downstream handler can read it
    async def _receive():
        return {"type": "http.request", "body": body, "more_body": False}
    request._receive = _receive  # type: ignore[attr-defined]

    # === The agent runs here ===
    response = await call_next(request)

    # === POST-HOOK: output check (LLM has already run — its cost is sunk) ===
    if response.headers.get("content-type", "").startswith("application/json"):
        chunks = [c async for c in response.body_iterator]
        resp_body = b"".join(chunks)
        try:
            resp_json = json.loads(resp_body)
            output_text = resp_json.get("text") or resp_json.get("response", "")
            if output_text:
                try:
                    out_bundle = ev.evaluate(
                        input_text=query, generated_text=output_text, metrics=OUTPUT_METRICS
                    )
                except Exception:
                    out_bundle = None
                if out_bundle is not None:
                    audit.record(
                        out_bundle,
                        input_payload={"stage": "output", "query": query, "generated_text": output_text},
                        request_id=request_id,
                    )
                    if out_bundle.failed():
                        msg = out_bundle.failed()[0].fallback_message
                        return JSONResponse(
                            {"action": "Block", "text": msg, "request_id": request_id}
                        )
        except json.JSONDecodeError:
            pass  # non-JSON response — let it pass through unmodified

        # Rebuild the response with the same body (we already consumed the iterator)
        return Response(
            content=resp_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    return response


# ----- Sample handler — your real agent goes here -----

@app.post("/api/chat")
async def chat(payload: dict):
    """Replace with your real agent / LLM call."""
    query = payload.get("query", "")
    return {"text": f"Echo: {query}"}
