"""@guard decorator — auto-trigger guardrails on any Python function.

Self-contained — partners copy this into their codebase and adapt as needed.
NOT shipped as an SDK feature (per design decision); kept as a reference so
partners can own the policy logic themselves.

Usage::

    from real_time_guardrails import GuardrailsEvaluator
    from decorator_example import guard

    ev = GuardrailsEvaluator()  # built once at startup

    @guard(evaluator=ev, input_categories=["safety"],
           output_metrics=["PII Detection", "HAP (Hate, Abuse, Profanity)"])
    def handle_user_query(query: str) -> str:
        return llm.generate(query)

    # Now every call to handle_user_query() is auto-guarded.

The decorator introspects the wrapped function's signature to find the
input argument (looks for 'query', 'input_text', 'prompt' in that order,
falls back to the first positional arg). Override via `input_arg=` if you
want a specific kwarg name.

On Block:
  - on_block="refuse" (default): returns the fallback_message instead of
    calling the function (input) / instead of the function's result (output)
  - on_block="raise": raises GuardrailBlocked exception

Has an async variant via asyncio.iscoroutinefunction detection.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Awaitable, Callable, Sequence

from real_time_guardrails import GuardrailsEvaluator, ResultBundle


class GuardrailBlocked(Exception):
    """Raised when a guarded function's input or output is blocked and
    on_block='raise'. The bundle is attached for inspection / logging."""

    def __init__(self, stage: str, bundle: ResultBundle, fallback_message: str):
        self.stage = stage
        self.bundle = bundle
        self.fallback_message = fallback_message
        super().__init__(f"[{stage}] {fallback_message}")


_DEFAULT_INPUT_ARG_NAMES = ("query", "input_text", "prompt", "user_input", "text")


def _extract_input(fn: Callable, args: tuple, kwargs: dict, input_arg: str | None) -> str:
    """Find the user-input string in the function's args/kwargs."""
    if input_arg is not None:
        if input_arg in kwargs:
            return str(kwargs[input_arg])
        sig = inspect.signature(fn)
        params = list(sig.parameters)
        if input_arg in params:
            return str(args[params.index(input_arg)])
        raise ValueError(f"input_arg={input_arg!r} not in {fn.__name__} signature")

    # Auto-detect: try the common names, then fall back to first positional
    for name in _DEFAULT_INPUT_ARG_NAMES:
        if name in kwargs:
            return str(kwargs[name])
    sig = inspect.signature(fn)
    params = list(sig.parameters)
    for name in _DEFAULT_INPUT_ARG_NAMES:
        if name in params:
            idx = params.index(name)
            if idx < len(args):
                return str(args[idx])
    if args:
        return str(args[0])
    return ""


def guard(
    *,
    evaluator: GuardrailsEvaluator,
    input_categories: Sequence[str] | None = None,
    input_metrics: Sequence[str] | None = None,
    output_metrics: Sequence[str] | None = None,
    on_block: str = "refuse",  # "refuse" | "raise"
    input_arg: str | None = None,
) -> Callable:
    """Decorator factory. See module docstring for usage."""
    if on_block not in {"refuse", "raise"}:
        raise ValueError(f"on_block must be 'refuse' or 'raise', got {on_block!r}")

    def decorator(fn: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(fn)

        def _maybe_refuse(stage: str, bundle: ResultBundle) -> str | None:
            failed = bundle.failed()
            if not failed:
                return None
            msg = failed[0].fallback_message or "Your request couldn't be processed."
            if on_block == "raise":
                raise GuardrailBlocked(stage=stage, bundle=bundle, fallback_message=msg)
            return msg  # "refuse" semantics

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            user_input = _extract_input(fn, args, kwargs, input_arg)

            # === PRE: input check ===
            if user_input and (input_categories or input_metrics):
                in_bundle = evaluator.evaluate(
                    input_text=user_input,
                    categories=list(input_categories) if input_categories else None,
                    metrics=list(input_metrics) if input_metrics else None,
                )
                refusal = _maybe_refuse("input", in_bundle)
                if refusal is not None:
                    return refusal  # SKIP the wrapped function entirely

            # === Wrapped function runs ===
            result = fn(*args, **kwargs)

            # === POST: output check ===
            if output_metrics and isinstance(result, str):
                out_bundle = evaluator.evaluate(
                    input_text=user_input,
                    generated_text=result,
                    metrics=list(output_metrics),
                )
                refusal = _maybe_refuse("output", out_bundle)
                if refusal is not None:
                    return refusal  # SUBSTITUTE for the result

            return result

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs) -> Any:
            user_input = _extract_input(fn, args, kwargs, input_arg)

            if user_input and (input_categories or input_metrics):
                in_bundle = await asyncio.to_thread(
                    evaluator.evaluate,
                    input_text=user_input,
                    categories=list(input_categories) if input_categories else None,
                    metrics=list(input_metrics) if input_metrics else None,
                )
                refusal = _maybe_refuse("input", in_bundle)
                if refusal is not None:
                    return refusal

            result = await fn(*args, **kwargs)

            if output_metrics and isinstance(result, str):
                out_bundle = await asyncio.to_thread(
                    evaluator.evaluate,
                    input_text=user_input,
                    generated_text=result,
                    metrics=list(output_metrics),
                )
                refusal = _maybe_refuse("output", out_bundle)
                if refusal is not None:
                    return refusal

            return result

        return async_wrapper if is_async else sync_wrapper

    return decorator


# =====================================================================
# Demo
# =====================================================================

def main() -> None:
    ev = GuardrailsEvaluator()

    @guard(
        evaluator=ev,
        input_categories=["safety"],
        output_metrics=["PII Detection", "HAP (Hate, Abuse, Profanity)"],
        on_block="refuse",
    )
    def handle_user_query(query: str) -> str:
        # Stand-in for your real LLM / agent call
        if "SSN" in query.upper():
            # Simulate an LLM that leaks PII in its output
            return f"Your SSN is {query.split()[-1]}, processed."
        return f"Echo: {query}"

    print("safe query:", handle_user_query("How do I reset my password?"))
    print("input-blocked:", handle_user_query("My SSN is 123-45-6789"))


if __name__ == "__main__":
    main()
