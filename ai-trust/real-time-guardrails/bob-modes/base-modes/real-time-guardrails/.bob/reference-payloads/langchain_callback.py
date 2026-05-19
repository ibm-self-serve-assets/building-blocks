"""LangChain integration for real-time-guardrails.

Two pieces:
  1. GuardrailsInputCallback  — fires on on_chain_start (pre-hook). Raises
     to abort the chain when input is blocked.
  2. output_guard()            — RunnableLambda factory that post-processes
     the chain's output (post-hook). Stock LangChain callbacks are
     observational and can't replace outputs, so we wrap the chain instead.

This asymmetry between callbacks-for-input and Runnable-wrapping-for-output
is THE thing to know about LangChain + guardrails. Document it for partners.

Run::

    pip install langchain-core
    set -a && source .env && set +a
    python langchain_callback.py
"""

from __future__ import annotations

from typing import Any, Sequence

# Optional: only imported when you actually use this file
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import Runnable, RunnableLambda

from real_time_guardrails import GuardrailsEvaluator


class GuardrailBlockedInChain(RuntimeError):
    """Raised from the callback to abort a LangChain invocation."""

    def __init__(self, fallback_message: str, bundle):
        self.fallback_message = fallback_message
        self.bundle = bundle
        super().__init__(fallback_message)


# =====================================================================
# Pre-hook: input check via callback (raises to abort the chain)
# =====================================================================

class GuardrailsInputCallback(BaseCallbackHandler):
    """Callback that runs guardrails on chain inputs. Raises on Block."""

    def __init__(
        self,
        evaluator: GuardrailsEvaluator,
        categories: Sequence[str] | None = None,
        metrics: Sequence[str] | None = None,
    ):
        self.ev = evaluator
        self.categories = list(categories) if categories else None
        self.metrics = list(metrics) if metrics else None

    def _extract_query(self, inputs: dict) -> str:
        for key in ("query", "input", "input_text", "question", "prompt"):
            if key in inputs:
                return str(inputs[key])
        if inputs:
            return str(next(iter(inputs.values())))
        return ""

    def on_chain_start(self, serialized, inputs, **kwargs):
        query = self._extract_query(inputs or {})
        if not query:
            return
        bundle = self.ev.evaluate(
            input_text=query, categories=self.categories, metrics=self.metrics
        )
        if bundle.failed():
            msg = bundle.failed()[0].fallback_message or "Your request couldn't be processed."
            raise GuardrailBlockedInChain(fallback_message=msg, bundle=bundle)


# =====================================================================
# Post-hook: output check via Runnable wrapping
# =====================================================================
#
# Stock LangChain callbacks (on_chain_end / on_llm_end) are observational —
# they can't replace outputs. Wrap the chain with a RunnableLambda that
# re-evaluates the result and substitutes a fallback if needed.

def output_guard(
    evaluator: GuardrailsEvaluator,
    metrics: Sequence[str],
    output_key: str | None = None,
) -> Runnable:
    """RunnableLambda that post-checks the chain's output.

    If `output_key` is given, looks up that key in dict results. Otherwise
    treats the whole result as the output text.

    Returns a Runnable that can be composed via `chain | output_guard(...)`.
    """
    metric_list = list(metrics)

    def _check(result: Any) -> Any:
        if isinstance(result, dict):
            output_text = result.get(output_key or "output") or result.get("text") or ""
        else:
            output_text = str(result)
        if not output_text:
            return result

        bundle = evaluator.evaluate(generated_text=output_text, metrics=metric_list)
        if bundle.failed():
            msg = bundle.failed()[0].fallback_message or "I couldn't generate a reliable answer."
            if isinstance(result, dict):
                return {**result, (output_key or "output"): msg, "guardrail_blocked": True}
            return msg
        return result

    return RunnableLambda(_check)


# =====================================================================
# Demo: simple chain with guardrails on both ends
# =====================================================================

def main() -> None:
    ev = GuardrailsEvaluator()

    # A trivial chain — replace with your real chain
    base_chain = RunnableLambda(
        lambda inputs: {"output": f"Echo: {inputs.get('query', '')}"}
    )

    # Compose with output guard (post-hook)
    guarded_chain = base_chain | output_guard(
        ev,
        metrics=["PII Detection", "HAP (Hate, Abuse, Profanity)"],
        output_key="output",
    )

    # Input guard via callback (pre-hook)
    input_callback = GuardrailsInputCallback(ev, categories=["safety"])

    print("--- safe query ---")
    try:
        result = guarded_chain.invoke(
            {"query": "How do I reset my password?"},
            config={"callbacks": [input_callback]},
        )
        print(result)
    except GuardrailBlockedInChain as exc:
        print("Blocked:", exc.fallback_message)

    print("\n--- PII in input ---")
    try:
        result = guarded_chain.invoke(
            {"query": "My SSN is 123-45-6789"},
            config={"callbacks": [input_callback]},
        )
        print(result)
    except GuardrailBlockedInChain as exc:
        print("Blocked at input:", exc.fallback_message)


if __name__ == "__main__":
    main()
