#!/usr/bin/env bash
set -euo pipefail

# agent-ops setup: Python 3.12 venv + watsonx Orchestrate ADK with the agentops extra
# (ADK >= 2.18 pulls evaluation framework 1.5.x). Prints next steps; installs nothing else.

VENV_DIR="${VENV_DIR:-$HOME/agent-ops-venv}"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"
ADK_SPEC="${ADK_SPEC:-ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "ERROR: $PYTHON_BIN not found. Install Python 3.12 (for example: pyenv install 3.12) or set PYTHON_BIN." >&2
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv at $VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    echo "Venv at $VENV_DIR already exists; reusing it"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Installing $ADK_SPEC"
pip install --upgrade pip
pip install "$ADK_SPEC"

echo
echo "Installed:"
pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework 2>/dev/null | grep -E "^(Name|Version):"

cat <<EOF

Setup complete.

Next steps:
  1. Make the venv available to the commands Bob emits:
       echo 'export VENV_ACTIVATE=$VENV_DIR/bin/activate' >> ~/.zshrc && source ~/.zshrc
  2. Point orchestrate at the instance where your agent is imported (see USAGE-GUIDE.md, step 4):
       orchestrate env add --name <env> --url <instance url>
       orchestrate env activate <env> --api-key "\$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"
  3. Optional: give Bob live ADK docs search:
       cp .bob/skills/agent-ops/assets/mcp.json ./mcp.json
  4. Open the agent project in Bob and ask: "Evaluate this watsonx Orchestrate agent."

See assets/PREREQUISITES.md for credentials, Developer Edition, and troubleshooting.
EOF
