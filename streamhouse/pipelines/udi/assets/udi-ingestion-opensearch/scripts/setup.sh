#!/usr/bin/env bash
# =============================================================================
# setup.sh — UDI Part 1: Register connections and create the flow (run once)
#
# Usage:
#   bash scripts/setup.sh               # uses scripts/.env by default
#   bash scripts/setup.sh /path/to/.env # uses a custom .env file
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-${SCRIPT_DIR}/.env}"

# ── Load .env ─────────────────────────────────────────────────────────────────
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: .env file not found at: ${ENV_FILE}"
  echo ""
  echo "Create it from the template:"
  echo "  cp scripts/.env.example scripts/.env"
  echo "  # then fill in your values"
  exit 1
fi

echo "Loading environment from: ${ENV_FILE}"
set -a
# shellcheck source=/dev/null
source "${ENV_FILE}"
set +a

# ── Validate required variables ───────────────────────────────────────────────
REQUIRED_VARS=(
  IBM_CLOUD_API_KEY
  PROJECT_ID
  COS_BUCKET
  OPENSEARCH_HOST
  OPENSEARCH_USERNAME
  OPENSEARCH_PASSWORD
)

MISSING=()
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    MISSING+=("${var}")
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "ERROR: The following required variables are not set in ${ENV_FILE}:"
  for var in "${MISSING[@]}"; do
    echo "  - ${var}"
  done
  exit 1
fi

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install Python >= 3.12 from https://python.org"
  exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: ${PY_VERSION}"

# ── Check dependencies ────────────────────────────────────────────────────────
if ! python3 -c "import udi" &>/dev/null 2>&1; then
  echo "Installing Python dependencies..."
  python3 -m pip install -r "${SCRIPT_DIR}/requirements.txt"
fi

# ── Run setup ─────────────────────────────────────────────────────────────────
echo ""
echo "======================================================================"
echo " UDI Setup — Part 1 of 2"
echo "======================================================================"
python3 "${SCRIPT_DIR}/setup.py"
