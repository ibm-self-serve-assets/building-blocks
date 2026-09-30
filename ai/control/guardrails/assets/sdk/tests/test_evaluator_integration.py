"""End-to-end tests that hit the real ibm_watsonx_gov SDK.

Run with ``pytest -m integration``. Skipped automatically if credentials are
absent so unit-test CI runs stay green.
"""

from __future__ import annotations

import os

import pytest


pytestmark = pytest.mark.integration


def _have_creds() -> bool:
    return all(
        os.environ.get(name)
        for name in ("WATSONX_APIKEY", "WXG_SERVICE_INSTANCE_ID", "WXG_PROJECT_ID")
    )


if not _have_creds():
    pytest.skip("watsonx.governance credentials not set", allow_module_level=True)


@pytest.fixture(scope="module")
def evaluator():
    from real_time_guardrails import GuardrailsEvaluator

    return GuardrailsEvaluator()


def test_safety_pii_on_input(evaluator) -> None:
    bundle = evaluator.evaluate(
        input_text="My SSN is 123-45-6789",
        metrics=["PII Detection"],
    )
    r = bundle["PII Detection"]
    assert r.score is not None
    assert 0.0 <= r.score <= 1.0


def test_rag_generation(evaluator) -> None:
    bundle = evaluator.evaluate(
        input_text="What is RAG?",
        generated_text="Retrieval-Augmented Generation combines retrieval with LLM generation.",
        context="RAG augments LLMs with relevant retrieved documents before generation.",
        metrics=["Faithfulness", "Answer Relevance"],
    )
    assert {"Faithfulness", "Answer Relevance"}.issubset(set(bundle.results))


def test_pattern_keyword_detection(evaluator) -> None:
    bundle = evaluator.evaluate(
        input_text="Project Phoenix is confidential",
        params={"keywords": ["Project Phoenix"]},
        metrics=["Keyword Detection"],
    )
    r = bundle["Keyword Detection"]
    assert r.score is not None


def test_list_metrics_returns_28(evaluator) -> None:
    payload = evaluator.list_metrics()
    assert payload["total"] == 28
