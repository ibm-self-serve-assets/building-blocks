"""Run `orchestrate evaluations quick-eval`: a reference-less smoke test.

Without ground truth, quick-eval drives each test case's story against the agent and reports tool calls
attempted, successful, failed on schema mismatch, and failed on hallucinated (non-existent) tools.
Python tools only. On multi-agent systems every chat_with_collaborator_* handoff is listed as a schema
mismatch — ignore those rows.

Usage:
  python 03_quick_eval.py [test paths] [tools dir] [output dir]
  defaults: sample_data/benchmarks.json  sample_agent/tools  results/quick_eval
"""

import csv
import os
import subprocess
import sys
from pathlib import Path

ORC = os.environ.get("ORC", "orchestrate")
TEST_PATHS = sys.argv[1] if len(sys.argv) > 1 else "sample_data/benchmarks.json"
TOOLS_PATH = sys.argv[2] if len(sys.argv) > 2 else "sample_agent/tools"
OUTPUT_DIR = Path(sys.argv[3] if len(sys.argv) > 3 else "results/quick_eval")


def run_quick_eval() -> Path:
    cmd = [ORC, "evaluations", "quick-eval", "-p", TEST_PATHS, "-t", TOOLS_PATH, "-o", str(OUTPUT_DIR)]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"quick-eval exited with {result.returncode}")
    runs = sorted(p for p in OUTPUT_DIR.glob("*/") if p.is_dir()) if OUTPUT_DIR.exists() else []
    return runs[-1] if runs else OUTPUT_DIR


def summarize(run: Path) -> None:
    print(f"\nResults: {run}")
    for f in sorted(run.rglob("*")):
        if f.is_file():
            print("  ", f.relative_to(run))
    for csv_file in sorted(run.rglob("*.csv")):
        rows = list(csv.DictReader(open(csv_file, encoding="utf-8")))
        if not rows:
            continue
        print(f"\n{csv_file.name}:")
        for r in rows:
            print("  " + ", ".join(f"{k}={v}" for k, v in r.items() if v not in ("", None)))
    print("\nNext: python 01_agent_evaluation.py  (full evaluation with ground truth)")


if __name__ == "__main__":
    summarize(run_quick_eval())
