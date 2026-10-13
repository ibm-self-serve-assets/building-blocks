"""End-to-end RAG guardrail pipeline built on real-time-guardrails.

Demonstrates the 4-choke-point pattern as a single ``GuardrailedAgent`` class:

    input → INPUT guard → retrieve → RETRIEVAL guard → LLM → OUTPUT guard → user

Every decision is recorded via ``AuditLogger``. Block actions return a
fallback message instead of the LLM output. Flag actions are allowed through
but logged for human review.

Drop in your real model + retriever by replacing the two callbacks:
``retrieve_callback`` and ``model_callback``. The simulated defaults make
this script runnable end-to-end against real watsonx.governance.

Run::

    set -a && source .env && set +a
    python examples/full_pipeline.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Optional

from real_time_guardrails import (
    AuditLogger,
    GuardrailsEvaluator,
    ResultBundle,
)


# ----- Pluggable callbacks (replace with your real implementations) -----


def simulate_retrieve(query: str) -> list[str]:
    """Stand-in retriever. Returns 3 fake docs. Replace with your vector store."""
    canned = {
        "password": [
            "To reset your password, go to Settings > Security > Reset Password.",
            "Password complexity rules: 12+ chars, mixed case, symbol.",
            "Account lockout occurs after 5 failed login attempts.",
        ],
        "weather": [
            "Cats are popular household pets.",
            "Pizza was invented in Naples.",
            "Mountains are tall.",
        ],
    }
    for key, docs in canned.items():
        if key in query.lower():
            return docs
    return ["No relevant docs found."]


def simulate_model(query: str, context: str) -> str:
    """Stand-in LLM. Returns a canned response. Replace with your LLM client."""
    if "password" in query.lower():
        return (
            "To reset your password, go to Settings > Security > Reset Password, "
            "enter your current password, then choose a new password meeting the "
            "complexity rules."
        )
    return f"Based on the available information: {context[:120]}..."


# ----- The pipeline class -----


@dataclass
class PipelineResult:
    request_id: str
    final_response: str
    overall_action: str
    input_bundle: Optional[ResultBundle] = None
    retrieval_bundle: Optional[ResultBundle] = None
    output_bundle: Optional[ResultBundle] = None
    docs: list[str] = field(default_factory=list)


class GuardrailedAgent:
    """A toy RAG agent wrapped in real-time-guardrails at all 4 choke points.

    Constructor takes an ``evaluator`` (built once at startup), an optional
    ``audit`` logger, and pluggable ``retrieve`` / ``model`` callbacks. Call
    ``process_request(user_input, request_id="...")`` to run the full pipeline.
    """

    def __init__(
        self,
        evaluator: GuardrailsEvaluator,
        *,
        audit: AuditLogger | None = None,
        retrieve_callback: Callable[[str], list[str]] = simulate_retrieve,
        model_callback: Callable[[str, str], str] = simulate_model,
    ) -> None:
        self.evaluator = evaluator
        self.audit = audit
        self.retrieve = retrieve_callback
        self.model = model_callback

    # ----- the four choke points -----

    def check_input(self, user_input: str) -> ResultBundle:
        return self.evaluator.evaluate(input_text=user_input, categories=["safety"])

    def check_retrieval(self, user_input: str, docs: list[str]) -> ResultBundle:
        return self.evaluator.evaluate(
            input_text=user_input,
            context=docs,
            categories=["rag_retrieval"],
        )

    def check_output(self, user_input: str, output: str, context: str) -> ResultBundle:
        return self.evaluator.evaluate(
            input_text=user_input,
            generated_text=output,
            context=context,
            categories=["rag_generation"],
        )

    # ----- end-to-end driver -----

    def process_request(self, user_input: str, request_id: str = "req-1") -> PipelineResult:
        # 1. Input guard
        input_bundle = self.check_input(user_input)
        self._audit(input_bundle, {"stage": "input", "input_text": user_input}, request_id)
        if input_bundle.failed():
            msg = self._first_fallback(input_bundle) or "Your request couldn't be processed."
            return PipelineResult(
                request_id=request_id,
                final_response=msg,
                overall_action=input_bundle.overall_action(),
                input_bundle=input_bundle,
            )

        # 2. Retrieval guard
        docs = self.retrieve(user_input)
        retrieval_bundle = self.check_retrieval(user_input, docs)
        self._audit(
            retrieval_bundle,
            {"stage": "retrieval", "input_text": user_input, "doc_count": len(docs)},
            request_id,
        )
        if retrieval_bundle.failed():
            msg = (
                self._first_fallback(retrieval_bundle)
                or "I don't have enough relevant information to answer that."
            )
            return PipelineResult(
                request_id=request_id,
                final_response=msg,
                overall_action=retrieval_bundle.overall_action(),
                input_bundle=input_bundle,
                retrieval_bundle=retrieval_bundle,
                docs=docs,
            )

        # 3. LLM call
        best_context = "\n\n".join(docs[:3])
        output = self.model(user_input, best_context)

        # 4. Output guard
        output_bundle = self.check_output(user_input, output, best_context)
        self._audit(
            output_bundle,
            {"stage": "output", "input_text": user_input, "generated_text": output},
            request_id,
        )
        if output_bundle.failed():
            msg = (
                self._first_fallback(output_bundle)
                or "I wasn't able to generate a reliable answer."
            )
            return PipelineResult(
                request_id=request_id,
                final_response=msg,
                overall_action=output_bundle.overall_action(),
                input_bundle=input_bundle,
                retrieval_bundle=retrieval_bundle,
                output_bundle=output_bundle,
                docs=docs,
            )

        # Pass / Flag — serve the response
        return PipelineResult(
            request_id=request_id,
            final_response=output,
            overall_action=output_bundle.overall_action(),
            input_bundle=input_bundle,
            retrieval_bundle=retrieval_bundle,
            output_bundle=output_bundle,
            docs=docs,
        )

    # ----- internals -----

    def _audit(self, bundle: ResultBundle, payload: dict, request_id: str) -> None:
        if self.audit is not None:
            self.audit.record(bundle, input_payload=payload, request_id=request_id)

    @staticmethod
    def _first_fallback(bundle: ResultBundle) -> str | None:
        for r in bundle.failed():
            if r.fallback_message:
                return r.fallback_message
        return None


# ----- demo -----


def main() -> None:
    ev = GuardrailsEvaluator()
    with AuditLogger(sink=lambda rec: print("AUDIT:", json.dumps(rec, default=str))) as audit:
        agent = GuardrailedAgent(ev, audit=audit)

        scenarios = [
            ("safe query", "How do I reset my password?", "scenario-1"),
            ("PII in user query", "My SSN is 123-45-6789, please log it", "scenario-2"),
            ("off-topic with poor retrieval", "What's the weather in Tokyo?", "scenario-3"),
        ]

        for label, query, req_id in scenarios:
            print(f"\n{'═' * 70}\nScenario: {label}\nQuery: {query!r}\n{'─' * 70}")
            result = agent.process_request(query, request_id=req_id)
            print(f"  Overall action: {result.overall_action}")
            print(f"  Final response: {result.final_response[:120]}")


if __name__ == "__main__":
    main()
