"""Generate test cases from user stories with `orchestrate evaluations generate`.

Input: a CSV with columns `story,agent` and the Python FILE that defines the agent's @tool functions
(a directory makes the command fall back to a minimal spec and guess).

Observed on ADK 2.18 / framework 1.5.2: `generate` calls the Langfuse API at the end of generation even when
--with-langfuse is not used; without LANGFUSE_HOST / LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY for a reachable
Langfuse project (Developer Edition `-l`, or a hosted one) it fails and writes no test cases. Without one,
author cases with a generator script instead — see examples/loan-underwriting/evaluations/make_testcases.py.

Usage:
  python 04_benchmark_generation.py [stories.csv] [tools file] [output dir]
  defaults: sample_data/user_stories.csv  sample_agent/tools/support_tools.py  results/generated
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ORC = os.environ.get("ORC", "orchestrate")
STORIES = sys.argv[1] if len(sys.argv) > 1 else "sample_data/user_stories.csv"
TOOLS_FILE = sys.argv[2] if len(sys.argv) > 2 else "sample_agent/tools/support_tools.py"
OUTPUT_DIR = Path(sys.argv[3] if len(sys.argv) > 3 else "results/generated")


def check_langfuse_env() -> None:
    missing = [k for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY") if not os.environ.get(k)]
    if missing:
        print(f"WARNING: {', '.join(missing)} not set. On ADK 2.18 / framework 1.5.2 `generate` needs a reachable "
              "Langfuse project (LANGFUSE_HOST + keys) and writes nothing without it; export them or write cases with a generator script.")


def run_generate() -> None:
    if not Path(TOOLS_FILE).is_file():
        sys.exit(f"tools path must be a Python file: {TOOLS_FILE}")
    cmd = [ORC, "evaluations", "generate", "-s", STORIES, "-t", TOOLS_FILE, "-o", str(OUTPUT_DIR)]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"generate exited with {result.returncode}")


def review() -> None:
    files = [f for f in sorted(OUTPUT_DIR.rglob("*.json")) if "snapshot" not in f.name]
    if not files:
        print("No test cases were written. See the warning above.")
        return
    print(f"\nGenerated {len(files)} case(s) under {OUTPUT_DIR}:")
    for f in files:
        try:
            case = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        tools = [g.get("tool_name") for g in case.get("goal_details", []) if g.get("type") == "tool_call"]
        print(f"  {f.relative_to(OUTPUT_DIR)}: agent={case.get('agent')} goals={len(case.get('goals', {}))} tools={tools}")
    print("\nReview before using: strict values the story never states, missing handoff goals "
          "(chat_with_collaborator_<agent>) on multi-agent systems, no end-of-conversation signal, no max_user_turns.")


if __name__ == "__main__":
    check_langfuse_env()
    run_generate()
    review()
