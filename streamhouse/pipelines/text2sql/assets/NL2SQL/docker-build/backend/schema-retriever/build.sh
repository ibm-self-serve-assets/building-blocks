#!/usr/bin/env bash
# =============================================================================
# build.sh — Build and push the schema-retriever image to IBM Cloud ICR
#
# Prerequisites:
#   ibmcloud cli     : https://cloud.ibm.com/docs/cli
#   container-registry plugin : ibmcloud plugin install container-registry
#   docker (or podman)
#
# Usage:
#   cd docker-build/backend/schema-retriever
#   ./build.sh                          # uses defaults from environment
#   ICR_NAMESPACE=mynamespace ./build.sh
# =============================================================================

set -euo pipefail

# ---- Configuration (override via env vars) ----------------------------------
ICR_REGION="${ICR_REGION:-de.icr.io}"                   # Frankfurt; use us.icr.io for Dallas
ICR_NAMESPACE="${ICR_NAMESPACE:?Set ICR_NAMESPACE (your ICR namespace)}"
IMAGE_NAME="${IMAGE_NAME:-schema-retriever-service}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
FULL_IMAGE="${ICR_REGION}/${ICR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_IMAGE="${ICR_REGION}/${ICR_NAMESPACE}/${IMAGE_NAME}:latest"
# -----------------------------------------------------------------------------

echo "▶ Building image: ${FULL_IMAGE}"

# ---- 1. Stage source files into the build context ---------------------------
# backend/schema_retriever/ and embedding/ are the canonical module directories.
# requirements.txt is sourced from backend/schema_retriever/ — no duplicate copy here.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RETRIEVER_DIR="${SCRIPT_DIR}/../../../backend/schema_retriever"
EMBEDDING_DIR="${SCRIPT_DIR}/../../../embedding"

cp "${RETRIEVER_DIR}/schema_retriever.py"            "${SCRIPT_DIR}/schema_retriever.py"
cp "${RETRIEVER_DIR}/schema_retriever_opensearch.py" "${SCRIPT_DIR}/schema_retriever_opensearch.py"
cp "${RETRIEVER_DIR}/schema_retriever_pgvector.py"   "${SCRIPT_DIR}/schema_retriever_pgvector.py"
cp "${RETRIEVER_DIR}/reranker.py"                    "${SCRIPT_DIR}/reranker.py"
cp "${RETRIEVER_DIR}/requirements.txt"               "${SCRIPT_DIR}/requirements.txt"
cp "${EMBEDDING_DIR}/embedders.py"                   "${SCRIPT_DIR}/embedders.py"
cp -r "${EMBEDDING_DIR}/connectors"                  "${SCRIPT_DIR}/connectors"
cp "${SCRIPT_DIR}/../../../ibmcloud-pg-ca.crt"       "${SCRIPT_DIR}/ibmcloud-pg-ca.crt"

cleanup() {
    rm -f  "${SCRIPT_DIR}/schema_retriever.py"
    rm -f  "${SCRIPT_DIR}/schema_retriever_opensearch.py"
    rm -f  "${SCRIPT_DIR}/schema_retriever_pgvector.py"
    rm -f  "${SCRIPT_DIR}/reranker.py"
    rm -f  "${SCRIPT_DIR}/requirements.txt"
    rm -f  "${SCRIPT_DIR}/embedders.py"
    rm -rf "${SCRIPT_DIR}/connectors"
    rm -f  "${SCRIPT_DIR}/ibmcloud-pg-ca.crt"
}
trap cleanup EXIT   # always clean up, even on error

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

# ---- 3. Login to ICR and push -----------------------------------------------
echo "▶ Logging in to IBM Cloud Container Registry (${ICR_REGION}) using ${CONTAINER_CLIENT}"
ibmcloud cr login --client "${CONTAINER_CLIENT}"

echo "▶ Pushing ${FULL_IMAGE}"
${CONTAINER_CLIENT} push "${FULL_IMAGE}"
${CONTAINER_CLIENT} push "${LATEST_IMAGE}"

echo "✅ Done: ${FULL_IMAGE}"
echo "   Update ce-app.yaml image field to: ${FULL_IMAGE}"
