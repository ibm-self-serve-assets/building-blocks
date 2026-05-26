"""Tutorial 02: RAG Quality Guardrails with real-time-guardrails

Two related but distinct checks for RAG agents:

  RAG retrieval — evaluates the *retriever*: did it return relevant docs?
                  Uses Retrieval Precision, Hit Rate, Reciprocal Rank.
                  Requires: input_text + context as list[str] of N docs.

  RAG generation — evaluates the *LLM's answer*: faithful + relevant?
                   Uses Answer Relevance, Context Relevance, Faithfulness.
                   Requires: input_text + generated_text + context (single string).

Default thresholds: LOW_IS_RISK with block=0.1, flag=0.3 — low scores are risky.

In production you'd run RAG retrieval AFTER vector search and BEFORE the LLM
call (so you can skip the LLM if HitRate=0), then RAG generation AFTER the
LLM responds. This tutorial demonstrates both stages on canned data.

Prerequisites
-------------
1. `pip install -e ./sdk[all]`
2. `cp ./sdk/.env.example ./.env` and fill in credentials
3. Run: `python 02_rag_quality_guardrails.py`
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv

from real_time_guardrails import GuardrailsEvaluator


load_dotenv()
ev = GuardrailsEvaluator()


# ── Stage 1: RAG retrieval — pass a LIST of retrieved docs ─────────────

RETRIEVAL_SCENARIOS = [
    {
        "id": "good_retrieval",
        "question": "How do I reset my password?",
        "docs": [
            "To reset your password, go to Settings > Security > Reset Password.",
            "Password complexity rules: 12+ chars, mixed case, symbol.",
            "Account lockout occurs after 5 failed login attempts.",
        ],
    },
    {
        "id": "irrelevant_retrieval",
        "question": "How do I reset my password?",
        "docs": [
            "Cats are popular household pets.",
            "Pizza was invented in Naples.",
            "Mountains are tall.",
        ],
    },
]


def check_retrieval(scenario: dict) -> None:
    bundle = ev.evaluate(
        input_text=scenario["question"],
        context=scenario["docs"],          # LIST = retrieval ranking
        categories=["rag_retrieval"],
    )
    print(f"  [{bundle.overall_action().upper()}] {scenario['id']} — Q={scenario['question']!r}")
    for name, r in bundle.results.items():
        score = f"{r.score:.3f}" if r.score is not None else "n/a"
        print(f"    {name}: score={score} action={r.action}")


# ── Stage 2: RAG generation — pass a SINGLE context string ─────────────

GENERATION_SCENARIOS = [
    {
        "id": "faithful_answer",
        "question": "What is the return policy?",
        "context": "Electronics: returns within 30 days with original receipt, 15% restocking fee on opened items.",
        "answer": "You can return electronics within 30 days with your receipt. Opened items have a 15% restocking fee.",
    },
    {
        "id": "hallucinated_answer",
        "question": "What is the return policy?",
        "context": "Electronics: returns within 30 days with original receipt.",
        "answer": "Electronics can be returned within 90 days with free shipping, lifetime warranty, and price matching against any competitor.",
    },
]


def check_generation(scenario: dict) -> None:
    bundle = ev.evaluate(
        input_text=scenario["question"],
        generated_text=scenario["answer"],
        context=scenario["context"],       # STRING = generation faithfulness
        categories=["rag_generation"],
    )
    print(f"  [{bundle.overall_action().upper()}] {scenario['id']} — Q={scenario['question']!r}")
    for name, r in bundle.results.items():
        score = f"{r.score:.3f}" if r.score is not None else "n/a"
        print(f"    {name}: score={score} action={r.action}")


def main() -> None:
    print("=" * 70)
    print("RAG RETRIEVAL QUALITY (after vector search, before LLM call)")
    print("=" * 70)
    for scenario in RETRIEVAL_SCENARIOS:
        print(f"\n─ Scenario: {scenario['id']}")
        check_retrieval(scenario)

    print("\n" + "=" * 70)
    print("RAG GENERATION QUALITY (after LLM call, before serving)")
    print("=" * 70)
    for scenario in GENERATION_SCENARIOS:
        print(f"\n─ Scenario: {scenario['id']}")
        check_generation(scenario)


if __name__ == "__main__":
    sys.exit(main())
