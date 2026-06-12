#!/usr/bin/env bash
set -euo pipefail

# agent-ops setup script
# Creates a Python 3.12 venv, installs the WXO ADK with the agentops extra
# (which pulls eval-framework 1.4+), installs uv (for the docs MCP), and
# prints next-step guidance for the VENV_ACTIVATE export and MCP wiring.

VENV_DIR="${VENV_DIR:-$HOME/agent-ops-venv}"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "ERROR: $PYTHON_BIN not found."
    echo "  Install Python 3.12 via pyenv ('pyenv install 3.12') or your system package manager."
    echo "  Why 3.12 specifically: eval-framework has C-extension wheels for 3.12 only;"
    echo "  3.11 may work, 3.13+ is not yet supported."
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv at $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    echo "Venv at $VENV_DIR already exists. Skipping creation."
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Installing ibm-watsonx-orchestrate[agentops]>=2.6.0,<3.0.0 (this also pulls eval-fw 1.4+)..."
pip install --upgrade pip
pip install "ibm-watsonx-orchestrate[agentops]>=2.6.0,<3.0.0"

echo "Installing uv (for the watsonx-orchestrate-adk-docs MCP server)..."
pip install uv

echo ""
echo "Installed versions:"
pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework 2>/dev/null | grep -E "^(Name|Version):"

cat <<EOF

Setup complete!

Next steps:
  1. Export VENV_ACTIVATE so the skill's emitted commands find your venv:
       echo 'export VENV_ACTIVATE=$VENV_DIR/bin/activate' >> ~/.zshrc
       source ~/.zshrc

  2. (Optional) Wire the WXO docs MCP server so Bob can search ADK docs live:
       cp .bob/skills/agent-ops/assets/mcp.json ./mcp.json
       # Restart Bob / your MCP client.

  3. Confirm the agent-ops skill is in your repo's .bob/skills/ directory.

  4. Open Bob in your agent's project root and ask:
       "Help me evaluate this watsonx Orchestrate agent."
     Bob will run the 3-question interview and walk you through the modules.

See assets/PREREQUISITES.md for the full prerequisites checklist (credentials,
Docker runtime, Lima VM, hardware, network egress).
EOF
