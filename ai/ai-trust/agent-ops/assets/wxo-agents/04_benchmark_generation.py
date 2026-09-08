"""
Benchmark Generation from User Stories

Automatically generates evaluation benchmarks (ground truth test cases)
from plain-English user stories. Converts natural language descriptions
of expected agent behavior into structured JSON benchmark files.

This eliminates the need to hand-write benchmark JSON — just describe
what the user should do and the framework generates the test case.

Prerequisites:
  - WXO Developer Edition running
  - Agent tools imported
  - pip install -r requirements.txt

Usage:
  python 04_benchmark_generation.py
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ── Configuration (override via command-line args) ────────────────────
STORIES_PATH = sys.argv[1] if len(sys.argv) > 1 else "sample_data/user_stories.csv"
TOOLS_PATH = sys.argv[2] if len(sys.argv) > 2 else "sample_agent/tools"
OUTPUT_DIR = sys.argv[3] if len(sys.argv) > 3 else "generated_benchmarks"


def run_generate(stories_path: str, tools_path: str, output_dir: str) -> Path:
    """Run the orchestrate evaluations generate CLI command.

    Converts user stories into structured benchmark JSON files.
    """
    cmd = [
        "orchestrate", "evaluations", "generate",
        "--stories-path", stories_path,
        "--tools-path", tools_path,
        "--output-dir", output_dir,
    ]

    print(f"Running: {' '.join(cmd)}")
    print("Generating benchmarks from user stories...\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Generation failed with exit code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    print(result.stdout)
    return Path(output_dir)


def review_generated_benchmarks(output_dir: Path) -> None:
    """Review the generated benchmark files and highlight key elements."""
    print("\n" + "=" * 60)
    print("GENERATED BENCHMARKS REVIEW")
    print("=" * 60)

    json_files = sorted(output_dir.rglob("*.json"))
    if not json_files:
        print("  No benchmark files generated.")
        return

    for json_file in json_files:
        if json_file.name.startswith("snapshot"):
            continue  # Skip LLM reasoning snapshots

        try:
            with open(json_file) as f:
                benchmark = json.load(f)
        except json.JSONDecodeError:
            continue

        print(f"\n  File: {json_file.name}")

        if isinstance(benchmark, dict):
            agent = benchmark.get("agent", "unknown")
            story = benchmark.get("story", "")
            starting = benchmark.get("starting_sentence", "")
            goals = benchmark.get("goals", {})
            details = benchmark.get("goal_details", [])

            print(f"    Agent: {agent}")
            print(f"    Story: \"{story[:80]}...\"")
            print(f"    First message: \"{starting[:60]}...\"")
            print(f"    Goals: {len(goals)} tool call(s)")

            for detail in details:
                tool_name = detail.get("tool_name", "unknown")
                args = detail.get("args", {})
                print(f"      → {tool_name}({', '.join(f'{k}={v}' for k, v in args.items())})")

    # Check for LLM reasoning snapshots
    snapshots = sorted(output_dir.rglob("snapshot*.json"))
    if snapshots:
        print(f"\n  LLM reasoning snapshots: {len(snapshots)} files")
        print("  (These show the LLM's reasoning for generating each test case)")


def show_stories_used(stories_path: str) -> None:
    """Display the user stories that were used for generation."""
    print("\n" + "─" * 60)
    print("INPUT USER STORIES")
    print("─" * 60)

    with open(stories_path) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            story = row.get("story", "")
            print(f"  {i + 1}. \"{story[:100]}...\"" if len(story) > 100 else f"  {i + 1}. \"{story}\"")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Agent Ops — Benchmark Generation from User Stories")
    print(f"Stories:  {STORIES_PATH}")
    print(f"Tools:    {TOOLS_PATH}")
    print(f"Output:   {OUTPUT_DIR}\n")

    # Show input stories
    show_stories_used(STORIES_PATH)

    # Generate benchmarks
    output_dir = run_generate(STORIES_PATH, TOOLS_PATH, OUTPUT_DIR)

    # Review generated files
    review_generated_benchmarks(output_dir)

    print(f"\nNext steps:")
    print(f"  1. Review and hand-edit the generated benchmarks if needed")
    print(f"  2. Run full evaluation: python 01_agent_evaluation.py")
    print(f"     (update BENCHMARK_DIR to point to {OUTPUT_DIR})")
