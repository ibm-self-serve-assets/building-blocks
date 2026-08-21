#!/usr/bin/env bash
# apply-controls.sh — Apply all Domain 5 control resource files to a deployment
#
# Usage:
#   bash apply-controls.sh <agent-display-name> <tool-name> <model-name>
#
# Example:
#   bash apply-controls.sh "test_DA" "my-db-tool" "gpt-4o"
#
# Requirements:
#   - venv activated with ibm-watsonx-orchestrate==2.15.0
#   - Active env: orchestrate env activate ibm_cloud (or your env)

set -euo pipefail

AGENT_NAME="${1:-test_DA}"
TOOL_NAME="${2:-my-db-tool}"
MODEL_NAME="${3:-gpt-4o}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  Controls Deployment"
echo "========================================"
echo "  Agent  : $AGENT_NAME"
echo "  Tool   : $TOOL_NAME"
echo "  Model  : $MODEL_NAME"
echo "========================================"

# Validate orchestrate CLI version
ADK_VERSION=$(orchestrate --version 2>&1 | grep "ADK Version" | awk '{print $3}')
echo ""
echo "[check] ADK Version: $ADK_VERSION"
if [[ "$ADK_VERSION" != "2.15.0" ]]; then
  echo "[warn]  Expected ADK 2.15.0 — found $ADK_VERSION. Proceeding anyway."
fi

# Create temp copies with substituted names
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

echo ""
echo "[step 1] Applying PII filter (agent: $AGENT_NAME)..."
sed "s/- my-agent/- \"$AGENT_NAME\"/g" \
  "$SCRIPT_DIR/pii-filter.yaml" > "$TMP_DIR/pii-filter.yaml"
orchestrate controls import -f "$TMP_DIR/pii-filter.yaml"
echo "         ✓ pii_filter_guard"

echo ""
echo "[step 2] Applying content guardrails (agent: $AGENT_NAME)..."
sed "s/- my-agent/- \"$AGENT_NAME\"/g" \
  "$SCRIPT_DIR/content-guardrails.yaml" > "$TMP_DIR/content-guardrails.yaml"
orchestrate controls import -f "$TMP_DIR/content-guardrails.yaml"
echo "         ✓ content_guardrails"

echo ""
echo "[step 3] Applying SQL sanitizer (tool: $TOOL_NAME)..."
sed "s/- my-db-tool/- \"$TOOL_NAME\"/g" \
  "$SCRIPT_DIR/sql-sanitizer.yaml" > "$TMP_DIR/sql-sanitizer.yaml"
orchestrate controls import -f "$TMP_DIR/sql-sanitizer.yaml"
echo "         ✓ sql_injection_guard"

echo ""
echo "[step 4] Applying model resilience (model: $MODEL_NAME)..."
sed "s/- gpt-4o/- \"$MODEL_NAME\"/g" \
  "$SCRIPT_DIR/model-resilience.yaml" > "$TMP_DIR/model-resilience.yaml"
orchestrate controls import -f "$TMP_DIR/model-resilience.yaml"
echo "         ✓ primary_model_fallback"

echo ""
echo "========================================"
echo "  Deployment complete"
echo "========================================"
echo ""

# Final status
orchestrate controls list
echo ""
orchestrate controls count
