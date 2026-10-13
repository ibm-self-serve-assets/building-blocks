from __future__ import annotations

from typing import Any, Mapping

from .exceptions import InputShapeError


ALLOWED_FIELDS = frozenset(
    {
        "input_text",
        "generated_text",
        "context",
        "system_prompt",
        "tool_calls",
        "available_tools",
        "params",
    }
)

_SINGLE_TEXT_FIELDS = ("input_text", "generated_text", "system_prompt")
_LIST_OF_DICT_FIELDS = ("tool_calls", "available_tools")


def _normalize_single_text(field: str, value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if len(value) != 1 or not isinstance(value[0], str):
            raise InputShapeError(
                field, value, "str or list[str] of length 1"
            )
        return value[0]
    raise InputShapeError(field, value, "str or list[str] of length 1")


def _normalize_context(value: Any) -> list[str]:
    """Always returned as ``list[str]``. Length 1 covers RAG generation; length N covers RAG retrieval."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        if not all(isinstance(item, str) for item in value):
            raise InputShapeError("context", value, "list[str]")
        if len(value) == 0:
            raise InputShapeError("context", value, "non-empty str or list[str]")
        return list(value)
    raise InputShapeError("context", value, "str or list[str]")


def _normalize_list_of_dicts(field: str, value: Any) -> list[dict]:
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return [dict(item) for item in value]
    raise InputShapeError(field, value, "list[dict]")


def _normalize_params(value: Any) -> dict:
    if isinstance(value, dict):
        return dict(value)
    raise InputShapeError("params", value, "dict")


def normalize_inputs(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Coerce caller-supplied fields into the canonical row-shape.

    Permissive at the boundary (accepts ``str`` or ``list[str]`` of length 1 for
    text fields; ``str`` or ``list[str]`` of any length for ``context``) and
    strict internally (raises :class:`InputShapeError` on unsupported shapes).
    Unknown fields raise the same error.

    ``None`` values are dropped (a missing field is signalled by absence, not
    presence of ``None``).
    """
    out: dict[str, Any] = {}
    for field, value in raw.items():
        if value is None:
            continue
        if field not in ALLOWED_FIELDS:
            raise InputShapeError(
                field,
                value,
                f"one of the supported fields: {sorted(ALLOWED_FIELDS)}",
            )
        if field in _SINGLE_TEXT_FIELDS:
            out[field] = _normalize_single_text(field, value)
        elif field == "context":
            out[field] = _normalize_context(value)
        elif field in _LIST_OF_DICT_FIELDS:
            out[field] = _normalize_list_of_dicts(field, value)
        elif field == "params":
            out[field] = _normalize_params(value)
    return out
