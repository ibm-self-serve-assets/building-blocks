#!/bin/bash

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtual environment directory
mkdir -p uv.venv
cd uv.venv

# Check if virtual environment already exists
if [ -d "ai-agent-builder" ]; then
    echo "Virtual environment 'ai-agent-builder' already exists. Skipping creation."
else
    echo "Creating virtual environment 'ai-agent-builder'..."
    uv venv ai-agent-builder
fi

# Activate the environment
source ai-agent-builder/bin/activate

# Install the package
echo "Installing ibm-watsonx-orchestrate..."
uv pip install ibm-watsonx-orchestrate

# Add virtual environment bin to PATH
VENV_BIN_PATH="$(pwd)/ai-agent-builder/bin"
if [[ ":$PATH:" != *":$VENV_BIN_PATH:"* ]]; then
    export PATH="$VENV_BIN_PATH:$PATH"
    echo "Added $VENV_BIN_PATH to PATH"
fi

# Verify installation
orchestrate --help

echo ""
echo "Setup complete!"
echo "Virtual environment created at: uv.venv/ai-agent-builder"
echo "Virtual environment bin added to PATH: $VENV_BIN_PATH"
echo "To activate in the future, run: source uv.venv/ai-agent-builder/bin/activate"
echo "Or add to your PATH: export PATH=\"$VENV_BIN_PATH:\$PATH\""
