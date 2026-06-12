#!/usr/bin/env bash
set -euo pipefail

# real-time-guardrails setup script.
#
# Creates a Python 3.11 venv, clones the building-blocks repo (or uses an
# existing clone), runs a `pip install --dry-run` pre-flight to surface any
# dependency conflicts BEFORE committing the install, then installs the SDK
# from source in editable mode.
#
# Why a dedicated venv: this skill's SDK pulls a large slice of the LLM
# ecosystem (langchain-openai, google-genai, watsonx-ai, etc.) via the
# [llmaj] extra. Installing it into an existing project venv that has older
# pinned versions of pydantic or httpx will raise ResolutionImpossible.
# A dedicated venv eliminates that whole class of failure.
#
# Overrides:
#   VENV_DIR=/path/to/venv           default: $HOME/guardrails-venv
#   PYTHON_BIN=python3.12            default: python3.11
#   BB_REPO_DIR=/path/to/clone       default: $HOME/src/building-blocks
#   BB_REPO_URL=...                  default: https://github.com/ibm-self-serve-assets/building-blocks

VENV_DIR="${VENV_DIR:-$HOME/guardrails-venv}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
BB_REPO_DIR="${BB_REPO_DIR:-$HOME/src/building-blocks}"
BB_REPO_URL="${BB_REPO_URL:-https://github.com/ibm-self-serve-assets/building-blocks}"
SDK_SUBPATH="ai-trust/real-time-guardrails/assets/sdk"

# --- 1. Python check ------------------------------------------------------
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "ERROR: $PYTHON_BIN not found."
    echo "  Install Python 3.11, 3.12, or 3.13 via pyenv or your system package manager."
    echo "  Why this range: ibm-watsonx-gov 1.4.x supports 3.11-3.13. 3.14+ is not yet"
    echo "  supported (the SDK chain has C-extension wheels for 3.11-3.13 only)."
    exit 1
fi

# --- 2. building-blocks repo ---------------------------------------------
if [ ! -d "$BB_REPO_DIR/$SDK_SUBPATH" ]; then
    if [ -d "$BB_REPO_DIR" ]; then
        echo "ERROR: $BB_REPO_DIR exists but doesn't contain $SDK_SUBPATH."
        echo "  Either set BB_REPO_DIR to a building-blocks clone that has the guardrails SDK,"
        echo "  or remove $BB_REPO_DIR and let this script clone fresh."
        exit 1
    fi
    echo "Cloning building-blocks into $BB_REPO_DIR..."
    mkdir -p "$(dirname "$BB_REPO_DIR")"
    git clone --depth 1 "$BB_REPO_URL" "$BB_REPO_DIR"
fi
SDK_DIR="$BB_REPO_DIR/$SDK_SUBPATH"
echo "Using SDK source at $SDK_DIR"

# --- 3. venv -------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv at $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    echo "Venv at $VENV_DIR already exists. Skipping creation."
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip

# --- 4. Pre-flight dependency resolution ---------------------------------
# Run pip's full SAT solver against the SDK's deps WITHOUT installing.
# Surfaces ResolutionImpossible in ~30s-2min if the deployed bounds collide
# with anything already in this venv (or with each other). Catches the
# orbital-outfitter-class conflict pattern before we commit to an install.
echo ""
echo "Pre-flight: dry-run resolution check (no packages installed)..."
echo ""
if pip install --dry-run -e "$SDK_DIR[all]" >/tmp/guardrails-dryrun.log 2>&1; then
    echo "  OK - resolution is clean."
else
    echo ""
    echo "ResolutionImpossible detected. Last 30 lines of pip output:"
    echo "----------------------------------------"
    tail -30 /tmp/guardrails-dryrun.log
    echo "----------------------------------------"
    echo ""
    echo "Today's known conflict floors (re-check quarterly with this script):"
    echo "  pydantic >= 2.10.3, < 3.0.0   (ibm-watsonx-gov 1.4.x floor)"
    echo "  httpx    >= 0.28.1, < 0.29    (google-genai floor / ibm-watsonx-ai ceiling)"
    echo ""
    echo "If pip reports a conflict on pydantic or httpx, your venv has a stricter pin"
    echo "than the SDK can accept. Easiest fix: relax those pins in your project's"
    echo "requirements.txt, or use a dedicated venv (this script's default)."
    echo ""
    echo "Full pip output saved to: /tmp/guardrails-dryrun.log"
    exit 2
fi

# --- 5. Real install -----------------------------------------------------
echo ""
echo "Installing real-time-guardrails[all] from source (editable mode)..."
pip install --quiet -e "$SDK_DIR[all]"

echo ""
echo "Installed versions:"
pip show real-time-guardrails ibm-watsonx-gov ibm-watsonx-ai pydantic httpx 2>/dev/null | \
    grep -E "^(Name|Version):"

cat <<EOF

Setup complete!

Next steps:
  1. Activate the venv in any new shell:
       source $VENV_DIR/bin/activate

  2. Set credentials in a .env file at your project root:
       WATSONX_APIKEY=<from IBM Cloud > IAM > API keys>
       WXG_SERVICE_INSTANCE_ID=<from IBM Cloud > Resource list > watsonx.governance instance > GUID>
       WXG_PROJECT_ID=<optional; unlocks 3 LLM-as-judge metrics>
       chmod 600 .env

  3. Sanity test:
       python3 -c "from real_time_guardrails import GuardrailsEvaluator; \\
                   ev = GuardrailsEvaluator(); \\
                   print('metrics:', ev.list_metrics()['total'])"
     Expected: "metrics: 28" (or 25 if no WXG_PROJECT_ID).

  4. Open Bob in your project root and ask:
       "Help me add safety guardrails to this RAG agent before going to production."
     Bob will load the skill and drive the 5-phase workflow.

For full setup details (IBM Cloud provisioning, dependency conflict troubleshooting,
threshold tuning, deployment modes), see USAGE-GUIDE.md and reference/.
EOF
