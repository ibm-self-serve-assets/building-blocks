"""
Agent Evaluation with watsonx Orchestrate ADK

Runs benchmarks against a deployed agent using LLM-simulated users,
then parses and analyzes the results programmatically.

This script automates the `orchestrate evaluations evaluate` CLI command
and processes the output — suitable for CI/CD pipeline integration.

Metrics measured:
  - Journey Success:       Did the agent complete all goals? (binary)
  - Journey Completion %:  Percentage of goals met
  - Tool Call Precision:   Correct calls / total calls made
  - Tool Call Recall:      Expected calls made / total expected
  - Agent Routing F1:      Harmonic mean of precision and recall

Prerequisites:
  - WXO Developer Edition running (orchestrate server start -e .env)
  - Agent imported (orchestrate agents import -f agent_config.yaml)
  - pip install -r requirements.txt

Usage:
  python 01_agent_evaluation.py
"""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ── Configuration (override via command-line args) ────────────────────
BENCHMARK_DIR = sys.argv[1] if len(sys.argv) > 1 else "sample_data"
OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "eval_results"


def run_evaluation(benchmark_dir: str, output_dir: str) -> Path:
    """Run the orchestrate evaluations evaluate CLI command.

    Args:
        benchmark_dir: Path to directory containing benchmark JSON files.
        output_dir: Base directory for evaluation results.

    Returns:
        Path to the timestamped results directory.
    """
    cmd = [
        "orchestrate", "evaluations", "evaluate",
        "--test-paths", benchmark_dir,
        "--output-dir", output_dir,
    ]

    print(f"Running: {' '.join(cmd)}")
    print("This may take a few minutes depending on the number of scenarios...\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Evaluation failed with exit code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    print(result.stdout)

    # Find the timestamped results directory (most recent)
    results_base = Path(output_dir)
    if not results_base.exists():
        print(f"ERROR: Output directory {output_dir} not found.")
        sys.exit(1)

    result_dirs = sorted(results_base.iterdir(), key=lambda p: p.name, reverse=True)
    if not result_dirs:
        print("ERROR: No results directories found.")
        sys.exit(1)

    return result_dirs[0]


def parse_summary_metrics(results_dir: Path) -> list[dict]:
    """Parse the summary_metrics.csv produced by the evaluation.

    Returns:
        List of dicts, one per scenario, with all metric columns.
    """
    csv_path = results_dir / "summary_metrics.csv"
    if not csv_path.exists():
        print(f"WARNING: {csv_path} not found. Looking for alternative output files...")
        return []

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        return list(reader)


def print_results(metrics: list[dict]) -> None:
    """Print evaluation results in a readable format."""
    if not metrics:
        print("No metrics to display.")
        return

    print("\n" + "=" * 70)
    print("AGENT EVALUATION RESULTS")
    print("=" * 70)

    # Per-scenario results
    for i, row in enumerate(metrics):
        scenario = row.get("test_case", row.get("scenario", f"Scenario {i + 1}"))
        journey_success = row.get("journey_success", "N/A")
        completion = row.get("journey_completion_pct", "N/A")
        precision = row.get("tool_call_precision", "N/A")
        recall = row.get("tool_call_recall", "N/A")
        f1 = row.get("agent_routing_f1", "N/A")

        print(f"\n  {scenario}:")
        print(f"    Journey Success:     {journey_success}")
        print(f"    Completion:          {completion}")
        print(f"    Tool Call Precision: {precision}")
        print(f"    Tool Call Recall:    {recall}")
        print(f"    Agent Routing F1:    {f1}")

    # Aggregate summary
    print(f"\n{'─' * 70}")
    print("AGGREGATE SUMMARY")
    print(f"{'─' * 70}")

    total = len(metrics)
    try:
        successes = sum(1 for m in metrics if float(m.get("journey_success", 0)) == 1.0)
        avg_precision = sum(float(m.get("tool_call_precision", 0)) for m in metrics) / total
        avg_recall = sum(float(m.get("tool_call_recall", 0)) for m in metrics) / total
        avg_f1 = sum(float(m.get("agent_routing_f1", 0)) for m in metrics) / total

        print(f"  Total scenarios:     {total}")
        print(f"  Successful journeys: {successes}/{total} ({successes / total * 100:.0f}%)")
        print(f"  Avg Precision:       {avg_precision:.3f}")
        print(f"  Avg Recall:          {avg_recall:.3f}")
        print(f"  Avg F1:              {avg_f1:.3f}")

        # Pass/fail verdict
        print(f"\n  Verdict: ", end="")
        if successes == total and avg_f1 >= 0.9:
            print("PASS — All journeys successful, routing quality high.")
        elif successes / total >= 0.8:
            print("REVIEW — Most journeys pass but some failures need investigation.")
        else:
            print("FAIL — Too many journey failures. Run analyze to diagnose.")
    except (ValueError, ZeroDivisionError):
        print("  Could not compute aggregates — check raw CSV for details.")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Agent Ops — Evaluation Runner")
    print(f"Benchmark directory: {BENCHMARK_DIR}")
    print(f"Output directory:    {OUTPUT_DIR}\n")

    # Step 1: Run evaluation
    results_dir = run_evaluation(BENCHMARK_DIR, OUTPUT_DIR)
    print(f"\nResults saved to: {results_dir}")

    # Step 2: Parse and display results
    metrics = parse_summary_metrics(results_dir)
    print_results(metrics)

    # Step 3: Suggest next steps
    print(f"\nNext steps:")
    print(f"  1. Run analysis:  python 02_agent_analysis.py {results_dir}")
    print(f"  2. Quick eval:    python 03_quick_eval.py")
    print(f"  3. Red-teaming:   python 05_red_teaming.py")
