"""Run `orchestrate evaluations evaluate` from a config file and summarize the run.

The framework evaluates the agent in the ACTIVE orchestrate environment (`orchestrate env list`).

Usage:
  python 01_agent_evaluation.py [config.yaml]        # default: sample_data/eval_config.yaml
  ORC=/path/to/orchestrate python 01_agent_evaluation.py evaluations/eval_config_v2.yaml

Prints the command, then one row per test case from summary_metrics.csv plus the averages.
"""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ORC = os.environ.get("ORC", "orchestrate")
CONFIG = Path(sys.argv[1] if len(sys.argv) > 1 else "sample_data/eval_config.yaml")

COLUMNS = [  # framework 1.5 column names
    ("dataset_name", "case"), ("is_success", "success"), ("orchestrate_agent_routing_accuracy", "routing"),
    ("tool_call_recall", "recall"), ("tool_call_precision", "precision"), ("missed_tool_calls", "missed"),
    ("tool_calls_with_incorrect_parameter", "bad_args"), ("text_match", "text"), ("average_agent_response_time", "resp_s"),
]


def run_evaluate(config: Path) -> Path:
    output_dir = Path(yaml.safe_load(config.read_text())["output_dir"])
    before = {p for p in output_dir.glob("*/") if (p / "summary_metrics.csv").exists()} if output_dir.exists() else set()
    cmd = [ORC, "evaluations", "evaluate", "-c", str(config)]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"evaluate exited with {result.returncode}")
    runs = sorted(p for p in output_dir.glob("*/") if (p / "summary_metrics.csv").exists())
    new = [p for p in runs if p not in before] or runs
    if not new:
        sys.exit(f"no run with summary_metrics.csv under {output_dir}")
    return new[-1]


def summarize(run: Path) -> None:
    rows = list(csv.DictReader(open(run / "summary_metrics.csv", encoding="utf-8")))
    print(f"\nRun: {run}")
    print(" ".join(f"{label:>10}" if i else f"{label:<32}" for i, (_, label) in enumerate(COLUMNS)))
    for r in rows:
        print(" ".join(f"{r.get(col, ''):>10}" if i else f"{r.get(col, ''):<32}" for i, (col, _) in enumerate(COLUMNS)))
    ok = sum(r.get("is_success") == "True" for r in rows)
    print(f"\njourney success: {ok}/{len(rows)}")
    avg = run / "average_metrics.json"
    if avg.exists():
        numbers = {k: round(v, 3) for k, v in json.loads(avg.read_text()).items() if isinstance(v, (int, float))}
        print("averages:", numbers)
    if ok == len(rows):
        print("\nVerdict: PASS — every journey succeeded.")
    else:
        print("\nVerdict: REVIEW — read messages/<case>.messages.analyze.json for each failed case, or run:")
        print(f"  python 02_agent_analysis.py {run}")


if __name__ == "__main__":
    if not CONFIG.exists():
        sys.exit(f"config not found: {CONFIG}")
    summarize(run_evaluate(CONFIG))
