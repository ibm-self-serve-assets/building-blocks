"""Both LLM-as-judge styles, side by side.

The IBM gov SDK accepts two ways to define a custom LLM-as-judge metric:

  STYLE A — prompt_template
      You write the full LLM prompt. Most control, most verbose.

  STYLE B — criteria_description + Option list
      You write a short rubric + named options. The SDK builds the prompt.
      Less control, less verbose, well-suited to simple Yes/No or
      High/Medium/Low judges.

Pick whichever feels right for your use case. This example builds one of
each style and runs them on the same scoring task so you can compare.

Run::

    set -a && source .env && set +a
    python examples/library_custom_judge.py
"""

from __future__ import annotations

import pandas as pd
from ibm_watsonx_gov.entities.criteria import Option

from real_time_guardrails import GuardrailsConfig
from real_time_guardrails.core.custom_metrics import (
    build_answer_completeness,
    build_criteria_judge,
)


def build_judge_from_env() -> object:
    """Build the shared LLMJudge instance from env vars."""
    cfg = GuardrailsConfig.from_env()
    if not cfg.project_id:
        raise SystemExit(
            "WXG_PROJECT_ID is required for LLM-as-judge metrics — set it in .env first."
        )
    from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
    from ibm_watsonx_gov.entities.llm_judge import LLMJudge

    return LLMJudge(
        model=WxAIFoundationModel(model_id=cfg.judge_model_id, project_id=cfg.project_id)
    )


def main() -> None:
    judge = build_judge_from_env()

    # Style A — prompt_template (ported from ai-trust/assets/03_custom_guardrails.py)
    completeness_metric = build_answer_completeness(judge)

    # Style B — criteria + Option (the new helper)
    helpfulness_metric = build_criteria_judge(
        name="helpfulness",
        display_name="Helpfulness",
        criteria_description=(
            "How helpful is the {generated_text}? Consider accuracy, "
            "actionability, and directness."
        ),
        options=[
            Option(
                name="High",
                description="Accurate, actionable, directly addresses the user's need.",
                value=1.0,
            ),
            Option(
                name="Medium",
                description="Partially helpful — lacks depth or has gaps.",
                value=0.5,
            ),
            Option(
                name="Low",
                description="Vague, inaccurate, or unhelpful.",
                value=0.0,
            ),
        ],
        judge=judge,
    )

    # Run both on the same data
    from ibm_watsonx_gov.evaluators import MetricsEvaluator
    from ibm_watsonx_gov.config import GenAIConfiguration

    config = GenAIConfiguration(
        input_fields=["input_text"],
        output_fields=["generated_text"],
    )
    ev = MetricsEvaluator(configuration=config)

    records = [
        {
            "input_text": "How do I reset my password?",
            "generated_text": (
                "Go to Settings > Security > Reset Password. Enter current password, "
                "then choose a new one meeting the complexity rules."
            ),
        },
        {
            "input_text": "How do I reset my password?",
            "generated_text": (
                "Passwords are very important. There are many ways to think about "
                "passwords. Some people use password managers."
            ),
        },
    ]
    df = pd.DataFrame(records)

    print("=" * 70)
    print("STYLE A — prompt_template (Answer Completeness)")
    print("=" * 70)
    result_a = ev.evaluate(data=df, metrics=[completeness_metric])
    print(result_a.to_df().to_string())

    print("\n" + "=" * 70)
    print("STYLE B — criteria + Option (Helpfulness)")
    print("=" * 70)
    result_b = ev.evaluate(data=df, metrics=[helpfulness_metric])
    print(result_b.to_df().to_string())

    print(
        "\nNote: both styles produce a numeric score per record. The styles "
        "differ in how you author the metric, not in what it returns."
    )


if __name__ == "__main__":
    main()
