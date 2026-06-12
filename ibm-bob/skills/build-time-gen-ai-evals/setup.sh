#!/usr/bin/env bash
set -euo pipefail

# build-time-gen-ai-evals setup script.
#
# Creates a Python 3.11 venv, runs a `pip install --dry-run` pre-flight to
# surface any dependency conflicts BEFORE committing the install, then
# installs `ibm-watsonx-gov` with the metrics + agentic + tools + llmaj
# extras. After this, partners use the SDK directly from Python — no MCP
# server, no Code Engine dependency.
#
# Why a dedicated venv: this skill's SDK pulls a large slice of the LLM
# ecosystem (langchain-openai, google-genai, watsonx-ai, etc.) via the
# [llmaj] extra. Installing it into an existing project venv that has older
# pinned versions of pydantic or httpx will raise ResolutionImpossible.
# A dedicated venv eliminates that whole class of failure.
#
# Overrides:
#   VENV_DIR=/path/to/venv      default: $HOME/gen-ai-evals-venv
#   PYTHON_BIN=python3.12       default: python3.11

VENV_DIR="${VENV_DIR:-$HOME/gen-ai-evals-venv}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

# The bound spec partners install. [metrics,agentic,tools,llmaj] gives the
# full surface: deterministic RAG metrics + agentic tool-call metrics +
# tool catalog + LLM-as-judge metrics (including custom-judge authoring).
SDK_SPEC=(
    "ibm-watsonx-gov[metrics,agentic,tools,llmaj]>=1.4.0,<2.0.0"
    "ibm_watsonx_ai>=1.3.13,<2.0.0"
    "pydantic>=2.10.3,<3.0.0"
    "httpx>=0.28.1,<0.29"
    "pandas>=2.2,<3.0"
    "python-dotenv>=1.0"
)

# --- 1. Python check ------------------------------------------------------
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "ERROR: $PYTHON_BIN not found."
    echo "  Install Python 3.11, 3.12, or 3.13 via pyenv or your system package manager."
    echo "  Why this range: ibm-watsonx-gov 1.4.x supports 3.11-3.13. 3.14+ is not yet"
    echo "  supported (the SDK chain has C-extension wheels for 3.11-3.13 only)."
    exit 1
fi

# --- 2. venv -------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv at $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    echo "Venv at $VENV_DIR already exists. Skipping creation."
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip

# --- 3. Pre-flight dependency resolution ---------------------------------
# Run pip's full SAT solver without installing. Catches conflicts in ~30s-2min.
echo ""
echo "Pre-flight: dry-run resolution check (no packages installed)..."
echo ""
if pip install --dry-run "${SDK_SPEC[@]}" >/tmp/gen-ai-evals-dryrun.log 2>&1; then
    echo "  OK - resolution is clean."
else
    echo ""
    echo "ResolutionImpossible detected. Last 30 lines of pip output:"
    echo "----------------------------------------"
    tail -30 /tmp/gen-ai-evals-dryrun.log
    echo "----------------------------------------"
    echo ""
    echo "Today's known conflict floors (re-check quarterly with this script):"
    echo "  pydantic >= 2.10.3, < 3.0.0   (ibm-watsonx-gov 1.4.x floor)"
    echo "  httpx    >= 0.28.1, < 0.29    (google-genai floor / ibm-watsonx-ai ceiling)"
    echo ""
    echo "If pip reports a conflict on pydantic or httpx, your venv has a stricter pin"
    echo "than the SDK can accept. Easiest fix: use a dedicated venv (this script's"
    echo "default), OR relax those pins in your existing project's requirements.txt."
    echo ""
    echo "Full pip output saved to: /tmp/gen-ai-evals-dryrun.log"
    exit 2
fi

# --- 4. Real install -----------------------------------------------------
echo ""
echo "Installing ibm-watsonx-gov[metrics,agentic,tools,llmaj]..."
pip install --quiet "${SDK_SPEC[@]}"

echo ""
echo "Installed versions:"
pip show ibm-watsonx-gov ibm-watsonx-ai pydantic httpx 2>/dev/null | \
    grep -E "^(Name|Version):"

cat <<EOF

Setup complete!

Next steps:
  1. Activate the venv in any new shell:
       source $VENV_DIR/bin/activate

  2. Set credentials in your shell (or in a .env file at your project root):
       export WATSONX_APIKEY=<from IBM Cloud > Manage > Access (IAM) > API keys>
       export WATSONX_PROJECT_ID=<from watsonx.ai console > project > Manage tab>
       # OR if you use a deployment space:
       export WATSONX_SPACE_ID=<from watsonx.ai console > deployments > your space>

     The WATSONX_PROJECT_ID (or WATSONX_SPACE_ID) is required for LLM-as-judge
     metrics. The watsonx project/space must be associated with a Watson Machine
     Learning instance.

  3. Sanity test:
       python3 -c "import ibm_watsonx_gov.metrics as m; \\
                   print('OK -', sum(1 for n in dir(m) if n.endswith('Metric')), \\
                         'metric classes available')"
     Expected: "OK - 20+ metric classes available".

  4. Open Bob in your project root and ask:
       "Evaluate my RAG pipeline before I deploy it."
     Bob will load the skill and walk you through the 5-phase workflow:
     understand the app, prepare data, plan evaluation, run, interpret.

For full setup details (IBM Cloud provisioning, dependency conflict troubleshooting,
data format examples, metrics reference), see USAGE-GUIDE.md and assets/PREREQUISITES.md.
EOF
