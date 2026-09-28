"""
Quick-Eval — Referenceless Agent Validation

Fast sanity check that validates agent behavior without ground truth
benchmarks. Detects structural issues early:
  - Tool schema mismatches (agent calling tools with wrong signatures)
  - Hallucinated tool calls (agent inventing tools that don't exist)
  - Parameter type violations

Use quick-eval as the first step in your evaluation workflow — it's
faster than full evaluation and catches obvious issues.

Prerequisites:
  - WXO Developer Edition running
  - Agent imported
  - pip install -r requirements.txt

Usage:
  python 03_quick_eval.py
"""

import json
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ── Configuration (override via command-line args) ────────────────────
BENCHMARK_DIR = sys.argv[1] if len(sys.argv) > 1 else "sample_data"
TOOLS_PATH = sys.argv[2] if len(sys.argv) > 2 else "sample_agent/tools"
OUTPUT_DIR = sys.argv[3] if len(sys.argv) > 3 else "quick_eval_results"


def run_quick_eval(benchmark_dir: str, tools_path: str, output_dir: str) -> Path:
    """Run the orchestrate evaluations quick-eval CLI command.

    Quick-eval validates tool schemas against benchmark expectations
    without running full agent conversations.
    """
    cmd = [
        "orchestrate", "evaluations", "quick-eval",
        "--test-paths", benchmark_dir,
        "--tools-path", tools_path,
        "--output-dir", output_dir,
    ]

    print(f"Running: {' '.join(cmd)}")
    print("Quick-eval validates tool schemas — no full conversations needed.\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Quick-eval failed with exit code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    print(result.stdout)

    # Find results
    results_base = Path(output_dir)
    result_dirs = sorted(
        [d for d in results_base.iterdir() if d.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    ) if results_base.exists() else []

    return result_dirs[0] if result_dirs else results_base


def parse_tool_spec(results_dir: Path) -> None:
    """Parse the tool_spec.json produced by quick-eval."""
    spec_path = results_dir / "tool_spec.json"
    if not spec_path.exists():
        # Try finding it in the output dir directly
        for path in results_dir.rglob("tool_spec.json"):
            spec_path = path
            break

    if spec_path.exists():
        with open(spec_path) as f:
            spec = json.load(f)

        print("\n" + "=" * 60)
        print("TOOL SPECIFICATION VALIDATION")
        print("=" * 60)

        if isinstance(spec, dict):
            for tool_name, tool_info in spec.items():
                print(f"\n  Tool: {tool_name}")
                if isinstance(tool_info, dict):
                    for key, value in tool_info.items():
                        print(f"    {key}: {value}")
        elif isinstance(spec, list):
            for tool_info in spec:
                print(f"\n  Tool: {tool_info.get('name', 'unknown')}")
                for key, value in tool_info.items():
                    if key != "name":
                        print(f"    {key}: {value}")
    else:
        print("\nNo tool_spec.json found in results.")


def summarize_quick_eval(results_dir: Path) -> None:
    """Scan results directory for any validation issues."""
    print("\n" + "=" * 60)
    print("QUICK-EVAL SUMMARY")
    print("=" * 60)

    # Check for any error or warning files
    issue_count = 0
    for result_file in results_dir.rglob("*.json"):
        try:
            with open(result_file) as f:
                data = json.load(f)
            if isinstance(data, dict):
                errors = data.get("errors", [])
                warnings = data.get("warnings", [])
                if errors:
                    issue_count += len(errors)
                    print(f"\n  Errors in {result_file.name}:")
                    for error in errors:
                        print(f"    - {error}")
                if warnings:
                    issue_count += len(warnings)
                    print(f"\n  Warnings in {result_file.name}:")
                    for warning in warnings:
                        print(f"    - {warning}")
        except (json.JSONDecodeError, KeyError):
            continue

    if issue_count == 0:
        print("\n  All tool schemas validated successfully.")
        print("  Proceed to full evaluation (01_agent_evaluation.py).")
    else:
        print(f"\n  Found {issue_count} issues. Fix these before running full evaluation.")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Agent Ops — Quick-Eval (Referenceless Validation)")
    print(f"Benchmarks: {BENCHMARK_DIR}")
    print(f"Tools:      {TOOLS_PATH}")
    print(f"Output:     {OUTPUT_DIR}\n")

    # Step 1: Run quick-eval
    results_dir = run_quick_eval(BENCHMARK_DIR, TOOLS_PATH, OUTPUT_DIR)
    print(f"\nResults saved to: {results_dir}")

    # Step 2: Parse tool spec
    parse_tool_spec(results_dir)

    # Step 3: Summary
    summarize_quick_eval(results_dir)
