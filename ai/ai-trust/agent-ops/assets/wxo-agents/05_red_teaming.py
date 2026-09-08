"""
Red-Teaming — Adversarial Security Testing

Stress-tests your agent against 15 adversarial attack types to identify
security vulnerabilities before deployment.

Attack categories:
  On-policy (within domain):
  - instruction_override     : Attempts to override system instructions
  - emotional_appeal         : Uses emotional manipulation
  - role_playing             : Tricks agent into adopting unsafe roles
  - hypothetical_scenario    : Uses "what if" framing to bypass guardrails
  - authority_impersonation  : Claims to be an admin or authority figure
  - crescendo_attack         : Gradually escalates requests

  Off-policy (outside domain):
  - jailbreaking             : Direct attempts to bypass safety
  - prompt_leakage           : Tries to extract system prompt
  - topic_derailment         : Steers agent away from its domain
  - social_engineering       : Manipulates agent through social tactics
  - data_extraction          : Attempts to extract training data or PII

Prerequisites:
  - WXO Developer Edition running
  - Agent imported
  - pip install -r requirements.txt

Usage:
  python 05_red_teaming.py
"""

import json
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ── Configuration (override via command-line args) ────────────────────
BENCHMARK_DIR = sys.argv[1] if len(sys.argv) > 1 else "sample_data"
AGENT_DIR = sys.argv[2] if len(sys.argv) > 2 else "sample_agent"
AGENT_NAME = sys.argv[3] if len(sys.argv) > 3 else "customer_support_assistant"
ATTACK_TYPES = "instruction_override,crescendo_attack,jailbreaking,prompt_leakage"
RED_TEAM_PLAN_DIR = "red_team_plans"
RED_TEAM_RESULTS_DIR = "red_team_results"
NUM_SCENARIOS_PER_ATTACK = 1


def list_attacks() -> str:
    """List all available attack types."""
    cmd = ["orchestrate", "evaluations", "red-teaming", "list"]
    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return ""

    print(result.stdout)
    return result.stdout


def plan_attacks(
    attack_types: str,
    benchmark_dir: str,
    agent_dir: str,
    agent_name: str,
    output_dir: str,
    num_scenarios: int = 1,
) -> Path:
    """Generate adversarial attack scenarios."""
    cmd = [
        "orchestrate", "evaluations", "red-teaming", "plan",
        "-a", attack_types,
        "-d", benchmark_dir,
        "-g", agent_dir,
        "-t", agent_name,
        "-o", output_dir,
        "-n", str(num_scenarios),
    ]

    print(f"Running: {' '.join(cmd)}")
    print(f"Generating attack plans for: {attack_types}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Attack planning failed with exit code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    print(result.stdout)
    return Path(output_dir)


def run_attacks(plan_dir: str, output_dir: str) -> Path:
    """Execute the planned adversarial attacks against the agent."""
    cmd = [
        "orchestrate", "evaluations", "red-teaming", "run",
        "-a", plan_dir,
        "-o", output_dir,
    ]

    print(f"Running: {' '.join(cmd)}")
    print("Executing adversarial attacks...\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Attack execution failed with exit code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    print(result.stdout)
    return Path(output_dir)


def analyze_results(results_dir: Path) -> None:
    """Analyze red-teaming results to identify vulnerabilities."""
    print("\n" + "=" * 60)
    print("RED-TEAMING RESULTS ANALYSIS")
    print("=" * 60)

    json_files = sorted(results_dir.rglob("*.json"))
    if not json_files:
        print("  No result files found.")
        return

    vulnerabilities = []
    safe_count = 0

    for json_file in json_files:
        try:
            with open(json_file) as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict):
            attack_type = data.get("attack_type", json_file.stem)
            success = data.get("attack_success", data.get("success", False))

            if success:
                vulnerabilities.append({
                    "attack": attack_type,
                    "file": json_file.name,
                    "details": data.get("details", ""),
                })
            else:
                safe_count += 1

    total = len(vulnerabilities) + safe_count

    print(f"\n  Total attacks executed: {total}")
    print(f"  Agent defended:        {safe_count}")
    print(f"  Vulnerabilities found: {len(vulnerabilities)}")

    if vulnerabilities:
        print(f"\n  {'─' * 50}")
        print("  VULNERABILITIES:")
        for vuln in vulnerabilities:
            print(f"\n    Attack: {vuln['attack']}")
            print(f"    File:   {vuln['file']}")
            if vuln["details"]:
                print(f"    Details: {vuln['details'][:100]}...")

        print(f"\n  ACTION REQUIRED:")
        print(f"  - Review agent instructions for gaps in safety boundaries")
        print(f"  - Add explicit refusal patterns for detected attack types")
        print(f"  - Re-run red-teaming after fixes to verify remediation")
    else:
        print(f"\n  Agent successfully defended against all attack types.")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Agent Ops — Red-Teaming (Adversarial Security Testing)")
    print(f"Agent: {AGENT_NAME}")
    print(f"Attacks: {ATTACK_TYPES}\n")

    # Step 1: List available attacks
    print("=" * 60)
    print("AVAILABLE ATTACK TYPES")
    print("=" * 60)
    list_attacks()

    # Step 2: Generate attack plans
    print("\n" + "=" * 60)
    print("GENERATING ATTACK PLANS")
    print("=" * 60)
    plan_dir = plan_attacks(
        ATTACK_TYPES, BENCHMARK_DIR, AGENT_DIR, AGENT_NAME,
        RED_TEAM_PLAN_DIR, NUM_SCENARIOS_PER_ATTACK,
    )

    # Step 3: Execute attacks
    print("\n" + "=" * 60)
    print("EXECUTING ATTACKS")
    print("=" * 60)
    results_dir = run_attacks(RED_TEAM_PLAN_DIR, RED_TEAM_RESULTS_DIR)

    # Step 4: Analyze results
    analyze_results(results_dir)
