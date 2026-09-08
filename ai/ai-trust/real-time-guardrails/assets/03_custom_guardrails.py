"""Tutorial 03: Custom LLM-as-Judge Guardrails with real-time-guardrails

The SDK ships 3 LLM-as-judge metrics out of the box (Answer Completeness,
Conciseness, Tool Call Relevance). Their prompts are OPINIONATED DEFAULTS —
we wrote them with reasonable defaults but you may want different rubrics
for your domain (e.g. strict compliance, brand voice, multi-language).

This tutorial shows two ways to author your own LLM-as-judge metric:

  A. criteria_description + Option  — short rubric (Yes/No, High/Medium/Low).
                                       The SDK builds the prompt for you.
                                       Helper: build_criteria_judge()

  B. prompt_template                — full control over the LLM prompt.
                                       Use when you need examples or careful
                                       instruction shaping.
                                       Helper: LLMAsJudgeMetric() directly

You can also use this pattern to REPLACE one of the 3 built-in LLM-judge
metrics — see the "Replacing built-in LLM-judge prompts" section in the
bob mode's 6_custom_metric_authoring.xml.

Both styles produce a numeric score 0.0–1.0. You register the metric in
the evaluator's registry and then call it like any built-in.

Prerequisites
-------------
1. `pip install -e ./sdk[all]`
2. `cp ./sdk/.env.example ./.env` and fill in ALL THREE creds (LLM-as-judge
   metrics REQUIRE WXG_PROJECT_ID for the watsonx.ai foundation model)
3. The watsonx.ai project must have a Watson Machine Learning service
   associated (project → Manage → Services and Integrations)
4. Run: `python 03_custom_guardrails.py`
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from ibm_watsonx_gov.entities.criteria import Option
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.metrics import LLMAsJudgeMetric

from real_time_guardrails import GuardrailsConfig, GuardrailsEvaluator
from real_time_guardrails.core.custom_metrics import build_criteria_judge
from real_time_guardrails.core.registry import MetricEntry
from real_time_guardrails.core.thresholds import Direction, ThresholdSpec


load_dotenv()
ev = GuardrailsEvaluator()
cfg = GuardrailsConfig.from_env()
if not cfg.project_id:
    print("ERROR: WXG_PROJECT_ID is required for LLM-as-judge metrics.")
    sys.exit(1)

# Shared LLM judge — built once, reused for both custom metrics.
judge = LLMJudge(
    model=WxAIFoundationModel(model_id=cfg.judge_model_id, project_id=cfg.project_id)
)


# ── Style A: criteria + Option (short rubric, SDK builds the prompt) ───

brand_voice = build_criteria_judge(
    name="brand_voice",
    display_name="Brand Voice",
    criteria_description=(
        "Does the {generated_text} match our brand voice "
        "(professional, concise, warm but not casual)?"
    ),
    options=[
        Option(name="Yes", description="On-brand: professional, concise, warm.", value=1.0),
        Option(name="No", description="Off-brand or unprofessional.", value=0.0),
    ],
    judge=judge,
)


# ── Style B: prompt_template (full prompt control) ─────────────────────

step_by_step = LLMAsJudgeMetric(
    name="step_by_step_clarity",
    llm_judge=judge,
    prompt_template=(
        "You are evaluating whether an AI response provides clear, "
        "step-by-step instructions.\n\n"
        "Question: {input_text}\n"
        "Response: {generated_text}\n\n"
        "Return one of: clear / partial / unclear"
    ),
    input_fields=["input_text", "generated_text"],
    options={"clear": 1.0, "partial": 0.5, "unclear": 0.0},
)


# ── Register both custom metrics in the evaluator's registry ───────────

def register(name: str, display: str, metric: object, fields: frozenset[str], desc: str) -> None:
    entry = MetricEntry(
        name=display, metric=metric, category="quality",
        column_name=name + ".llm_as_judge",
        threshold_spec=ThresholdSpec(value=0.5, direction=Direction.LOW_IS_RISK, flag_value=None),
        required_fields=fields, description=desc,
    )
    ev.registry._by_name[entry.name] = entry

register("brand_voice", "Brand Voice", brand_voice,
         frozenset({"generated_text"}), "On-brand vs off-brand check (Yes/No).")
register("step_by_step_clarity", "Step-By-Step Clarity", step_by_step,
         frozenset({"input_text", "generated_text"}), "Clear/partial/unclear rubric for instructions.")
ev._threshold_resolver.attach_known_metrics(set(ev.registry.names))


# ── Demo: run both custom metrics on real data ─────────────────────────

RECORDS = [
    {
        "input_text": "How do I reset my password?",
        "generated_text": "1) Go to Settings > Security > Reset Password. 2) Enter your current password. 3) Choose a new one.",
    },
    {
        "input_text": "How do I reset my password?",
        "generated_text": "Hey! 😎 So passwords are like, super important, you know? You should probably reset it via the settings or something.",
    },
]


def main() -> None:
    print(f"Registry size: {len(ev.registry)} metrics (28 catalog + 2 custom)\n")
    for i, record in enumerate(RECORDS, 1):
        print(f"─ Record {i} — A={record['generated_text'][:60]}…")
        bundle = ev.evaluate(
            input_text=record["input_text"],
            generated_text=record["generated_text"],
            metrics=["Brand Voice", "Step-By-Step Clarity"],
        )
        for name, r in bundle.results.items():
            score = f"{r.score:.3f}" if r.score is not None else "n/a"
            print(f"    {name}: score={score} action={r.action} (threshold={r.threshold})")
        print()


if __name__ == "__main__":
    sys.exit(main())
