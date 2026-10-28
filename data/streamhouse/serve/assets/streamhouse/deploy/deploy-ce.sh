#!/usr/bin/env bash
# ------------------------------------------------------------
# FactoryPulse Streamhouse – IBM Cloud Code Engine deploy
# Required environment variables (export before running):
#   REGION          IBM Cloud region, e.g. eu-de
#   RESOURCE_GROUP  IBM Cloud resource group
#   ICR_IMAGE       Image repo without tag, e.g. <region>.icr.io/<namespace>/streamhouse-factory-pulse
# Optional: CE_PROJECT (default streamhouse), CE_APP_NAME (default streamhouse-factory-pulse)
# Secrets:        created from the repo-root .env file
# ------------------------------------------------------------
set -euo pipefail

# Always resolve paths relative to the repo root (one level up from deploy/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CE_APP_NAME="${CE_APP_NAME:-streamhouse-factory-pulse}"
SECRET_NAME="${SECRET_NAME:-streamhouse-secrets}"
ICR_IMAGE="${ICR_IMAGE:?Set ICR_IMAGE, e.g. <region>.icr.io/<namespace>/streamhouse-factory-pulse}"   # repo, no tag
MIN_SCALE="${MIN_SCALE:-1}"
MAX_SCALE="${MAX_SCALE:-1}"
RESOURCE_GROUP="${RESOURCE_GROUP:?Set RESOURCE_GROUP to your IBM Cloud resource group}"
CE_PROJECT="${CE_PROJECT:-streamhouse}"
REGION="${REGION:?Set REGION to your IBM Cloud region, e.g. eu-de}"
APP_PORT="${APP_PORT:-8080}"   # must match EXPOSE / PORT in deploy/Dockerfile

ENV_FILE="$REPO_ROOT/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Create .env from .env.example first (expected at: $ENV_FILE)"
  exit 1
fi

# Strip a UTF-8 BOM if present (common when the file is created on Windows).
sed -i 's/^\xEF\xBB\xBF//' "$ENV_FILE" 2>/dev/null || true

# Load .env so API_KEY and the checks below are available. Keep .env out of version control.
set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

required=(KAFKA_BOOTSTRAP_SERVERS KAFKA_API_KEY KAFKA_API_SECRET)
for key in "${required[@]}"; do
  if [[ -z "${!key:-}" ]]; then
    echo "Missing required variable in .env: $key"
    exit 1
  fi
done

# ------------------------------------------------------------
# IBM Cloud login – API_KEY from .env is the IBM Cloud API key
# ------------------------------------------------------------
IBM_CLOUD_API_KEY="${API_KEY:-${IBM_CLOUD_API_KEY:-}}"
if [[ -z "$IBM_CLOUD_API_KEY" ]]; then
  echo "ERROR: Set API_KEY in .env to authenticate with IBM Cloud."
  exit 1
fi

echo "==> Logging in to IBM Cloud (api-key, region=$REGION)"
ibmcloud login --apikey "$IBM_CLOUD_API_KEY" -r "$REGION" -g "$RESOURCE_GROUP" -q

# ------------------------------------------------------------
# Code Engine project – create if it does not exist
# ------------------------------------------------------------
if ibmcloud ce project get --name "$CE_PROJECT" >/dev/null 2>&1; then
  echo "==> Code Engine project '$CE_PROJECT' already exists – selecting"
  ibmcloud ce project select --name "$CE_PROJECT"
else
  echo "==> Code Engine project '$CE_PROJECT' not found – creating"
  ibmcloud ce project create --name "$CE_PROJECT"
  # Wait until the project becomes active before proceeding
  echo "==> Waiting for project to become active..."
  for i in $(seq 1 18); do
    STATUS=$(ibmcloud ce project get --name "$CE_PROJECT" --output json 2>/dev/null \
             | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "unknown")
    echo "    attempt $i/18 – status: $STATUS"
    if [[ "$STATUS" == "active" ]]; then break; fi
    sleep 10
  done
  ibmcloud ce project select --name "$CE_PROJECT"
fi

# ------------------------------------------------------------
# Container Registry – ensure ICR namespace exists and
# a registry secret is available in the CE project
# ------------------------------------------------------------
ICR_REGISTRY="${ICR_IMAGE%%/*}"          # <region>.icr.io
ICR_NAMESPACE="${ICR_IMAGE#*/}"          # <namespace>/...
ICR_NAMESPACE="${ICR_NAMESPACE%%/*}"     # <namespace>

echo "==> Ensuring ICR namespace '$ICR_NAMESPACE' exists in $ICR_REGISTRY"
ibmcloud plugin install container-registry -f -q 2>/dev/null || true
# cr region-set takes a short name like "eu-de" not the full hostname
ibmcloud cr region-set "$REGION" 2>/dev/null || true
if ! ibmcloud cr namespace-list 2>/dev/null | grep -q "$ICR_NAMESPACE"; then
  echo "    Creating ICR namespace '$ICR_NAMESPACE'"
  ibmcloud cr namespace-add "$ICR_NAMESPACE"
else
  echo "    ICR namespace '$ICR_NAMESPACE' already exists"
fi

ICR_SECRET_NAME="${ICR_SECRET_NAME:-icr-secret}"
if ibmcloud ce registry get --name "$ICR_SECRET_NAME" >/dev/null 2>&1; then
  echo "==> Registry secret '$ICR_SECRET_NAME' already exists – skipping"
else
  echo "==> Creating registry secret '$ICR_SECRET_NAME' for $ICR_REGISTRY"
  ibmcloud ce registry create \
    --name "$ICR_SECRET_NAME" \
    --server "$ICR_REGISTRY" \
    --username iamapikey \
    --password "$IBM_CLOUD_API_KEY"
fi

# ------------------------------------------------------------
# App secret – created from .env
# Filtered copy: drops comments, blank lines, empty values, CRs,
# and PORT (reserved by Code Engine) / API_KEY (deploy credential only).
# ------------------------------------------------------------
SECRET_ENV_FILE="$(mktemp)"
trap 'rm -f "$SECRET_ENV_FILE"' EXIT
tr -d '\r' < "$ENV_FILE" \
  | grep -E '^[A-Za-z_][A-Za-z0-9_]*=.+' \
  | grep -vE '^(PORT|API_KEY)=' > "$SECRET_ENV_FILE"

echo "==> Creating secret '$SECRET_NAME' from .env ($(wc -l < "$SECRET_ENV_FILE") variables)"
ibmcloud ce secret delete --name "$SECRET_NAME" --force >/dev/null 2>&1 || true
ibmcloud ce secret create --name "$SECRET_NAME" --from-env-file "$SECRET_ENV_FILE"

# ------------------------------------------------------------
# Image – build locally, then push to ICR
# ------------------------------------------------------------
ENGINE="${CONTAINER_ENGINE:-podman}"
command -v "$ENGINE" >/dev/null 2>&1 || { echo "ERROR: $ENGINE not found (set CONTAINER_ENGINE=docker to use docker)."; exit 1; }

IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d%H%M%S)}"
IMAGE_REF="$ICR_IMAGE:$IMAGE_TAG"

# VITE_* values are public and baked into the frontend bundle at build time.
echo "==> Building image locally with $ENGINE: $IMAGE_REF"
"$ENGINE" build --platform linux/amd64 -t "$IMAGE_REF" -t "$ICR_IMAGE:latest" -f "$REPO_ROOT/deploy/Dockerfile" \
  --build-arg "VITE_GOOGLE_MAPS_API_KEY=${VITE_GOOGLE_MAPS_API_KEY:-}" \
  --build-arg "VITE_GOOGLE_MAPS_MAP_ID=${VITE_GOOGLE_MAPS_MAP_ID:-}" \
  "$REPO_ROOT"

echo "==> Pushing image to $ICR_REGISTRY"
printf '%s' "$IBM_CLOUD_API_KEY" | "$ENGINE" login "$ICR_REGISTRY" --username iamapikey --password-stdin
"$ENGINE" push "$IMAGE_REF"
"$ENGINE" push "$ICR_IMAGE:latest"

# ------------------------------------------------------------
# Application – create on first run, otherwise roll out a new
# revision. The unique image tag forces a new revision, which
# also picks up the freshly recreated secret.
# ------------------------------------------------------------
if ibmcloud ce application get --name "$CE_APP_NAME" >/dev/null 2>&1; then
  ACTION=update
else
  ACTION=create
fi

echo "==> Running 'application $ACTION' for '$CE_APP_NAME' with $IMAGE_REF"
ibmcloud ce application "$ACTION" \
  --name "$CE_APP_NAME" \
  --image "$IMAGE_REF" \
  --registry-secret "$ICR_SECRET_NAME" \
  --port "$APP_PORT" \
  --min-scale "$MIN_SCALE" \
  --max-scale "$MAX_SCALE" \
  --cpu 1 \
  --memory 2G \
  --env-from-secret "$SECRET_NAME"

echo ""
ibmcloud ce application get --name "$CE_APP_NAME"
