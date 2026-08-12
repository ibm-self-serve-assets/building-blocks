#!/usr/bin/env bash
# =============================================================================
# ingest.sh — UDI Part 2: Trigger a new ingestion run (run as often as needed)
#
# Requires setup.sh to have been run first (udi_config.json must exist).
#
# Usage:
#   bash scripts/ingest.sh               # uses scripts/.env by default
#   bash scripts/ingest.sh /path/to/.env # uses a custom .env file
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-${SCRIPT_DIR}/.env}"
CONFIG_FILE="${UDI_CONFIG:-${SCRIPT_DIR}/udi_config.json}"

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

# ── Validate IBM_CLOUD_API_KEY ────────────────────────────────────────────────
if [[ -z "${IBM_CLOUD_API_KEY:-}" ]]; then
  echo "ERROR: IBM_CLOUD_API_KEY is not set in ${ENV_FILE}"
  exit 1
fi

# ── Check udi_config.json ─────────────────────────────────────────────────────
if [[ ! -f "${CONFIG_FILE}" ]]; then
  echo "ERROR: Config file not found at: ${CONFIG_FILE}"
  echo ""
  echo "Run setup first:"
  echo "  bash scripts/setup.sh"
  exit 1
fi

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install Python >= 3.12 from https://python.org"
  exit 1
fi

# ── Check dependencies ────────────────────────────────────────────────────────
if ! python3 -c "import udi" &>/dev/null 2>&1; then
  echo "Installing Python dependencies..."
  pip3 install -r "${SCRIPT_DIR}/requirements.txt"
fi

# ── Run ingestion ─────────────────────────────────────────────────────────────
echo ""
echo "======================================================================"
echo " UDI Ingest — Part 2 of 2"
echo "======================================================================"
python3 "${SCRIPT_DIR}/ingest.py"
