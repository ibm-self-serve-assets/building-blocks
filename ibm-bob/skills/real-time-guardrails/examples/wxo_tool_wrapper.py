"""WXO TOOL WRAPPING — Approach 1 in 9_watsonx_orchestrate_integration.xml.

Wrap the body of @tool() decorated functions with real-time guardrails.
This is the most flexible WXO integration — works for any tool topology,
each tool can have its own policy, no infrastructure changes.

Topology:
  user → WXO (managed) → calls THIS tool → your retrieval/API/logic → tool returns → WXO → user

What this wrapper attaches:
  ① INPUT safety   — on the tool's query arg
  ② RETRIEVAL      — if the tool fetches docs, on those docs
  ③ OUTPUT safety  — on the formatted text the tool returns to the agent

What it CANNOT see:
  - The user's original message (WXO may have rewritten it for the tool)
  - WXO's reasoning between tool calls
  - WXO's final answer to the user

Copy this file into your partner project, replace `your_retrieval_function`
and `format_for_agent` with your real implementations, push to WXO via:
  orchestrate tools import -k python -f wxo_tool_wrapper.py
"""

from __future__ import annotations

# WXO SDK
from ibm_watsonx_orchestrate.agent_builder.tools import tool

# Our SDK (must be installed in the same Python env as the tool runtime)
from real_time_guardrails import AuditLogger, GuardrailsEvaluator


# ────────────────────────────────────────────────────────────────────────
# RULE 16: build the evaluator ONCE at module import, not per tool call.
# WXO loads this module once per worker; this constructor runs once.
# ────────────────────────────────────────────────────────────────────────

_ev = GuardrailsEvaluator()

# For Code Engine / K8s tools (ephemeral filesystem), prefer sink= over path=:
#   _audit = AuditLogger(sink=lambda rec: ibm_cloud_logs_client.send(rec))
# For local development or persistent volumes, file path is fine:
_audit = AuditLogger(path="/var/log/wxo_guardrails/audit.jsonl")


# ────────────────────────────────────────────────────────────────────────
# Replace these two with your real implementations
# ────────────────────────────────────────────────────────────────────────

def your_retrieval_function(query: str) -> list[str]:
    """Stand-in for your real retrieval (vector store, REST API, etc.).
    Returns a list of doc strings."""
    return [f"sample doc for: {query}"]


def format_for_agent(query: str, docs: list[str]) -> str:
    """Stand-in for your real result formatter. Returns the text WXO will
    serve to the agent."""
    return f"Found {len(docs)} relevant result(s) for {query!r}."


# ────────────────────────────────────────────────────────────────────────
# Wrapped tool — preserves the original signature so WXO's introspection
# still works. The wrapping happens INSIDE the function body.
# ────────────────────────────────────────────────────────────────────────

@tool(name="example_retrieval_tool",
      description="Retrieves relevant information for a user query.")
def example_retrieval_tool(query: str) -> str:
    """Guardrailed retrieval tool — 3 in-tool choke points."""

    # ① INPUT SAFETY (cheap — runs first to short-circuit unsafe inputs)
    in_bundle = _ev.evaluate(input_text=query, categories=["safety"])
    _audit.record(
        in_bundle,
        input_payload={"stage": "input", "tool": "example_retrieval_tool", "query": query},
        request_id="wxo-" + (query[:32] if query else "anon"),
    )
    if in_bundle.failed():
        # Return a polite refusal to the agent; the agent will surface it
        # to the user as the tool result.
        return in_bundle.failed()[0].fallback_message or (
            "I can't help with that request. Please rephrase."
        )

    # ─── Your real tool logic runs here ───────────────────────────────
    docs = your_retrieval_function(query)
    answer_text = format_for_agent(query, docs)
    # ──────────────────────────────────────────────────────────────────

    # ② RETRIEVAL QUALITY (only if the tool fetches docs)
    if docs:
        ret_bundle = _ev.evaluate(
            input_text=query,
            context=docs,                  # list[str] = retrieval ranking metrics
            categories=["rag_retrieval"],
        )
        _audit.record(
            ret_bundle,
            input_payload={"stage": "retrieval", "tool": "example_retrieval_tool",
                           "doc_count": len(docs)},
            request_id="wxo-" + (query[:32] if query else "anon"),
        )
        if ret_bundle.failed():
            return (
                "I don't have enough relevant information to answer that. "
                "Please rephrase or provide more context."
            )

    # ③ OUTPUT SAFETY on the formatted text the agent will see
    out_bundle = _ev.evaluate(
        generated_text=answer_text,
        metrics=["PII Detection", "HAP (Hate, Abuse, Profanity)"],
    )
    _audit.record(
        out_bundle,
        input_payload={"stage": "output", "tool": "example_retrieval_tool"},
        request_id="wxo-" + (query[:32] if query else "anon"),
    )
    if out_bundle.failed():
        # Tool generated something unsafe (e.g. leaked PII from a doc) —
        # serve the fallback instead.
        return out_bundle.failed()[0].fallback_message or (
            "I couldn't generate a safe response. Please rephrase."
        )

    # All checks passed (Pass or Flag — Flag is allowed through, logged for review)
    return answer_text


# ────────────────────────────────────────────────────────────────────────
# Optional: wrapping a non-retrieval tool (e.g. database query, email send)
# ────────────────────────────────────────────────────────────────────────
# Skip the retrieval choke point; just input + output checks.

@tool(name="example_action_tool",
      description="Performs a non-retrieval action (DB / email / etc.).")
def example_action_tool(user_request: str) -> str:
    """Guardrailed action tool — input + output checks only (no retrieval stage)."""

    # ① INPUT SAFETY
    in_bundle = _ev.evaluate(input_text=user_request, categories=["safety"])
    _audit.record(in_bundle, input_payload={"stage": "input", "tool": "example_action_tool"})
    if in_bundle.failed():
        return in_bundle.failed()[0].fallback_message or "I can't help with that request."

    # ─── Your real action logic ───────────────────────────────────────
    result = f"Action completed for: {user_request}"
    # ──────────────────────────────────────────────────────────────────

    # ③ OUTPUT SAFETY
    out_bundle = _ev.evaluate(
        generated_text=result,
        metrics=["PII Detection", "HAP (Hate, Abuse, Profanity)"],
    )
    _audit.record(out_bundle, input_payload={"stage": "output", "tool": "example_action_tool"})
    if out_bundle.failed():
        return out_bundle.failed()[0].fallback_message or "Couldn't complete the action safely."

    return result
