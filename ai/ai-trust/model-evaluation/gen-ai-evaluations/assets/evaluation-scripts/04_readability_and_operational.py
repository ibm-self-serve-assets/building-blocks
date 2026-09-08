"""
Readability & Operational Metrics with IBM watsonx governance

Evaluates the readability and operational characteristics of AI outputs:

  Readability:
  - Text Grade Level:  US school grade level needed to understand the text
  - Text Reading Ease: Flesch Reading Ease score (0-100, higher = easier)

  Operational:
  - Cost:              Token cost per record
  - Duration:          Response latency
  - Input Token Count: Number of input tokens
  - Output Token Count: Number of output tokens

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"

Usage:
  python 04_readability_and_operational.py
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
    TextGradeLevelMetric,
    TextReadingEaseMetric,
)


# ── Sample data ───────────────────────────────────────────────────────
READABILITY_RECORDS = [
    {
        "generated_text": (
            "AI governance is important. It helps keep AI safe. "
            "Companies need to check their AI models. This makes sure "
            "the models work well and are fair to everyone."
        ),
    },
    {
        "generated_text": (
            "The implementation of comprehensive AI governance frameworks "
            "necessitates a multifaceted approach encompassing algorithmic "
            "auditing, bias mitigation strategies, and regulatory compliance "
            "mechanisms to ensure the responsible deployment of artificial "
            "intelligence systems across heterogeneous enterprise environments."
        ),
    },
    {
        "generated_text": (
            "To set up model monitoring, go to the watsonx governance dashboard. "
            "Click on your model deployment. Choose the metrics you want to track. "
            "Set your alert thresholds. The system will notify you when metrics "
            "fall outside acceptable ranges."
        ),
    },
]


def evaluate_readability(records: list[dict]) -> None:
    """Evaluate the readability of generated text."""
    config = GenAIConfiguration(
        output_fields=["generated_text"],
    )

    metrics = [
        TextGradeLevelMetric(),
        TextReadingEaseMetric(),
    ]

    evaluator = MetricsEvaluator(configuration=config)
    df = pd.DataFrame(records)
    result = evaluator.evaluate(data=df, metrics=metrics)

    print("\n" + "=" * 60)
    print("READABILITY EVALUATION RESULTS")
    print("=" * 60)

    for metric in result.metrics_result:
        print(f"\n  {metric.name}:")
        print(f"    Mean:  {metric.mean:.2f}")
        print(f"    Min:   {metric.min:.2f}")
        print(f"    Max:   {metric.max:.2f}")

    print("\n" + "-" * 60)
    print("Per-Record Readability:")
    print("-" * 60)

    reading_ease_guide = {
        (90, 100): "Very Easy (5th grade)",
        (80, 89): "Easy (6th grade)",
        (70, 79): "Fairly Easy (7th grade)",
        (60, 69): "Standard (8th-9th grade)",
        (50, 59): "Fairly Difficult (10th-12th grade)",
        (30, 49): "Difficult (College)",
        (0, 29): "Very Difficult (Graduate)",
    }

    for i, record in enumerate(result.to_dict()):
        text_preview = records[i]["generated_text"][:80] + "..."
        print(f"\n  Record {i + 1}: \"{text_preview}\"")
        for key, value in record.items():
            if value is not None:
                label = ""
                if "reading_ease" in key:
                    for (low, high), desc in reading_ease_guide.items():
                        if low <= value <= high:
                            label = f"  ({desc})"
                            break
                print(f"    {key}: {value:.2f}{label}")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Evaluating {len(READABILITY_RECORDS)} records for readability...\n")
    evaluate_readability(READABILITY_RECORDS)

    print("\n\nReadability Scale Reference:")
    print("  90-100: Very Easy (5th grade)")
    print("  80-89:  Easy (6th grade)")
    print("  70-79:  Fairly Easy (7th grade)")
    print("  60-69:  Standard (8th-9th grade)")
    print("  50-59:  Fairly Difficult (10th-12th grade)")
    print("  30-49:  Difficult (College)")
    print("  0-29:   Very Difficult (Graduate)")
