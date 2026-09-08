from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from real_time_guardrails.core.results import GuardrailResult, ResultBundle
from real_time_guardrails.mcp.server import make_tool_functions


def _bundle(metric: str, action: str = "Pass") -> ResultBundle:
    return ResultBundle.from_mapping(
        "eval_1",
        {
            metric: GuardrailResult(
                metric=metric,
                category="safety",
                score=0.1,
                passed=True,
                action=action,  # type: ignore[arg-type]
                column=metric.lower(),
                threshold=0.5,
            )
        },
    )


@pytest.fixture
def fake_eval() -> MagicMock:
    ev = MagicMock()
    ev.evaluate.return_value = _bundle("PII Detection")
    ev.list_metrics.return_value = {"total": 28, "metrics": []}
    return ev


@pytest.fixture
def tools(fake_eval: MagicMock):
    return make_tool_functions(fake_eval)


def test_all_nine_tools_registered(tools: dict) -> None:
    assert set(tools.keys()) == {
        "evaluate",
        "evaluate_safety",
        "evaluate_prompt_safety",
        "evaluate_rag_generation",
        "evaluate_rag_retrieval",
        "evaluate_quality",
        "evaluate_pattern",
        "evaluate_tool_call",
        "list_metrics",
    }


def test_list_metrics_delegates(tools: dict, fake_eval: MagicMock) -> None:
    payload = tools["list_metrics"]()
    assert payload["total"] == 28
    fake_eval.list_metrics.assert_called_once()


def test_evaluate_safety_input_role(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_safety"]("hello")
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["input_text"] == "hello"
    assert kwargs["categories"] == ["safety"]
    assert "generated_text" not in kwargs or kwargs.get("generated_text") is None


def test_evaluate_safety_output_role(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_safety"]("hello", role="output")
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["generated_text"] == "hello"


def test_evaluate_prompt_safety_packs_correct_metrics(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_prompt_safety"]("input", "you are an assistant")
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["system_prompt"] == "you are an assistant"
    assert set(kwargs["metrics"]) == {"Prompt Safety Risk", "Topic Relevance"}


def test_evaluate_rag_generation_uses_category(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_rag_generation"]("q", "a", "c")
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["categories"] == ["rag_generation"]
    assert kwargs["context"] == "c"


def test_evaluate_rag_retrieval_passes_list_context(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_rag_retrieval"]("q", ["d1", "d2", "d3"])
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["categories"] == ["rag_retrieval"]
    assert kwargs["context"] == ["d1", "d2", "d3"]


def test_evaluate_pattern_with_keywords(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_pattern"]("text", keywords=["secret"])
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["metrics"] == ["Keyword Detection"]
    assert kwargs["params"] == {"keywords": ["secret"]}


def test_evaluate_pattern_with_regex(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_pattern"]("text", pattern=r"\d+")
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["metrics"] == ["Regex Detection"]
    assert kwargs["params"] == {"pattern": r"\d+"}


def test_evaluate_pattern_requires_keywords_or_pattern(tools: dict) -> None:
    with pytest.raises(ValueError):
        tools["evaluate_pattern"]("text")


def test_evaluate_tool_call_with_available_tools(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_tool_call"](
        "q",
        tool_calls=[{"name": "x"}],
        available_tools=[{"name": "x"}],
    )
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert set(kwargs["metrics"]) == {"Tool Call Accuracy", "Tool Call Relevance"}


def test_evaluate_tool_call_without_available_tools(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate_tool_call"]("q", tool_calls=[{"name": "x"}])
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["metrics"] == ["Tool Call Accuracy"]


def test_generic_evaluate_forwards_all_kwargs(tools: dict, fake_eval: MagicMock) -> None:
    tools["evaluate"](
        input_text="i",
        generated_text="o",
        context="c",
        metrics=["Faithfulness"],
        thresholds={"Faithfulness": 0.2},
    )
    kwargs = fake_eval.evaluate.call_args.kwargs
    assert kwargs["input_text"] == "i"
    assert kwargs["generated_text"] == "o"
    assert kwargs["context"] == "c"
    assert kwargs["metrics"] == ["Faithfulness"]
    assert kwargs["thresholds"] == {"Faithfulness": 0.2}


def test_each_tool_returns_dict(tools: dict, fake_eval: MagicMock) -> None:
    out = tools["evaluate_safety"]("hi")
    assert isinstance(out, dict)
    assert "results" in out
