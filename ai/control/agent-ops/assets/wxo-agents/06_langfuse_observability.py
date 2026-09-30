"""
Langfuse Observability Integration

Track cost, latency, and token usage per agent interaction with full
traceability using Langfuse.

Workflow:
  1. Start WXO Developer Edition with Langfuse enabled
  2. Run evaluation with --with-langfuse flag
  3. Access the Langfuse dashboard for visual trace exploration
  4. Query Langfuse API programmatically for metrics

Prerequisites:
  - WXO Developer Edition running with Langfuse: orchestrate server start -e .env -l
  - Langfuse credentials set (see .env.template)
  - pip install -r requirements.txt

Usage:
  python 06_langfuse_observability.py
"""

import json
import os
import subprocess
import sys
from base64 import b64encode

import requests
from dotenv import load_dotenv

load_dotenv()


# ── Configuration ─────────────────────────────────────────────────────
BENCHMARK_DIR = "sample_data"
OUTPUT_DIR = "eval_results_langfuse"

LANGFUSE_BASE_URL = os.environ.get("LANGFUSE_BASE_URL", "http://localhost:3010")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "")


def check_langfuse_health() -> bool:
    """Verify Langfuse is running and accessible."""
    try:
        response = requests.get(f"{LANGFUSE_BASE_URL}/api/public/health", timeout=5)
        if response.status_code == 200:
            print(f"  Langfuse is healthy at {LANGFUSE_BASE_URL}")
            return True
        else:
            print(f"  Langfuse returned status {response.status_code}")
            return False
    except requests.ConnectionError:
        print(f"  ERROR: Cannot reach Langfuse at {LANGFUSE_BASE_URL}")
        print("  Make sure WXO Developer Edition is running with -l flag:")
        print("    orchestrate server start -e .env -l")
        return False


def configure_model_pricing() -> None:
    """Register custom model pricing in Langfuse for cost tracking.

    Without this, Langfuse cannot calculate costs for non-standard models.
    """
    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        print("  WARNING: Langfuse API keys not set. Skipping model pricing config.")
        return

    auth_token = b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()

    model_config = {
        "modelName": "groq/openai/gpt-oss-120b",
        "matchPattern": "(?i)^(groq/openai/gpt-oss-120b)$",
        "unit": "TOKENS",
        "tokenizerId": "openai",
        "tokenizerConfig": {"tokenizerModel": "gpt-4o"},
        "inputPrice": 0.000001,
        "outputPrice": 0.000002,
    }

    try:
        response = requests.post(
            f"{LANGFUSE_BASE_URL}/api/public/models",
            headers={
                "Authorization": f"Basic {auth_token}",
                "Content-Type": "application/json",
            },
            json=model_config,
            timeout=10,
        )
        if response.status_code in (200, 201):
            print("  Model pricing configured successfully.")
        elif response.status_code == 409:
            print("  Model pricing already configured.")
        else:
            print(f"  WARNING: Model pricing config returned {response.status_code}")
    except requests.ConnectionError:
        print("  WARNING: Could not configure model pricing.")


def run_evaluation_with_langfuse(benchmark_dir: str, output_dir: str) -> None:
    """Run evaluation with Langfuse tracing enabled."""
    cmd = [
        "orchestrate", "evaluations", "evaluate",
        "--test-paths", benchmark_dir,
        "--output-dir", output_dir,
        "--with-langfuse",
    ]

    print(f"\nRunning: {' '.join(cmd)}")
    print("Evaluation traces will be sent to Langfuse...\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Evaluation failed with exit code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    print(result.stdout)


def query_langfuse_traces() -> None:
    """Query Langfuse API for recent traces and display cost/latency stats."""
    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        print("\n  Langfuse API keys not set — skipping trace query.")
        print(f"  View traces manually at: {LANGFUSE_BASE_URL}")
        return

    auth_token = b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()

    try:
        response = requests.get(
            f"{LANGFUSE_BASE_URL}/api/public/traces",
            headers={"Authorization": f"Basic {auth_token}"},
            params={"limit": 10, "orderBy": "timestamp.desc"},
            timeout=10,
        )

        if response.status_code != 200:
            print(f"\n  Could not query traces: HTTP {response.status_code}")
            return

        data = response.json()
        traces = data.get("data", [])

        if not traces:
            print("\n  No traces found. Run an evaluation first.")
            return

        print("\n" + "=" * 60)
        print("RECENT LANGFUSE TRACES")
        print("=" * 60)

        total_cost = 0
        total_tokens = 0

        for trace in traces:
            trace_id = trace.get("id", "unknown")[:12]
            name = trace.get("name", "unnamed")
            latency = trace.get("latency")
            cost = trace.get("totalCost", 0) or 0
            input_tokens = trace.get("inputTokens", 0) or 0
            output_tokens = trace.get("outputTokens", 0) or 0

            total_cost += cost
            total_tokens += input_tokens + output_tokens

            latency_str = f"{latency:.2f}s" if latency else "N/A"
            print(f"\n  Trace: {trace_id}  Name: {name}")
            print(f"    Latency: {latency_str}  Cost: ${cost:.6f}")
            print(f"    Tokens:  {input_tokens} in / {output_tokens} out")

        print(f"\n{'─' * 60}")
        print(f"  Total cost:   ${total_cost:.6f}")
        print(f"  Total tokens: {total_tokens}")

    except requests.ConnectionError:
        print("\n  Could not connect to Langfuse API.")


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Agent Ops — Langfuse Observability Integration")
    print(f"Langfuse URL: {LANGFUSE_BASE_URL}\n")

    # Step 1: Health check
    print("=" * 60)
    print("LANGFUSE STATUS")
    print("=" * 60)
    langfuse_available = check_langfuse_health()

    if langfuse_available:
        # Step 2: Configure model pricing
        print("\n" + "=" * 60)
        print("MODEL PRICING CONFIGURATION")
        print("=" * 60)
        configure_model_pricing()

        # Step 3: Run evaluation with Langfuse
        print("\n" + "=" * 60)
        print("RUNNING EVALUATION WITH TRACING")
        print("=" * 60)
        run_evaluation_with_langfuse(BENCHMARK_DIR, OUTPUT_DIR)
    else:
        print("\n  WARNING: Langfuse is not available. Skipping observability features.")
        print("  To enable: orchestrate server start -e .env -l")
        print("  Evaluation can still be run without Langfuse using 01_agent_evaluation.py.")

    # Step 4: Query traces
    query_langfuse_traces()

    print(f"\n  Dashboard: {LANGFUSE_BASE_URL}")
    print(f"  Login: orchestrate@ibm.com / <password from server start output>")
