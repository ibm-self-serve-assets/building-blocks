"""Tutorial 01: Content Safety Guardrails with real-time-guardrails

Real-time detection of harmful content on AI inputs and outputs. Uses the
package's 12 safety metrics (HAP, PII, Jailbreak, SocialBias, Violence,
Profanity, Unethical, Sexual Content, Evasiveness, Harm, HarmEngagement,
PromptSafetyRisk) with the 3-state action model:

  - Pass   : score is safely below the flag threshold
  - Flag   : score is between flag and block thresholds (allow + log for review)
  - Block  : score crossed the block threshold (refuse with fallback message)

Default thresholds: Safety category → block=0.65, flag=0.4 (HIGH_IS_RISK).

Prerequisites
-------------
1. `pip install -e ./sdk[all]`    (or `pip install real-time-guardrails[all]` once published)
2. `cp ./sdk/.env.example ./.env` and fill in WATSONX_APIKEY + WXG_SERVICE_INSTANCE_ID
   (WXG_PROJECT_ID is optional unless you also want LLM-as-judge metrics)
3. Run: `python 01_content_safety_guardrails.py`
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from real_time_guardrails import GuardrailsEvaluator


load_dotenv()

# Build the evaluator ONCE — registry build is multi-second; reuse across calls.
ev = GuardrailsEvaluator()

# What we want to enforce on the input side. categories=["safety"] selects all
# 11 input-eligible safety metrics whose required fields are present.
SAFETY_METRICS = [
    "HAP (Hate, Abuse, Profanity)",
    "PII Detection",
    "Jailbreak Detection",
    "Social Bias",
    "Violence",
    "Profanity",
]


def check(text: str, *, role: str = "input") -> None:
    """Evaluate a piece of text and print the per-metric outcome."""
    kwargs = {"metrics": SAFETY_METRICS}
    if role == "input":
        kwargs["input_text"] = text
    else:
        kwargs["generated_text"] = text

    bundle = ev.evaluate(**kwargs)
    print(f"  [{bundle.overall_action().upper()}] {role}: {text[:80]!r}")
    for name, r in bundle.results.items():
        if r.action != "Pass":
            score = f"{r.score:.3f}" if r.score is not None else "n/a"
            print(f"    - {name}: score={score} action={r.action} (threshold={r.threshold})")
    if bundle.failed():
        fallback = bundle.failed()[0].fallback_message
        if fallback:
            print(f"    fallback → {fallback!r}")


def main() -> None:
    scenarios_path = Path(__file__).parent / "sample_data" / "guardrail_test_scenarios.json"
    scenarios = json.loads(scenarios_path.read_text())

    print("=" * 70)
    print("CONTENT SAFETY GUARDRAILS")
    print("=" * 70)
    print(f"Built evaluator with {ev.list_metrics()['total']} metrics total.")
    print(f"Running input + output safety checks on {len(scenarios)} scenarios.\n")

    for scenario in scenarios:
        print(f"─ Scenario: {scenario['id']} — {scenario['description']}")
        check(scenario["input_text"], role="input")
        # If input is blocked, skip output check (the agent wouldn't have run)
        # — left here for didactic purposes; production code would short-circuit.
        if scenario.get("generated_text"):
            check(scenario["generated_text"], role="output")
        print()


if __name__ == "__main__":
    sys.exit(main())
