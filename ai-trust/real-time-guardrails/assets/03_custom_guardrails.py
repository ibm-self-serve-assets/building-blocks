"""
Custom LLM-as-Judge Guardrails with IBM watsonx governance

Define custom guardrail metrics using LLM-as-judge — an LLM evaluates
AI responses against custom criteria you define. This enables guardrails
beyond built-in safety metrics:

  - Answer Completeness: Does the response address all parts of the question?
  - Conciseness:         Is the response brief and direct?
  - Helpfulness:         Is the response accurate, useful, and actionable?

Uses LLMAsJudgeMetric with WxAIFoundationModel as the judge.

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"
  export WXG_PROJECT_ID="your-watsonx-governance-project-id"

Usage:
  python 03_custom_guardrails.py
"""

import os
import sys

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("WATSONX_APIKEY"):
    print("ERROR: WATSONX_APIKEY environment variable is not set.")
    sys.exit(1)

if not os.environ.get("WXG_PROJECT_ID"):
    print("ERROR: WXG_PROJECT_ID environment variable is not set.")
    print("  This is required for LLM-as-judge metrics.")
    sys.exit(1)

from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.entities.criteria import Option
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.metrics import LLMAsJudgeMetric


# ── Set up LLM judge ─────────────────────────────────────────────────
PROJECT_ID = os.environ["WXG_PROJECT_ID"]
llm_judge = LLMJudge(
    model=WxAIFoundationModel(
        model_id="llama-3-3-70b-instruct",
        project_id=PROJECT_ID,
    )
)


# ── Define custom guardrail metrics ──────────────────────────────────

# 1. Answer Completeness — uses a detailed prompt template
completeness_prompt = """You are an expert grader. Evaluate the completeness of an AI-generated response.

**Question:**
{input_text}

**AI-Generated Response:**
{generated_text}

Rate the response completeness:

complete - The response thoroughly addresses all parts of the question.
partial - The response addresses some parts but is missing key information.
incomplete - The response fails to address the question or ends unexpectedly.
"""

answer_completeness = LLMAsJudgeMetric(
    name="answer_completeness",
    display_name="Answer Completeness",
    prompt_template=completeness_prompt,
    options={"complete": 1, "partial": 0.5, "incomplete": 0},
    llm_judge=llm_judge,
)

# 2. Conciseness — uses criteria_description + Option objects
conciseness = LLMAsJudgeMetric(
    name="conciseness",
    display_name="Conciseness",
    criteria_description="Is the {generated_text} concise and to the point?",
    options=[
        Option(
            name="Yes",
            description="The response is short, succinct and directly addresses the point.",
            value=1,
        ),
        Option(
            name="No",
            description="The response lacks brevity and clarity.",
            value=0,
        ),
    ],
    output_field="generated_text",
    llm_judge=llm_judge,
)

# 3. Helpfulness — multi-level scoring
helpfulness = LLMAsJudgeMetric(
    name="helpfulness",
    display_name="Helpfulness",
    criteria_description=(
        "How helpful is the {generated_text}? Consider whether it provides "
        "accurate, useful, and actionable information."
    ),
    options=[
        Option(
            name="High",
            description="Very helpful: accurate, actionable, and directly addresses needs.",
            value=1,
        ),
        Option(
            name="Medium",
            description="Somewhat helpful: partially addresses needs but lacks depth.",
            value=0.5,
        ),
        Option(
            name="Low",
            description="Not helpful: vague, inaccurate, or fails to provide assistance.",
            value=0,
        ),
    ],
    output_field="generated_text",
    llm_judge=llm_judge,
)


# ── Quality thresholds for custom guardrails ──────────────────────────
CUSTOM_THRESHOLDS = {
    "answer_completeness": 0.5,
    "conciseness": 0.5,
    "helpfulness": 0.5,
}


# ── Test data ─────────────────────────────────────────────────────────
CUSTOM_GUARDRAIL_RECORDS = [
    {
        "input_text": "What are the three steps to reset my password?",
        "generated_text": (
            "To reset your password: 1) Go to the login page and click 'Forgot Password', "
            "2) Enter your registered email address, 3) Check your email for the reset link "
            "and create a new password."
        ),
    },
    {
        "input_text": "What are the three steps to reset my password?",
        "generated_text": (
            "Password security is a very important topic in today's digital landscape. "
            "There are many considerations when it comes to managing your credentials "
            "across different platforms and services. You might want to consider using "
            "a password manager to help keep track of your various accounts. Additionally, "
            "it's worth noting that strong passwords typically include a mix of uppercase "
            "and lowercase letters, numbers, and special characters."
        ),
    },
    {
        "input_text": "How do I cancel my subscription?",
        "generated_text": (
            "Go to Settings > Subscriptions > Click 'Cancel'. "
            "Your access continues until the end of the billing period."
        ),
    },
]


def evaluate_custom_guardrails(records: list[dict]) -> None:
    """Run custom LLM-as-judge guardrails on a set of records."""
    config = GenAIConfiguration(
        input_fields=["input_text"],
        output_fields=["generated_text"],
    )

    custom_metrics = [answer_completeness, conciseness, helpfulness]

    evaluator = MetricsEvaluator(configuration=config)
    df = pd.DataFrame(records)
    result = evaluator.evaluate(data=df, metrics=custom_metrics)

    print("\n" + "=" * 60)
    print("CUSTOM LLM-AS-JUDGE GUARDRAIL RESULTS")
    print("=" * 60)

    # Aggregate scores
    for metric in result.metrics_result:
        threshold = CUSTOM_THRESHOLDS.get(metric.name, 0.5)
        status = "PASS" if metric.mean >= threshold else "FAIL"
        print(f"\n  {metric.name}:")
        print(f"    Mean: {metric.mean:.3f} [{status}] (threshold: {threshold})")

    # Per-record details
    print("\n" + "-" * 60)
    print("Per-Record Results:")
    print("-" * 60)
    for i, record in enumerate(result.to_dict()):
        question = records[i]["input_text"]
        answer_preview = records[i]["generated_text"][:60] + "..."
        print(f"\n  Record {i + 1}:")
        print(f"    Q: \"{question}\"")
        print(f"    A: \"{answer_preview}\"")

        all_pass = True
        for key, value in record.items():
            if value is not None:
                threshold = CUSTOM_THRESHOLDS.get(key, 0.5)
                status = "PASS" if value >= threshold else "FAIL"
                if status == "FAIL":
                    all_pass = False
                print(f"    {key}: {value:.3f} [{status}]")

        action = "PASS" if all_pass else "FLAG"
        print(f"    → Action: [{action}]")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Custom LLM-as-Judge Guardrails")
    print(f"Evaluating {len(CUSTOM_GUARDRAIL_RECORDS)} records...\n")
    evaluate_custom_guardrails(CUSTOM_GUARDRAIL_RECORDS)
