"""Run `orchestrate evaluations analyze` on an evaluation run.

Usage:
  python 02_agent_analysis.py                              # latest run under results/evaluate/
  python 02_agent_analysis.py results/evaluate/<timestamp>  # a specific run
  python 02_agent_analysis.py <run> --enhanced [--tools sample_agent/tools]   # adds docstring checks for failed tools

Framework 1.5.2 writes `text_match` as a number in messages/*.metrics.json while `analyze` validates it as
the enum string; this script analyzes a normalized copy of the run folder (<run>-analyze).
"""

import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ORC = os.environ.get("ORC", "orchestrate")
RESULTS_ROOT = Path("results/evaluate")
TEXT_MATCH = {1: "Summary Matched", 0: "Summary MisMatched"}


def latest_run(root: Path) -> Path:
    runs = sorted(p for p in root.glob("*/") if (p / "summary_metrics.csv").exists() and not p.name.endswith("-analyze"))
    if not runs:
        sys.exit(f"no runs under {root}; run 01_agent_evaluation.py first")
    return runs[-1]


def normalized_copy(run: Path) -> Path:
    dst = run.parent / (run.name.rstrip("/") + "-analyze")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(run, dst)
    for mf in glob.glob(str(dst / "messages" / "*.metrics.json")):
        m = json.load(open(mf))
        tm = m.get("text_match")
        if isinstance(tm, (int, float)) and not isinstance(tm, bool):
            m["text_match"] = "Summary Matched" if tm >= 1 else "Summary MisMatched" if tm <= 0 else "Partially Match"
            json.dump(m, open(mf, "w"))
    return dst


def analyze(run: Path, enhanced: bool, tools: str | None) -> None:
    cmd = [ORC, "evaluations", "analyze", "-d", str(run)]
    if tools:
        cmd += ["-t", tools]
    if enhanced:
        cmd += ["--mode", "enhanced"]
    env = dict(os.environ, COLUMNS=os.environ.get("COLUMNS", "170"))
    if enhanced:
        env.setdefault("GATE_TOOL_ENRICHMENTS", "false")
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        sys.exit(f"analyze exited with {result.returncode}")


def failing_steps(run: Path) -> None:
    """Quote the first judged-wrong step of each case from messages/*.messages.analyze.json."""
    for f in sorted(run.glob("messages/*.messages.analyze.json")):
        case = f.name.replace(".messages.analyze.json", "")
        for item in json.loads(f.read_text()):
            reason = (item.get("reason") or {}).get("reason")
            msg = item.get("message", {})
            if reason and msg.get("type") == "tool_call":
                try:
                    call = json.loads(msg.get("content", "{}"))
                except json.JSONDecodeError:
                    call = {"name": msg.get("content")}
                print(f"  {case}: {reason} — {call.get('name')} args={call.get('args')} expected={(item.get('reason') or {}).get('expected')}")
                break


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    enhanced = "--enhanced" in sys.argv
    tools = sys.argv[sys.argv.index("--tools") + 1] if "--tools" in sys.argv else ("sample_agent/tools" if enhanced else None)
    run = Path(args[0]) if args else latest_run(RESULTS_ROOT)
    print(f"Run: {run}")
    analyze(normalized_copy(run), enhanced, tools)
    print("\nFirst judged-wrong tool step per case (from messages/*.messages.analyze.json):")
    failing_steps(run)
