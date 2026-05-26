from __future__ import annotations

import pytest

from real_time_guardrails.core.exceptions import InputShapeError
from real_time_guardrails.core.inputs import ALLOWED_FIELDS, normalize_inputs


def test_normalize_drops_none_values() -> None:
    out = normalize_inputs({"input_text": "hi", "generated_text": None, "context": None})
    assert out == {"input_text": "hi"}


@pytest.mark.parametrize("field", ["input_text", "generated_text", "system_prompt"])
def test_text_fields_accept_str(field: str) -> None:
    assert normalize_inputs({field: "hello"}) == {field: "hello"}


@pytest.mark.parametrize("field", ["input_text", "generated_text", "system_prompt"])
def test_text_fields_accept_list_of_one(field: str) -> None:
    assert normalize_inputs({field: ["hello"]}) == {field: "hello"}


@pytest.mark.parametrize("field", ["input_text", "generated_text", "system_prompt"])
@pytest.mark.parametrize("bad", [["a", "b"], [], 123, {"foo": "bar"}, [123]])
def test_text_fields_reject_bad_shapes(field: str, bad: object) -> None:
    with pytest.raises(InputShapeError) as exc:
        normalize_inputs({field: bad})
    assert exc.value.field == field


def test_context_accepts_string_and_returns_list() -> None:
    assert normalize_inputs({"context": "one doc"}) == {"context": ["one doc"]}


def test_context_accepts_list_of_any_length() -> None:
    assert normalize_inputs({"context": ["a", "b", "c"]}) == {"context": ["a", "b", "c"]}


@pytest.mark.parametrize("bad", [[], [1, 2], 42, {"foo": "bar"}])
def test_context_rejects_bad_shapes(bad: object) -> None:
    with pytest.raises(InputShapeError) as exc:
        normalize_inputs({"context": bad})
    assert exc.value.field == "context"


def test_tool_calls_accepts_list_of_dicts() -> None:
    payload = [{"name": "get_weather", "arguments": {"city": "Tokyo"}}]
    assert normalize_inputs({"tool_calls": payload}) == {"tool_calls": payload}


@pytest.mark.parametrize("bad", [{"a": "b"}, "foo", [1, 2], [{"a": 1}, "x"]])
def test_tool_calls_rejects_bad_shapes(bad: object) -> None:
    with pytest.raises(InputShapeError) as exc:
        normalize_inputs({"tool_calls": bad})
    assert exc.value.field == "tool_calls"


def test_available_tools_accepts_list_of_dicts() -> None:
    payload = [{"name": "tool_a"}, {"name": "tool_b"}]
    assert normalize_inputs({"available_tools": payload}) == {"available_tools": payload}


def test_params_accepts_dict() -> None:
    assert normalize_inputs({"params": {"keywords": ["a", "b"]}}) == {
        "params": {"keywords": ["a", "b"]}
    }


@pytest.mark.parametrize("bad", ["foo", ["a"], 42])
def test_params_rejects_bad_shapes(bad: object) -> None:
    with pytest.raises(InputShapeError) as exc:
        normalize_inputs({"params": bad})
    assert exc.value.field == "params"


def test_unknown_field_raises() -> None:
    with pytest.raises(InputShapeError) as exc:
        normalize_inputs({"ground_truth": "x"})
    assert exc.value.field == "ground_truth"


def test_allowed_fields_constant_in_sync_with_normalizer() -> None:
    # If we add a field, this test forces the normalizer to handle it.
    for name in ALLOWED_FIELDS:
        value = "hi" if name in {"input_text", "generated_text", "system_prompt", "context"} else (
            [{"name": "x"}] if name in {"tool_calls", "available_tools"} else {"keywords": ["x"]}
        )
        result = normalize_inputs({name: value})
        assert name in result
