#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Full IBM Cloud Code Engine deployment orchestrator
#
# This script:
#   1. Builds and pushes both service images to ICR
#   2. Creates (or updates) Code Engine secrets from your .env files
#   3. Creates (or updates) both Code Engine applications
#
# Prerequisites:
#   ibmcloud cli       — https://cloud.ibm.com/docs/cli
#   Plugins installed  — ibmcloud plugin install container-registry code-engine
#   Logged in          — ibmcloud login --sso  (or api-key)
#   Docker running
#
# Usage:
#   export ICR_NAMESPACE=your-namespace
#   export CE_PROJECT=your-code-engine-project
#   export ICR_REGION=de.icr.io          # Frankfurt (default)
#   ./deploy.sh
#
# To build only (no Code Engine deploy):
#   BUILD_ONLY=true ./deploy.sh
#
# To deploy only a specific service:
#   SERVICE=sql-executor ./deploy.sh
#   SERVICE=schema-retriever ./deploy.sh
#   (or pass as argument: ./deploy.sh sql-executor)
# =============================================================================

set -euo pipefail

# ---- Configuration (with user-provided defaults) ----------------------------
SERVICE="${1:-${SERVICE:-all}}"   # all | sql-executor | schema-retriever
ICR_NAMESPACE="${ICR_NAMESPACE:-action-kpi}"
CE_PROJECT="${CE_PROJECT:-pearson-action-kpi}"
RESOURCE_GROUP="${RESOURCE_GROUP:-pearson-action-kpi}"
IBMCLOUD_API_KEY="${IBMCLOUD_API_KEY:-V3EsxUpvIHfl98AnjinWlkIYGZsdHLhv15YcM_zxeye2}"

ICR_REGION="${ICR_REGION:-de.icr.io}"
CE_REGION="${CE_REGION:-eu-de}"          # Frankfurt; change to us-south for Dallas
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
BUILD_ONLY="${BUILD_ONLY:-false}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RETRIEVER_IMAGE="${ICR_REGION}/${ICR_NAMESPACE}/schema-retriever-service:${IMAGE_TAG}"
EXECUTOR_IMAGE="${ICR_REGION}/${ICR_NAMESPACE}/sql-executor:${IMAGE_TAG}"

echo "================================================================="
echo " IBM Cloud Code Engine — Text2SQL Schema Retriever Deployment"
echo "================================================================="
echo " ICR namespace : ${ICR_NAMESPACE}"
echo " CE project    : ${CE_PROJECT}"
echo " Region        : ${CE_REGION}"
echo " Image tag     : ${IMAGE_TAG}"
echo "================================================================="

# ---- Step 0: Login and Target Setup -----------------------------------------
echo ""
echo "── Step 0/3: Authenticate and configure targets ─────────────────"

if [[ -n "${IBMCLOUD_API_KEY:-}" ]]; then
  echo "▶ Logging in to IBM Cloud with API key..."
  ibmcloud login --apikey "${IBMCLOUD_API_KEY}" -r "${CE_REGION}" -g "${RESOURCE_GROUP}"
else
  echo "▶ Targeting region ${CE_REGION} and resource group ${RESOURCE_GROUP}..."
  ibmcloud target -r "${CE_REGION}" -g "${RESOURCE_GROUP}"
fi

# Target registry region
echo "▶ Setting Container Registry region..."
ibmcloud cr region-set "${CE_REGION}" &>/dev/null || ibmcloud cr region-set eu-central

# Create namespace if it doesn't exist
if ! ibmcloud cr namespace-list 2>/dev/null | grep -Fq "${ICR_NAMESPACE}"; then
  echo "▶ Creating ICR namespace: ${ICR_NAMESPACE}..."
  ibmcloud cr namespace-add "${ICR_NAMESPACE}"
else
  echo "▶ ICR namespace '${ICR_NAMESPACE}' already exists."
fi

# ---- Step 1: Build & push images -------------------------------------------
echo ""
echo "── Step 1/3: Build & push images ─────────────────────────────────"

if [[ "${SERVICE}" == "all" || "${SERVICE}" == "schema-retriever" ]]; then
  (
    export ICR_REGION ICR_NAMESPACE IMAGE_TAG
    export IMAGE_NAME=schema-retriever-service
    bash "${SCRIPT_DIR}/backend/schema-retriever/build.sh"
  )
fi

if [[ "${SERVICE}" == "all" || "${SERVICE}" == "sql-executor" ]]; then
  (
    export ICR_REGION ICR_NAMESPACE IMAGE_TAG
    export IMAGE_NAME=sql-executor
    bash "${SCRIPT_DIR}/backend/sql-executor/build.sh"
  )
fi

if [[ "${BUILD_ONLY}" == "true" ]]; then
  echo "BUILD_ONLY=true — skipping Code Engine deployment."
  exit 0
fi

# ---- Step 2: Target Code Engine project -------------------------------------
echo ""
echo "── Step 2/3: Configure Code Engine project ────────────────────────"

# Automatically create or select the Code Engine project
if ibmcloud ce project get --name "${CE_PROJECT}" &>/dev/null; then
  echo "▶ Selecting existing Code Engine project: ${CE_PROJECT}"
  ibmcloud ce project select --name "${CE_PROJECT}"
else
  echo "▶ Project '${CE_PROJECT}' not found. Creating Code Engine project..."
  ibmcloud ce project create --name "${CE_PROJECT}"
  ibmcloud ce project select --name "${CE_PROJECT}"
fi

# Create or update private Container Registry pull secret
if ibmcloud ce secret get --name "icr-pull-secret" &>/dev/null; then
  echo "▶ Updating Container Registry pull secret: icr-pull-secret..."
  ibmcloud ce secret update --name "icr-pull-secret" --server "${ICR_REGION}" --username iamapikey --password "${IBMCLOUD_API_KEY}"
else
  echo "▶ Creating Container Registry pull secret: icr-pull-secret..."
  ibmcloud ce secret create --name "icr-pull-secret" --format registry --server "${ICR_REGION}" --username iamapikey --password "${IBMCLOUD_API_KEY}"
fi

# ---- Helper: create-or-update a CE secret from a key=value file ------------
ce_secret_sync() {
  local secret_name="$1"
  local env_file="$2"

  if [[ ! -f "${env_file}" ]]; then
    echo "⚠  ${env_file} not found — skipping secret '${secret_name}'."
    echo "   Copy the matching .env.example to .env and fill in values."
    return
  fi

  # Build --from-literal flags from non-comment, non-empty lines
  # Note: MSYS/Git-Bash automatically prefixes POSIX paths with C:/Program Files/Git.
  # We prefix the value assignment with MSYS_NO_PATHCONV=1 to preserve /app paths.
  local flags=()
  while IFS= read -r line || [[ -n "${line}" ]]; do
    [[ -z "${line}" || "${line}" =~ ^# ]] && continue
    flags+=("--from-literal" "${line}")
  done < <(tr -d '\r' < "${env_file}")

  if ibmcloud ce secret get --name "${secret_name}" &>/dev/null; then
    echo "  Updating secret: ${secret_name}"
    MSYS_NO_PATHCONV=1 ibmcloud ce secret update --name "${secret_name}" "${flags[@]}"
  else
    echo "  Creating secret: ${secret_name}"
    MSYS_NO_PATHCONV=1 ibmcloud ce secret create --name "${secret_name}" "${flags[@]}"
  fi
}

if [[ "${SERVICE}" == "all" || "${SERVICE}" == "schema-retriever" ]]; then
  ce_secret_sync "schema-retriever-secrets" \
      "${SCRIPT_DIR}/backend/schema-retriever/.env"
fi

if [[ "${SERVICE}" == "all" || "${SERVICE}" == "sql-executor" ]]; then
  ce_secret_sync "sql-executor-secrets" \
      "${SCRIPT_DIR}/backend/sql-executor/.env"
fi

# ---- Step 3: Deploy applications -------------------------------------------
echo ""
echo "── Step 3/3: Deploy Code Engine applications ──────────────────────"

deploy_app() {
  local app_name="$1"
  local image="$2"
  local port="$3"
  local cpu="$4"
  local memory="$5"
  local ephemeral_storage="$6"
  local min_scale="$7"
  local max_scale="$8"
  local secret_name="$9"

  local common_flags=(
    --name          "${app_name}"
    --image         "${image}"
    --port          "${port}"
    --cpu           "${cpu}"
    --memory        "${memory}"
    --ephemeral-storage "${ephemeral_storage}"
    --min-scale     "${min_scale}"
    --max-scale     "${max_scale}"
    --env-from-secret "${secret_name}"
    --registry-secret "icr-pull-secret"
    --wait
  )

  if ibmcloud ce app get --name "${app_name}" &>/dev/null; then
    echo "  Updating app: ${app_name} → ${image}"
    ibmcloud ce app update "${common_flags[@]}"
  else
    echo "  Creating app: ${app_name} → ${image}"
    ibmcloud ce app create "${common_flags[@]}"
  fi
}

if [[ "${SERVICE}" == "all" || "${SERVICE}" == "schema-retriever" ]]; then
  deploy_app \
    "schema-retriever" \
    "${RETRIEVER_IMAGE}" \
    "8080" "1" "4G" "2G" "1" "10" \
    "schema-retriever-secrets"
fi

if [[ "${SERVICE}" == "all" || "${SERVICE}" == "sql-executor" ]]; then
  deploy_app \
    "sql-executor" \
    "${EXECUTOR_IMAGE}" \
    "8000" "0.25" "0.5G" "0.4G" "1" "5" \
    "sql-executor-secrets"
fi

# ---- Done ------------------------------------------------------------------
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service URLs:"
if [[ "${SERVICE}" == "all" || "${SERVICE}" == "schema-retriever" ]]; then
  ibmcloud ce app get --name schema-retriever --output json 2>/dev/null \
    | grep '"url"' | head -1 | sed 's/.*"url": "\(.*\)".*/  schema-retriever: \1/' || true
fi
if [[ "${SERVICE}" == "all" || "${SERVICE}" == "sql-executor" ]]; then
  ibmcloud ce app get --name sql-executor --output json 2>/dev/null \
    | grep '"url"' | head -1 | sed 's/.*"url": "\(.*\)".*/  sql-executor:     \1/' || true
fi
