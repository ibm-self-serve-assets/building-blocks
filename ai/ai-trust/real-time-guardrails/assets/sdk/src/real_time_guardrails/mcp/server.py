from __future__ import annotations

from typing import Any, Callable, Mapping

from real_time_guardrails.core.evaluator import GuardrailsEvaluator


# ----- pure tool functions (testable without FastMCP) -----


def make_tool_functions(evaluator: GuardrailsEvaluator) -> dict[str, Callable[..., dict]]:
    """Return a name → callable mapping for every MCP tool.

    Kept separate from the FastMCP registration so unit tests can exercise the
    logic without spinning up a real stdio server.
    """

    def _serialize(bundle: Any) -> dict[str, Any]:
        return bundle.to_dict()

    def evaluate(
        input_text: str | None = None,
        generated_text: str | None = None,
        context: str | list[str] | None = None,
        system_prompt: str | None = None,
        tool_calls: list[dict] | None = None,
        available_tools: list[dict] | None = None,
        params: dict | None = None,
        metrics: list[str] | None = None,
        categories: list[str] | None = None,
        thresholds: Mapping[str, float] | None = None,
    ) -> dict:
        """Generic evaluator. Pass any combination of fields + a metric/category filter."""
        return _serialize(
            evaluator.evaluate(
                input_text=input_text,
                generated_text=generated_text,
                context=context,
                system_prompt=system_prompt,
                tool_calls=tool_calls,
                available_tools=available_tools,
                params=params,
                metrics=metrics,
                categories=categories,
                thresholds=thresholds,
            )
        )

    def evaluate_safety(
        text: str,
        role: str = "input",
        thresholds: Mapping[str, float] | None = None,
    ) -> dict:
        """Run all input/output-eligible safety metrics on a single text.

        ``role`` is ``"input"`` (default) or ``"output"`` — controls which field
        the text is sent in.
        """
        kwargs: dict[str, Any] = {"thresholds": thresholds, "categories": ["safety"]}
        if role == "output":
            kwargs["generated_text"] = text
        else:
            kwargs["input_text"] = text
        return _serialize(evaluator.evaluate(**kwargs))

    def evaluate_prompt_safety(
        input_text: str, system_prompt: str, thresholds: Mapping[str, float] | None = None
    ) -> dict:
        """Run Prompt Safety Risk + Topic Relevance — both need the system prompt."""
        return _serialize(
            evaluator.evaluate(
                input_text=input_text,
                system_prompt=system_prompt,
                metrics=["Prompt Safety Risk", "Topic Relevance"],
                thresholds=thresholds,
            )
        )

    def evaluate_rag_generation(
        input_text: str,
        generated_text: str,
        context: str,
        thresholds: Mapping[str, float] | None = None,
    ) -> dict:
        """Run Answer Relevance + Context Relevance + Faithfulness on a single retrieved doc."""
        return _serialize(
            evaluator.evaluate(
                input_text=input_text,
                generated_text=generated_text,
                context=context,
                categories=["rag_generation"],
                thresholds=thresholds,
            )
        )

    def evaluate_rag_retrieval(
        input_text: str,
        contexts: list[str],
        thresholds: Mapping[str, float] | None = None,
    ) -> dict:
        """Run Retrieval Precision + Hit Rate + Reciprocal Rank over the retrieved set."""
        return _serialize(
            evaluator.evaluate(
                input_text=input_text,
                context=contexts,
                categories=["rag_retrieval"],
                thresholds=thresholds,
            )
        )

    def evaluate_quality(
        input_text: str,
        generated_text: str,
        thresholds: Mapping[str, float] | None = None,
    ) -> dict:
        """Run output quality metrics (Answer Completeness, Conciseness, readability, etc.)."""
        return _serialize(
            evaluator.evaluate(
                input_text=input_text,
                generated_text=generated_text,
                categories=["quality"],
                thresholds=thresholds,
            )
        )

    def evaluate_pattern(
        input_text: str,
        keywords: list[str] | None = None,
        pattern: str | None = None,
        thresholds: Mapping[str, float] | None = None,
    ) -> dict:
        """Run Keyword Detection (if keywords given) and/or Regex Detection (if pattern given)."""
        params: dict[str, Any] = {}
        metrics: list[str] = []
        if keywords:
            params["keywords"] = keywords
            metrics.append("Keyword Detection")
        if pattern:
            params["pattern"] = pattern
            metrics.append("Regex Detection")
        if not metrics:
            raise ValueError("Provide at least one of: keywords, pattern.")
        return _serialize(
            evaluator.evaluate(
                input_text=input_text,
                params=params,
                metrics=metrics,
                thresholds=thresholds,
            )
        )

    def evaluate_tool_call(
        input_text: str,
        tool_calls: list[dict],
        available_tools: list[dict] | None = None,
        thresholds: Mapping[str, float] | None = None,
    ) -> dict:
        """Run Tool Call Accuracy (and Relevance if ``available_tools`` is supplied)."""
        metrics = ["Tool Call Accuracy"]
        if available_tools:
            metrics.append("Tool Call Relevance")
        return _serialize(
            evaluator.evaluate(
                input_text=input_text,
                tool_calls=tool_calls,
                available_tools=available_tools,
                metrics=metrics,
                thresholds=thresholds,
            )
        )

    def list_metrics() -> dict:
        """Return the metric catalog (name, category, default + effective thresholds)."""
        return evaluator.list_metrics()

    return {
        "evaluate": evaluate,
        "evaluate_safety": evaluate_safety,
        "evaluate_prompt_safety": evaluate_prompt_safety,
        "evaluate_rag_generation": evaluate_rag_generation,
        "evaluate_rag_retrieval": evaluate_rag_retrieval,
        "evaluate_quality": evaluate_quality,
        "evaluate_pattern": evaluate_pattern,
        "evaluate_tool_call": evaluate_tool_call,
        "list_metrics": list_metrics,
    }


# ----- FastMCP wiring -----


def build_server(evaluator: GuardrailsEvaluator | None = None) -> Any:
    """Build a FastMCP server with all 9 tools registered."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "MCP extras not installed. Install with `pip install real-time-guardrails[mcp]`."
        ) from exc

    if evaluator is None:
        evaluator = GuardrailsEvaluator()
    server = FastMCP("real-time-guardrails")
    for name, fn in make_tool_functions(evaluator).items():
        server.tool(name=name)(fn)
    return server


def serve() -> None:  # pragma: no cover - entry point
    server = build_server()
    server.run("stdio")
