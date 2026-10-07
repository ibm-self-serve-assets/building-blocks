#!/usr/bin/env bash
# =============================================================================
# build.sh — Build and push the sql-executor image to IBM Cloud ICR
#
# Prerequisites:
#   ibmcloud cli     : https://cloud.ibm.com/docs/cli
#   container-registry plugin : ibmcloud plugin install container-registry
#   docker (or podman)
#
# Usage:
#   cd docker-build/backend/sql-executor
#   ./build.sh
#   ICR_NAMESPACE=mynamespace ./build.sh
# =============================================================================

set -euo pipefail

# ---- Configuration ----------------------------------------------------------
ICR_REGION="${ICR_REGION:-de.icr.io}"
ICR_NAMESPACE="${ICR_NAMESPACE:?Set ICR_NAMESPACE (your ICR namespace)}"
IMAGE_NAME="${IMAGE_NAME:-sql-executor}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
FULL_IMAGE="${ICR_REGION}/${ICR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_IMAGE="${ICR_REGION}/${ICR_NAMESPACE}/${IMAGE_NAME}:latest"
# -----------------------------------------------------------------------------

echo "▶ Building image: ${FULL_IMAGE}"

# ---- 1. Stage source files into the build context ---------------------------
# backend/sql_executor/ is the canonical module directory.
# requirements.txt is sourced from backend/sql_executor/ — no duplicate copy here.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXECUTOR_DIR="${SCRIPT_DIR}/../../../backend/sql_executor"

cp "${EXECUTOR_DIR}/tool_sql_executor.py" "${SCRIPT_DIR}/tool_sql_executor.py"
cp "${EXECUTOR_DIR}/sql_validation.py"    "${SCRIPT_DIR}/sql_validation.py"
cp "${EXECUTOR_DIR}/requirements.txt"     "${SCRIPT_DIR}/requirements.txt"
cp "${SCRIPT_DIR}/../../../ibmcloud-pg-ca.crt" "${SCRIPT_DIR}/ibmcloud-pg-ca.crt"

cleanup() {
    rm -f "${SCRIPT_DIR}/tool_sql_executor.py"
    rm -f "${SCRIPT_DIR}/sql_validation.py"
    rm -f "${SCRIPT_DIR}/requirements.txt"
    rm -f "${SCRIPT_DIR}/ibmcloud-pg-ca.crt"
}
trap cleanup EXIT

# ---- 2. Detect container engine & Build -------------------------------------
if command -v podman &>/dev/null; then
    CONTAINER_CLIENT="podman"
elif command -v docker &>/dev/null; then
    CONTAINER_CLIENT="docker"
else
    echo "❌ ERROR: Neither podman nor docker found in PATH." >&2
    exit 1
fi
echo "▶ Using container client: ${CONTAINER_CLIENT}"

echo "▶ Running build on ${CONTAINER_CLIENT}..."
${CONTAINER_CLIENT} build \
    --platform linux/amd64 \
    --label "git-commit=${IMAGE_TAG}" \
    --label "build-date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -t "${FULL_IMAGE}" \
    -t "${LATEST_IMAGE}" \
    "${SCRIPT_DIR}"

# ---- 3. Push to ICR ---------------------------------------------------------
echo "▶ Logging in to IBM Cloud Container Registry (${ICR_REGION}) using ${CONTAINER_CLIENT}"
ibmcloud cr login --client "${CONTAINER_CLIENT}"

echo "▶ Pushing ${FULL_IMAGE}"
${CONTAINER_CLIENT} push "${FULL_IMAGE}"
${CONTAINER_CLIENT} push "${LATEST_IMAGE}"

echo "✅ Done: ${FULL_IMAGE}"
echo "   Update ce-app.yaml image field to: ${FULL_IMAGE}"
