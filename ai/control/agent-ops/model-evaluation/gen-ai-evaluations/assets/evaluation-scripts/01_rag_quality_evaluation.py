"""
RAG Quality Evaluation with IBM watsonx governance

Evaluates a Retrieval-Augmented Generation (RAG) pipeline for quality metrics:
  - Answer Relevance:     Does the answer address the question?
  - Faithfulness:         Is the answer grounded in the provided context?
  - Context Relevance:    Is the retrieved context relevant to the question?
  - Answer Similarity:    How similar is the answer to a reference/ground-truth?
  - Retrieval Precision:  What fraction of retrieved chunks are relevant?
  - NDCG:                 Ranking quality of retrieved results

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"
  export WATSONX_REGION="us-south"

Usage:
  python 01_rag_quality_evaluation.py
"""

import os
import sys

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ── Validate credentials ──────────────────────────────────────────────
if not os.environ.get("WATSONX_APIKEY"):
    print("ERROR: WATSONX_APIKEY environment variable is not set.")
    print("  export WATSONX_APIKEY='your-ibm-cloud-api-key'")
    sys.exit(1)

# ── Import watsonx governance SDK ─────────────────────────────────────
from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.metrics import (
    AnswerRelevanceMetric,
    AnswerSimilarityMetric,
    ContextRelevanceMetric,
    FaithfulnessMetric,
    RetrievalPrecisionMetric,
    NDCGMetric,
)


def evaluate_rag_quality(data: pd.DataFrame) -> dict:
    """Evaluate RAG quality across multiple metrics.

    Args:
        data: DataFrame with columns: question, context, generated_text, reference

    Returns:
        dict with per-metric aggregate scores and per-record details
    """
    config = GenAIConfiguration(
        input_fields=["question"],
        context_fields=["context"],
        output_fields=["generated_text"],
        reference_fields=["reference"],
    )

    metrics = [
        AnswerRelevanceMetric(),
        FaithfulnessMetric(),
        ContextRelevanceMetric(),
        AnswerSimilarityMetric(),
        RetrievalPrecisionMetric(),
        NDCGMetric(),
    ]

    evaluator = MetricsEvaluator(configuration=config)
    result = evaluator.evaluate(data=data, metrics=metrics)

    return result


def print_results(result) -> None:
    """Print evaluation results in a readable format."""
    print("\n" + "=" * 60)
    print("RAG QUALITY EVALUATION RESULTS")
    print("=" * 60)

    for metric in result.metrics_result:
        print(f"\n  {metric.name}:")
        print(f"    Mean:  {metric.mean:.4f}")
        print(f"    Min:   {metric.min:.4f}")
        print(f"    Max:   {metric.max:.4f}")
        print(f"    Count: {metric.total_records}")

    print("\n" + "-" * 60)
    print("Per-Record Scores:")
    print("-" * 60)
    for i, record in enumerate(result.to_dict()):
        print(f"\n  Record {i + 1}:")
        for key, value in record.items():
            if value is not None:
                print(f"    {key}: {value}")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load sample data
    data = pd.read_csv("sample_data/rag_test_data.csv")
    print(f"Loaded {len(data)} records from sample_data/rag_test_data.csv")

    # Run evaluation
    result = evaluate_rag_quality(data)
    print_results(result)
