"""
Agent Analysis with watsonx Orchestrate ADK

Diagnoses agent failures by analyzing evaluation results. Supports two modes:
  - Default:   Trace-level analysis of conversation flow and tool call errors
  - Enhanced:  Includes tool docstring inspection to detect schema issues

This script automates the `orchestrate evaluations analyze` CLI command
and parses the output for programmatic use.

Prerequisites:
  - Evaluation results from 01_agent_evaluation.py
  - pip install -r requirements.txt

Usage:
  python 02_agent_analysis.py                         # auto-detect latest results
  python 02_agent_analysis.py eval_results/20260423   # specify results directory
"""

import subprocess
import sys
from pathlib import Path


# ── Configuration ─────────────────────────────────────────────────────
OUTPUT_DIR = "eval_results"
TOOLS_PATH = "sample_agent/tools"


def find_latest_results(output_dir: str) -> Path:
    """Find the most recent evaluation results directory."""
    results_base = Path(output_dir)
    if not results_base.exists():
        print(f"ERROR: {output_dir} does not exist. Run 01_agent_evaluation.py first.")
        sys.exit(1)

    result_dirs = sorted(
        [d for d in results_base.iterdir() if d.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    if not result_dirs:
        print(f"ERROR: No results found in {output_dir}.")
        sys.exit(1)

    return result_dirs[0]


def run_analysis(results_dir: Path, mode: str = "default") -> str:
    """Run the orchestrate evaluations analyze CLI command.

    Args:
        results_dir: Path to the evaluation results directory.
        mode: Analysis mode — "default" or "enhanced".

    Returns:
        The analysis output text.
    """
    cmd = [
        "orchestrate", "evaluations", "analyze",
        "-d", str(results_dir),
    ]

    if mode == "enhanced":
        cmd.extend([
            "--tools-path", TOOLS_PATH,
            "--mode", "enhanced",
        ])

    print(f"Running: {' '.join(cmd)}")
    print(f"Mode: {mode}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Analysis failed with exit code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    return result.stdout


def parse_analysis(output: str) -> dict:
    """Parse the analysis output to extract failure categories.

    Returns:
        dict with counts of failure types and recommendations.
    """
    failures = {
        "wrong_tool_called": 0,
        "wrong_parameters": 0,
        "missing_tool_call": 0,
        "extra_tool_call": 0,
        "conversation_ended_early": 0,
        "other": 0,
    }

    for line in output.lower().split("\n"):
        if "wrong tool" in line:
            failures["wrong_tool_called"] += 1
        elif "wrong parameter" in line or "incorrect arg" in line:
            failures["wrong_parameters"] += 1
        elif "missing" in line and "tool" in line:
            failures["missing_tool_call"] += 1
        elif "extra" in line and "tool" in line:
            failures["extra_tool_call"] += 1
        elif "ended early" in line or "conversation end" in line:
            failures["conversation_ended_early"] += 1

    return failures


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Determine results directory
    if len(sys.argv) > 1:
        results_dir = Path(sys.argv[1])
    else:
        results_dir = find_latest_results(OUTPUT_DIR)

    print("Agent Ops — Failure Analysis")
    print(f"Results directory: {results_dir}\n")

    # Step 1: Default analysis
    print("=" * 60)
    print("DEFAULT ANALYSIS")
    print("=" * 60)
    default_output = run_analysis(results_dir, mode="default")
    if default_output:
        print(default_output)

    # Step 2: Enhanced analysis (includes tool docstring inspection)
    print("\n" + "=" * 60)
    print("ENHANCED ANALYSIS (with tool schema inspection)")
    print("=" * 60)
    enhanced_output = run_analysis(results_dir, mode="enhanced")
    if enhanced_output:
        print(enhanced_output)

    # Step 3: Parse and summarize failures
    failures = parse_analysis(default_output + enhanced_output)
    total_failures = sum(failures.values())

    if total_failures > 0:
        print("\n" + "─" * 60)
        print("FAILURE SUMMARY")
        print("─" * 60)
        for category, count in failures.items():
            if count > 0:
                print(f"  {category}: {count}")
        print(f"\n  Total failure signals: {total_failures}")
        print("\n  Recommendations:")
        if failures["wrong_tool_called"] > 0:
            print("  - Review tool descriptions — agent may be confused about tool purpose")
        if failures["wrong_parameters"] > 0:
            print("  - Check tool docstrings — parameter descriptions may be ambiguous")
        if failures["missing_tool_call"] > 0:
            print("  - Agent may not recognize when a tool should be invoked")
        if failures["extra_tool_call"] > 0:
            print("  - Agent is calling unnecessary tools — review instructions")
        if failures["conversation_ended_early"] > 0:
            print("  - Agent is ending conversations prematurely — check goal completion logic")
    else:
        print("\nNo failure patterns detected in analysis output.")
