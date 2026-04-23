"""
Content Safety Guardrails with IBM watsonx governance

Real-time detection and enforcement of safety boundaries on AI inputs
and outputs. Demonstrates configurable threshold-based actions:
  - BLOCK: Reject the content entirely
  - FLAG:  Allow but mark for human review
  - PASS:  Content is within acceptable limits

Safety metrics applied:
  - HAP (Hate, Abuse, Profanity)
  - PII (Personally Identifiable Information)
  - Jailbreak (prompt injection detection)
  - Social Bias
  - Violence
  - Profanity

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"

Usage:
  python 01_content_safety_guardrails.py
"""

import json
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
    HAPMetric,
    PIIMetric,
    JailbreakMetric,
    SocialBiasMetric,
    ViolenceMetric,
    ProfanityMetric,
)


# ── Guardrail configuration ──────────────────────────────────────────
# Define thresholds for each safety metric.
# Scores above BLOCK threshold → content is rejected.
# Scores above FLAG threshold → content is flagged for review.
# Scores below FLAG threshold → content passes.

GUARDRAIL_POLICY = {
    "hap":         {"block": 0.8, "flag": 0.5},
    "pii":         {"block": 0.5, "flag": 0.3},
    "jailbreak":   {"block": 0.7, "flag": 0.4},
    "social_bias": {"block": 0.7, "flag": 0.4},
    "violence":    {"block": 0.7, "flag": 0.4},
    "profanity":   {"block": 0.8, "flag": 0.5},
}


def apply_guardrails(text: str, direction: str = "input") -> dict:
    """Apply safety guardrails to a piece of text.

    Args:
        text: The text to evaluate (user input or model output).
        direction: "input" for user queries, "output" for model responses.

    Returns:
        dict with action (PASS/FLAG/BLOCK), scores, and triggered rules.
    """
    if direction == "input":
        data = {"input_text": text, "generated_text": ""}
        config = GenAIConfiguration(input_fields=["input_text"], output_fields=["generated_text"])
    else:
        data = {"input_text": "", "generated_text": text}
        config = GenAIConfiguration(input_fields=["input_text"], output_fields=["generated_text"])

    metrics = [
        HAPMetric(),
        PIIMetric(),
        JailbreakMetric(),
        SocialBiasMetric(),
        ViolenceMetric(),
        ProfanityMetric(),
    ]

    evaluator = MetricsEvaluator(configuration=config)
    df = pd.DataFrame([data])
    result = evaluator.evaluate(data=df, metrics=metrics)

    # Collect scores and determine action.
    # result.metrics_result contains AggregateMetricResult objects.
    # For a single-record DataFrame, .mean equals the single record's score.
    scores = {}
    triggered_rules = []
    action = "PASS"

    for metric in result.metrics_result:
        score = metric.mean
        scores[metric.name] = score

        policy = GUARDRAIL_POLICY.get(metric.name, {})
        if score >= policy.get("block", 1.0):
            action = "BLOCK"
            triggered_rules.append(f"{metric.name}: {score:.3f} >= {policy['block']} (BLOCK)")
        elif score >= policy.get("flag", 1.0):
            if action != "BLOCK":
                action = "FLAG"
            triggered_rules.append(f"{metric.name}: {score:.3f} >= {policy['flag']} (FLAG)")

    return {
        "direction": direction,
        "action": action,
        "scores": scores,
        "triggered_rules": triggered_rules,
    }


def print_guardrail_result(text: str, result: dict) -> None:
    """Print guardrail evaluation result."""
    action_symbols = {"PASS": "PASS", "FLAG": "FLAG", "BLOCK": "BLOCK"}
    symbol = action_symbols[result["action"]]

    print(f"\n  [{symbol}] Direction: {result['direction']}")
    print(f"  Text: \"{text[:80]}...\"" if len(text) > 80 else f"  Text: \"{text}\"")

    if result["triggered_rules"]:
        print("  Triggered rules:")
        for rule in result["triggered_rules"]:
            print(f"    - {rule}")
    else:
        print("  All safety checks passed.")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load test scenarios
    with open("sample_data/guardrail_test_scenarios.json") as f:
        scenarios = json.load(f)

    print("=" * 60)
    print("CONTENT SAFETY GUARDRAILS")
    print("=" * 60)
    print(f"\nPolicy thresholds:")
    for metric, thresholds in GUARDRAIL_POLICY.items():
        print(f"  {metric}: block >= {thresholds['block']}, flag >= {thresholds['flag']}")

    print(f"\nEvaluating {len(scenarios)} scenarios...")

    for scenario in scenarios:
        print(f"\n{'─' * 60}")
        print(f"Scenario: {scenario['description']}")

        # Check input
        input_result = apply_guardrails(scenario["input_text"], direction="input")
        print_guardrail_result(scenario["input_text"], input_result)

        # Check output (only if input wasn't blocked)
        if input_result["action"] != "BLOCK":
            output_result = apply_guardrails(scenario["generated_text"], direction="output")
            print_guardrail_result(scenario["generated_text"], output_result)
        else:
            print("  Output evaluation skipped — input was blocked.")
