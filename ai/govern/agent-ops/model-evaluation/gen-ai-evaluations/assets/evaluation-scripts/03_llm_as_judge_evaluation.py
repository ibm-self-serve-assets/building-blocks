"""
LLM-as-Judge Quality Evaluation with IBM watsonx governance

Uses an LLM to judge the quality of AI-generated outputs — more nuanced
than token-level metrics. Also includes evasiveness and topic relevance
detection.

Metrics demonstrated:
  - LLM-as-Judge:     Nuanced quality scoring using an LLM evaluator
  - Evasiveness:      Is the model avoiding or dodging the question?
  - Topic Relevance:  Is the response on-topic for the question asked?

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"

Usage:
  python 03_llm_as_judge_evaluation.py
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
    EvasivenessMetric,
    TopicRelevanceMetric,
)


# ── Sample data ───────────────────────────────────────────────────────
QUALITY_TEST_RECORDS = [
    {
        "question": "What are the benefits of using RAG in enterprise applications?",
        "generated_text": (
            "RAG brings several key benefits to enterprise applications: "
            "1) Reduced hallucinations by grounding responses in verified documents, "
            "2) Access to up-to-date information without retraining, "
            "3) Better attribution and traceability of answers, "
            "4) Domain-specific accuracy by connecting to internal knowledge bases."
        ),
        "context": (
            "Retrieval-Augmented Generation (RAG) enhances AI applications by combining "
            "retrieval from knowledge bases with generation. Benefits include reduced "
            "hallucinations, access to current information, and domain-specific accuracy."
        ),
    },
    {
        "question": "How do I configure fairness monitoring in watsonx governance?",
        "generated_text": (
            "That's an interesting question. There are many aspects to consider "
            "when thinking about AI governance. I'd recommend looking into the "
            "documentation for more details on various features."
        ),
        "context": (
            "To configure fairness monitoring, navigate to the Evaluations tab in "
            "watsonx governance. Select your model deployment, choose the fairness "
            "metrics you want to track, set the protected attributes and reference "
            "groups, then configure alert thresholds."
        ),
    },
    {
        "question": "What is the capital of France?",
        "generated_text": (
            "Machine learning models can be trained using various techniques including "
            "supervised learning, unsupervised learning, and reinforcement learning. "
            "Each approach has its own strengths depending on the problem at hand."
        ),
        "context": (
            "France is a country in Western Europe. Its capital city is Paris, "
            "which is also the country's largest city and its main cultural and "
            "commercial center."
        ),
    },
]


def evaluate_evasiveness_and_relevance(records: list[dict]) -> None:
    """Detect evasive responses and off-topic answers."""
    config = GenAIConfiguration(
        input_fields=["question"],
        output_fields=["generated_text"],
        context_fields=["context"],
    )

    metrics = [
        EvasivenessMetric(),
        TopicRelevanceMetric(),
    ]

    evaluator = MetricsEvaluator(configuration=config)
    df = pd.DataFrame(records)
    result = evaluator.evaluate(data=df, metrics=metrics)

    print("\n" + "=" * 60)
    print("EVASIVENESS & TOPIC RELEVANCE RESULTS")
    print("=" * 60)

    for metric in result.metrics_result:
        print(f"\n  {metric.name}:")
        print(f"    Mean:  {metric.mean:.4f}")
        print(f"    Min:   {metric.min:.4f}")
        print(f"    Max:   {metric.max:.4f}")

    print("\n" + "-" * 60)
    print("Per-Record Analysis:")
    print("-" * 60)
    for i, record in enumerate(result.to_dict()):
        question = records[i]["question"]
        answer_preview = records[i]["generated_text"][:80] + "..."
        print(f"\n  Record {i + 1}:")
        print(f"    Question: \"{question}\"")
        print(f"    Answer:   \"{answer_preview}\"")
        for key, value in record.items():
            if value is not None:
                print(f"    {key}: {value}")


def evaluate_with_topic_prompt(records: list[dict], system_prompt: str) -> None:
    """Evaluate topic relevance against a specific system prompt context.

    This is useful when you want to check if responses stay within the
    boundaries defined by the system prompt (e.g., a customer service bot
    should only answer questions about products).
    """
    config = GenAIConfiguration(
        input_fields=["question"],
        output_fields=["generated_text"],
    )

    metrics = [TopicRelevanceMetric(system_prompt=system_prompt)]

    evaluator = MetricsEvaluator(configuration=config)
    df = pd.DataFrame(records)
    result = evaluator.evaluate(data=df, metrics=metrics)

    print("\n" + "=" * 60)
    print("TOPIC RELEVANCE WITH SYSTEM PROMPT")
    print("=" * 60)
    print(f"  System prompt: \"{system_prompt[:80]}...\"")

    for metric in result.metrics_result:
        print(f"\n  {metric.name}:")
        print(f"    Mean:  {metric.mean:.4f}")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Evaluating {len(QUALITY_TEST_RECORDS)} records for quality...\n")

    # Run evasiveness and topic relevance
    evaluate_evasiveness_and_relevance(QUALITY_TEST_RECORDS)

    # Run topic relevance with a system prompt boundary
    system_prompt = (
        "You are a helpful AI assistant specializing in IBM watsonx governance "
        "and AI trust. Only answer questions related to AI governance, model "
        "evaluation, safety, and compliance."
    )
    evaluate_with_topic_prompt(QUALITY_TEST_RECORDS, system_prompt)
