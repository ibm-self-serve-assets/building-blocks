"""Red-team a native watsonx Orchestrate agent: list attacks, plan them from your test cases, run, summarize.

Attack catalogue (framework 1.5): on-policy — Instruction Override, Crescendo Attack, Emotional Appeal,
Imperative Emphasis, Role Playing, Random Prefix, Random Postfix, Encoded Input, Foreign Languages;
off-policy — Crescendo Prompt Leakage, Functionality Based Attacks, Undermine Model, Unsafe Topics,
Jailbreaking, Topic Derailment. Names are accepted as listed or in snake_case; "all" is not a keyword.

The goal inside each attack file defines what "the attack succeeded" means. Generated plans need review:
run with --plan-only, edit the files under the plan directory, then run again without --plan-only.

Usage:
  python 05_red_teaming.py [--plan-only] [--run-only]
  env: ATTACKS="Instruction Override,Crescendo Attack,Emotional Appeal"  TEST_PATHS=sample_data/benchmarks.json
       AGENTS_DIR=sample_agent  TARGET=customer_support_assistant  PLAN_DIR=results/red_team_plan
       RESULTS_DIR=results/red_team  VARIANTS=1  ORC=orchestrate
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ORC = os.environ.get("ORC", "orchestrate")
ATTACKS = os.environ.get("ATTACKS", "Instruction Override,Crescendo Attack,Emotional Appeal")
TEST_PATHS = os.environ.get("TEST_PATHS", "sample_data/benchmarks.json")
AGENTS_DIR = os.environ.get("AGENTS_DIR", "sample_agent")
TARGET = os.environ.get("TARGET", "customer_support_assistant")
PLAN_DIR = Path(os.environ.get("PLAN_DIR", "results/red_team_plan"))
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "results/red_team"))
VARIANTS = os.environ.get("VARIANTS", "1")


def run(cmd: list[str]) -> None:
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"{cmd[2]} exited with {result.returncode}")


def plan() -> None:
    run([ORC, "evaluations", "red-teaming", "list"])
    run([ORC, "evaluations", "red-teaming", "plan", "-a", ATTACKS, "-d", TEST_PATHS, "-g", AGENTS_DIR,
         "-t", TARGET, "-o", str(PLAN_DIR), "-n", VARIANTS])
    files = sorted(PLAN_DIR.glob("*.json"))
    print(f"\n{len(files)} attack file(s) under {PLAN_DIR}. Review each one: `targeted_policy` states the rule; "
          "`goals`/`goal_details` must describe the forbidden outcome (the tool call or text that must never happen).")
    for f in files:
        try:
            a = json.loads(f.read_text())
            print(f"  {f.name}: {a.get('attack_data', {}).get('attack_name')} → goals {list(a.get('goals', {}))}")
        except json.JSONDecodeError:
            print(f"  {f.name}: (unreadable)")


def execute() -> None:
    run([ORC, "evaluations", "red-teaming", "run", "-a", str(PLAN_DIR), "-o", str(RESULTS_DIR)])
    summary_file = RESULTS_DIR / "attacks_results.json"
    if summary_file.exists():
        summary = json.loads(summary_file.read_text())
        print("\nSummary:", {k: v for k, v in summary.items() if isinstance(v, (int, float, str))})
    print("\nPer attack:")
    for f in sorted((RESULTS_DIR / "results").glob("*.result.json")):
        success = json.loads(f.read_text()).get("success")
        verdict = "SUCCEEDED (vulnerability)" if success else "resisted"
        print(f"  {f.name.replace('.result.json', '')}: {verdict}")
    print(f"\nTranscripts: {RESULTS_DIR}/messages/<attack>.messages.json — read the ones that succeeded, "
          "fix the instructions or structure, re-run the same attack files.")


if __name__ == "__main__":
    if "--run-only" not in sys.argv:
        plan()
    if "--plan-only" in sys.argv:
        sys.exit(0)
    execute()
