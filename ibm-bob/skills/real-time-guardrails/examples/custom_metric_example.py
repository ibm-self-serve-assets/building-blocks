"""Reference: authoring custom LLM-as-judge metrics.

Two styles, side by side:

  STYLE A — prompt_template (full prompt control)
  STYLE B — criteria_description + Option (SDK builds the prompt)

Plus: how to register the custom metric in the evaluator's MetricRegistry
so `ev.evaluate(metrics=["My Metric Name"])` can find it.

Run::

    cd <your project root>
    set -a && source .env && set +a
    python custom_metric_example.py
"""

from __future__ import annotations

from ibm_watsonx_gov.entities.criteria import Option
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.metrics import LLMAsJudgeMetric

from real_time_guardrails import GuardrailsConfig, GuardrailsEvaluator
from real_time_guardrails.core.custom_metrics import build_criteria_judge
from real_time_guardrails.core.registry import MetricEntry
from real_time_guardrails.core.thresholds import Direction, ThresholdSpec


# ----- Build a shared LLMJudge from env config -----

cfg = GuardrailsConfig.from_env()
if not cfg.project_id:
    raise SystemExit("WXG_PROJECT_ID is required for LLM-as-judge metrics. Set it in .env.")
judge = LLMJudge(
    model=WxAIFoundationModel(model_id=cfg.judge_model_id, project_id=cfg.project_id)
)


# =====================================================================
# STYLE A — prompt_template: you write the full prompt
# =====================================================================
#
# Use when: you need to inject examples, multi-turn context, or careful
# instruction shaping. Trade-off: prompt becomes a long string you maintain.

contract_clause_metric = LLMAsJudgeMetric(
    name="contract_clause_correctness",
    llm_judge=judge,
    prompt_template=(
        "You are evaluating whether an AI response correctly cites the relevant "
        "contract clause.\n\n"
        "Question: {input_text}\n"
        "AI Response: {generated_text}\n"
        "Reference Contract: {context}\n\n"
        "Return one of: correct / partially_correct / incorrect"
    ),
    input_fields=["input_text", "generated_text", "context"],
    options={"correct": 1.0, "partially_correct": 0.5, "incorrect": 0.0},
)


# =====================================================================
# STYLE B — criteria_description + Option: SDK builds the prompt
# =====================================================================
#
# Use when: judgment is a short rubric (Yes/No or 3-tier). Less code,
# easier maintenance.

brand_voice_metric = build_criteria_judge(
    name="brand_voice",
    display_name="Brand Voice",
    criteria_description=(
        "Does the {generated_text} match our brand voice "
        "(professional, concise, warm)?"
    ),
    options=[
        Option(name="Yes", description="On-brand: professional, concise, warm.", value=1.0),
        Option(name="No", description="Off-brand.", value=0.0),
    ],
    judge=judge,
)


# =====================================================================
# REGISTRATION — add the custom metric to the evaluator's registry
# =====================================================================
#
# Without registration, `ev.evaluate(metrics=["..."])` raises
# UnknownMetricError. Add a MetricEntry post-construction.

def register_custom_metrics(ev: GuardrailsEvaluator) -> None:
    """Append our two custom metrics to the evaluator's registry."""
    entries = [
        MetricEntry(
            name="Contract Clause Correctness",
            metric=contract_clause_metric,
            category="quality",
            column_name="contract_clause_correctness",
            threshold_spec=ThresholdSpec(
                value=0.5, direction=Direction.LOW_IS_RISK, flag_value=0.75
            ),
            required_fields=frozenset({"input_text", "generated_text", "context"}),
            description="Whether the response correctly cites the relevant clause.",
        ),
        MetricEntry(
            name="Brand Voice",
            metric=brand_voice_metric,
            category="quality",
            column_name="brand_voice",
            threshold_spec=ThresholdSpec(
                value=0.5, direction=Direction.LOW_IS_RISK, flag_value=None
            ),
            required_fields=frozenset({"generated_text"}),
            description="On-brand vs off-brand response check (Yes/No rubric).",
        ),
    ]
    for entry in entries:
        ev.registry._by_name[entry.name] = entry
    # Re-bind the threshold resolver's known-metric set so threshold
    # overrides + warnings work correctly for the new metrics.
    ev._threshold_resolver.attach_known_metrics(set(ev.registry.names))


# =====================================================================
# Demo
# =====================================================================

def main() -> None:
    ev = GuardrailsEvaluator()
    register_custom_metrics(ev)
    print(f"registry size: {len(ev.registry)} metrics (28 catalog + 2 custom)")

    print("\n--- Brand Voice (criteria style) ---")
    bundle = ev.evaluate(
        generated_text=(
            "Hey there! Just letting you know — your order shipped! 🎉 Thanks "
            "for being awesome!"
        ),
        metrics=["Brand Voice"],
    )
    r = bundle["Brand Voice"]
    print(f"  score={r.score} action={r.action} threshold={r.threshold}")

    print("\n--- Contract Clause Correctness (prompt_template style) ---")
    bundle = ev.evaluate(
        input_text="Can I terminate my contract early?",
        generated_text="Yes, per Section 7.2 you may terminate with 30 days' notice.",
        context="Section 7.2: Either party may terminate this agreement upon thirty (30) days' written notice.",
        metrics=["Contract Clause Correctness"],
    )
    r = bundle["Contract Clause Correctness"]
    print(f"  score={r.score} action={r.action} threshold={r.threshold}")


if __name__ == "__main__":
    main()
