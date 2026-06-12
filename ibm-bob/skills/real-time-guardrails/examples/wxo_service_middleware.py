"""WXO SERVICE-LAYER MIDDLEWARE — Approach 2 in 9_watsonx_orchestrate_integration.xml.

Attach guardrails as FastAPI middleware on the partner-owned service that
WXO tools call. Best for RAG-heavy WXO agents whose tools mostly hit ONE
retrieval API.

Topology:
  user → WXO (managed) → tool function → HTTP → THIS service (with middleware) → vector DB
                                                       ↑
                                                  guardrails fire here

What this middleware sees:
  ① INPUT (request body) — the query the tool sends. Note: this may have
     been REWRITTEN by the tool from the user's original message.
  ② RETRIEVAL — if the service returns retrieved docs, run RAG retrieval
     quality on them before the response leaves.
  (No OUTPUT-stage safety check — the service's response goes back to the
   tool, which formats it for the agent. If you want output safety on the
   final tool result, layer Approach 1 on top of this.)

What it CANNOT see:
  - The user's original message (the tool may have rewritten the query)
  - WXO's final answer to the user

Drop into your partner-owned FastAPI service. The example assumes the
orbital-outfitter / typical RAG-retrieval shape:
  POST /retrieve  body: {"query": "...", "k": 5}
                  resp: {"results": [{"text": "...", "score": ..., ...}, ...]}
"""

from __future__ import annotations

import json
import os

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from real_time_guardrails import AuditLogger, GuardrailsEvaluator


# ────────────────────────────────────────────────────────────────────────
# RULE 16: build evaluator ONCE at app startup
# ────────────────────────────────────────────────────────────────────────

app = FastAPI()
_ev = GuardrailsEvaluator()

# Code Engine / K8s tools often have ephemeral filesystems — use a sink
# that writes to IBM Cloud Logs / Splunk / ELK rather than a local file.
# For demo purposes we use /tmp, but partners should swap this in prod:
_audit = AuditLogger(
    path=os.environ.get("GUARDRAILS_AUDIT_PATH", "/tmp/guardrails-audit.jsonl")
)


# ────────────────────────────────────────────────────────────────────────
# Configurable per partner — which metrics to run, which endpoints to guard
# ────────────────────────────────────────────────────────────────────────

GUARDED_ENDPOINTS = {"/retrieve", "/keyword-search"}   # extend for your service
INPUT_CATEGORIES = ["safety"]                            # input metrics on the tool's query
RAG_RETRIEVAL_CATEGORIES = ["rag_retrieval"]             # retrieval-quality metrics


# ────────────────────────────────────────────────────────────────────────
# The middleware
# ────────────────────────────────────────────────────────────────────────

@app.middleware("http")
async def wxo_service_guardrail(request: Request, call_next):
    """Run guardrails on every request to a guarded endpoint."""

    # Only guard the configured endpoints (let /health etc. pass through)
    if request.url.path not in GUARDED_ENDPOINTS:
        return await call_next(request)

    request_id = request.headers.get("X-Request-ID", "wxo-tool-call")

    # === Read the request body (must restore it for downstream handler) ===
    body = await request.body()
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return await call_next(request)   # non-JSON request — let it through

    query = payload.get("query", "")

    # === PRE-HOOK: input safety on the tool's query ==================
    # NOTE: this query is what the TOOL sent to us. WXO may have rewritten
    # the user's original message. For input safety on the literal user
    # message, you need Approach 3 (frontend BFF) instead.
    if query:
        try:
            in_bundle = _ev.evaluate(input_text=query, categories=INPUT_CATEGORIES)
        except Exception as exc:
            app.logger.warning("guardrails input check failed: %s", exc) if hasattr(app, "logger") else None
            in_bundle = None

        if in_bundle is not None:
            _audit.record(
                in_bundle,
                input_payload={"stage": "input", "endpoint": request.url.path, "query": query},
                request_id=request_id,
            )
            if in_bundle.failed():
                msg = (
                    in_bundle.failed()[0].fallback_message
                    or "Request couldn't be processed."
                )
                # Return a 200 with empty results so the tool gets a
                # well-formed response and can serve the fallback to the agent.
                return JSONResponse(
                    {
                        "results": [],
                        "guardrail_action": "Block",
                        "guardrail_reason": msg,
                    },
                    status_code=200,
                )

    # === Restore body for downstream handler ============================
    async def _receive():
        return {"type": "http.request", "body": body, "more_body": False}
    request._receive = _receive   # type: ignore[attr-defined]

    # === Downstream handler runs (e.g. Milvus search) ==================
    response = await call_next(request)

    # === POST-HOOK: retrieval quality on the retrieved docs ============
    # Only meaningful for JSON responses with a "results" array of docs.
    if response.headers.get("content-type", "").startswith("application/json"):
        chunks = [c async for c in response.body_iterator]
        resp_body = b"".join(chunks)
        try:
            resp_json = json.loads(resp_body)
            results = resp_json.get("results", [])

            # Extract the doc texts — adapt this to your service's schema.
            # orbital-outfitter shape: results = [{"text": "...", "score": ..., ...}]
            docs = [r.get("text", "") for r in results if r.get("text")]

            if query and docs:
                try:
                    ret_bundle = _ev.evaluate(
                        input_text=query,
                        context=docs,                        # list[str] = retrieval ranking
                        categories=RAG_RETRIEVAL_CATEGORIES,
                    )
                except Exception as exc:
                    ret_bundle = None

                if ret_bundle is not None:
                    _audit.record(
                        ret_bundle,
                        input_payload={"stage": "retrieval",
                                       "endpoint": request.url.path,
                                       "doc_count": len(docs)},
                        request_id=request_id,
                    )
                    if ret_bundle.failed():
                        # Retrieval found nothing relevant — short-circuit
                        # so the agent doesn't hallucinate on noise.
                        return JSONResponse(
                            {
                                "results": [],
                                "guardrail_action": "Block",
                                "guardrail_reason": (
                                    "No sufficiently relevant documents retrieved."
                                ),
                            },
                            status_code=200,
                        )
        except json.JSONDecodeError:
            pass   # non-JSON response — let it pass through unchanged

        # Rebuild the response (we consumed the body_iterator above)
        return Response(
            content=resp_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    return response


# ────────────────────────────────────────────────────────────────────────
# Your existing endpoints (left intact — middleware wraps them transparently)
# ────────────────────────────────────────────────────────────────────────

@app.post("/retrieve")
async def retrieve(payload: dict):
    """Replace this stub with your real retrieval logic (Milvus, OpenSearch, etc.)."""
    query = payload.get("query", "")
    k = payload.get("k", 5)
    # ... your real retrieval here ...
    return {
        "results": [{"text": f"Doc {i} for {query}", "score": 0.9 - i * 0.1} for i in range(k)]
    }


@app.post("/keyword-search")
async def keyword_search(payload: dict):
    """Same pattern — middleware applies transparently."""
    query = payload.get("query", "")
    return {"results": [{"text": f"Keyword match for {query}", "score": 0.85}]}


# ────────────────────────────────────────────────────────────────────────
# Deployment notes (read also: 9_watsonx_orchestrate_integration.xml)
# ────────────────────────────────────────────────────────────────────────
# Code Engine:
#   ibmcloud ce app create --name your-rag-svc \
#       --image <your-image> \
#       --env WATSONX_APIKEY=$WATSONX_APIKEY \
#       --env WXG_SERVICE_INSTANCE_ID=$WXG_SERVICE_INSTANCE_ID \
#       --env WXG_PROJECT_ID=$WXG_PROJECT_ID \
#       --env GUARDRAILS_AUDIT_PATH=/tmp/audit.jsonl
#
# Kubernetes:
#   Add the secrets to your Secret manifest; mount as env vars in the
#   deployment spec. See 5_deployment.xml for the full K8s pattern.
