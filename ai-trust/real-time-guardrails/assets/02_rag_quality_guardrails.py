"""
RAG Quality Guardrails with IBM watsonx governance

Real-time quality checks on RAG pipeline responses before returning
them to the user. Ensures generated answers are:
  - Faithful to the retrieved context (not hallucinated)
  - Relevant to the user's question
  - Based on relevant context

If quality is below threshold, the response is blocked or flagged
and the user receives a fallback message.

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"

Usage:
  python 02_rag_quality_guardrails.py
"""

import os
import sys

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("WATSONX_APIKEY"):
    print("ERROR: WATSONX_APIKEY environment variable is not set.")
    sys.exit(1)

from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.metrics import (
    AnswerRelevanceMetric,
    ContextRelevanceMetric,
    FaithfulnessMetric,
)


# ── Quality thresholds ────────────────────────────────────────────────
QUALITY_THRESHOLDS = {
    "answer_relevance":  0.7,
    "faithfulness":      0.7,
    "context_relevance": 0.6,
}

FALLBACK_MESSAGE = (
    "I'm not confident in my answer based on the available information. "
    "Let me connect you with a specialist who can help."
)


# ── Test scenarios ────────────────────────────────────────────────────
RAG_RESPONSES = [
    {
        "id": "grounded_response",
        "question": "What is the return policy for electronics?",
        "context": (
            "Our return policy for electronics allows returns within 30 days of "
            "purchase with original receipt. Items must be in original packaging "
            "and in working condition. A 15% restocking fee applies to opened items."
        ),
        "generated_text": (
            "You can return electronics within 30 days with your original receipt. "
            "The item needs to be in its original packaging and working condition. "
            "Note that there's a 15% restocking fee for opened items."
        ),
    },
    {
        "id": "hallucinated_response",
        "question": "What is the return policy for electronics?",
        "context": (
            "Our return policy for electronics allows returns within 30 days of "
            "purchase with original receipt."
        ),
        "generated_text": (
            "Electronics can be returned within 90 days with a full refund and "
            "free return shipping. We also offer a lifetime warranty on all "
            "electronic purchases and price matching against any competitor."
        ),
    },
    {
        "id": "irrelevant_context",
        "question": "How do I set up two-factor authentication?",
        "context": (
            "Our catering menu includes a variety of sandwiches, salads, and "
            "beverages. We offer group discounts for orders over 20 people. "
            "Delivery is available within a 10-mile radius."
        ),
        "generated_text": (
            "Based on the available information, two-factor authentication "
            "can be set up by going to your account settings. However, I "
            "should note that I don't have specific documentation about this."
        ),
    },
]


def check_rag_quality(record: dict) -> dict:
    """Evaluate a single RAG response against quality thresholds.

    Returns:
        dict with action (PASS/BLOCK), metric scores, and the response to serve.
    """
    config = GenAIConfiguration(
        input_fields=["question"],
        context_fields=["context"],
        output_fields=["generated_text"],
    )

    metrics = [
        AnswerRelevanceMetric(),
        FaithfulnessMetric(),
        ContextRelevanceMetric(),
    ]

    evaluator = MetricsEvaluator(configuration=config)
    df = pd.DataFrame([record])
    result = evaluator.evaluate(data=df, metrics=metrics)

    # result.metrics_result contains AggregateMetricResult objects.
    # For a single-record DataFrame, .mean equals the single record's score.
    scores = {}
    failed_metrics = []

    for metric in result.metrics_result:
        score = metric.mean
        scores[metric.name] = score
        threshold = QUALITY_THRESHOLDS.get(metric.name, 0.5)
        if score < threshold:
            failed_metrics.append(f"{metric.name}: {score:.3f} < {threshold}")

    if failed_metrics:
        return {
            "action": "BLOCK",
            "scores": scores,
            "failed_metrics": failed_metrics,
            "response": FALLBACK_MESSAGE,
        }
    else:
        return {
            "action": "PASS",
            "scores": scores,
            "failed_metrics": [],
            "response": record["generated_text"],
        }


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("RAG QUALITY GUARDRAILS")
    print("=" * 60)
    print("\nQuality thresholds:")
    for metric, threshold in QUALITY_THRESHOLDS.items():
        print(f"  {metric}: >= {threshold}")

    for record in RAG_RESPONSES:
        print(f"\n{'─' * 60}")
        print(f"Scenario: {record['id']}")
        print(f"Question: \"{record['question']}\"")

        result = check_rag_quality(record)

        print(f"\n  Action: [{result['action']}]")
        print(f"  Scores:")
        for metric, score in result["scores"].items():
            threshold = QUALITY_THRESHOLDS.get(metric, 0.5)
            status = "PASS" if score >= threshold else "FAIL"
            print(f"    {metric}: {score:.3f} [{status}]")

        if result["failed_metrics"]:
            print(f"  Failed checks:")
            for fail in result["failed_metrics"]:
                print(f"    - {fail}")

        print(f"  Response served: \"{result['response'][:80]}...\"")
