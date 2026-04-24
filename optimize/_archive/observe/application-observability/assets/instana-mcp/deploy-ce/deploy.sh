#!/bin/bash
set -euo pipefail

############################################
# Helper Functions
############################################

error() {
  echo "ERROR: $1" >&2
  exit 1
}

info() {
  echo "$1"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || error "$1 CLI not found."
}

############################################
# Preconditions
############################################

require_command ibmcloud
require_command grep
require_command awk
require_command sed

############################################
# Input Handling
############################################

INPUT_FILE="${1:-input.properties}"

[ ! -f "$INPUT_FILE" ] && error "Input file not found: $INPUT_FILE"

info "Loading configuration from $INPUT_FILE"

# shellcheck disable=SC1090
source "$INPUT_FILE"

############################################
# Validate Required Inputs
############################################

: "${LOCATION:?LOCATION missing}"
: "${PROJECT_NAME:?PROJECT_NAME missing}"
: "${IMAGE_REF:?IMAGE_REF missing}"

RESOURCE_GROUP="${RESOURCE_GROUP:-default}"

: "${INSTANA_API_TOKEN:?INSTANA_API_TOKEN missing}"
: "${INSTANA_BASE_URL:?INSTANA_BASE_URL missing}"
: "${IBM_CLOUD_API_KEY:?IBM_CLOUD_API_KEY missing}"

############################################
# IBM Cloud Session Validation
############################################

info "Validating IBM Cloud session..."

ibmcloud target >/dev/null 2>&1 \
  || error "Not logged in. Run: ibmcloud login"

############################################
# Code Engine Plugin Validation
############################################

if ! ibmcloud plugin list 2>/dev/null | grep -q code-engine; then
  info "Installing Code Engine plugin..."
  ibmcloud plugin install code-engine -f >/dev/null
fi

############################################
# Target Region & Resource Group
############################################

info "Targeting region → $LOCATION"
ibmcloud target -r "$LOCATION" >/dev/null

info "Targeting resource group → $RESOURCE_GROUP"
ibmcloud target -g "$RESOURCE_GROUP" >/dev/null

############################################
# Code Engine Project Handling
############################################

info "Checking Code Engine project..."

if ibmcloud ce project get --name "$PROJECT_NAME" >/dev/null 2>&1; then
    info "Project exists → $PROJECT_NAME"
else
    info "Project missing → creating"
    ibmcloud ce project create --name "$PROJECT_NAME" >/dev/null \
        || error "Project creation failed (quota/permissions)"
fi

info "Selecting project → $PROJECT_NAME"

ibmcloud ce project select --name "$PROJECT_NAME" >/dev/null \
    || error "Project selection failed"

############################################
# Registry Secret Handling
############################################

SECRET_NAME="instana-mcp"

info "Checking registry secret..."

if ibmcloud ce secret get --name "$SECRET_NAME" >/dev/null 2>&1; then
    info "Secret exists → updating"
    ibmcloud ce secret update \
        --name "$SECRET_NAME" \
        --username iamapikey \
        --password "$IBM_CLOUD_API_KEY" >/dev/null \
        || error "Secret update failed"
else
    info "Secret missing → creating"
    ibmcloud ce secret create \
        --name "$SECRET_NAME" \
        --format registry \
        --server us.icr.io \
        --username iamapikey \
        --password "$IBM_CLOUD_API_KEY" >/dev/null \
        || error "Secret creation failed"
fi

############################################
# Application Handling
############################################

APP_NAME="instana-mcp"

info "Checking application..."

if ibmcloud ce application get --name "$APP_NAME" >/dev/null 2>&1; then
    info "Application exists → updating image"
    ibmcloud ce application update \
        --name "$APP_NAME" \
        --image "$IMAGE_REF" >/dev/null \
        || error "Application update failed"
else
    info "Application missing → creating"
    ibmcloud ce application create \
        --name "$APP_NAME" \
        --image "$IMAGE_REF" \
        --registry-secret "$SECRET_NAME" \
        --min-scale 1 \
        --max-scale 1 \
        --cpu 1 \
        --memory 2G \
        --port 8080 >/dev/null \
        || error "Application creation failed"
fi

############################################
# Environment Variables
############################################

info "Applying environment variables..."

ibmcloud ce application update \
    --name "$APP_NAME" \
    --env CE_APP=mcp-instana \
    --env ALLOWED_HOSTS="localhost,localhost:*,127.0.0.1,127.0.0.1:*" \
    --env ALLOWED_ORIGINS="*" \
    --env INSTANA_API_TOKEN="$INSTANA_API_TOKEN" \
    --env INSTANA_BASE_URL="$INSTANA_BASE_URL" >/dev/null \
    || error "Environment variable update failed"

############################################
# Wait for Readiness
############################################

info "Waiting for application readiness..."

RETRIES=30
for ((i=1; i<=RETRIES; i++)); do
    if ibmcloud ce application get --name "$APP_NAME" 2>/dev/null | grep -q Ready; then
        info "Application Ready"
        break
    fi

    [ "$i" -eq "$RETRIES" ] && error "Application failed to become Ready"

    sleep 5
done

############################################
# Extract Application URL
############################################

info "Extracting application URL..."

APP_URL=$(ibmcloud ce application get --name "$APP_NAME" \
          | awk '/URL/ {print $2}')

[ -z "$APP_URL" ] && error "Failed to extract application URL"

HOSTNAME=$(echo "$APP_URL" | sed 's|https://||')

info "Application URL → $APP_URL"

############################################
# Update Allowed Hosts
############################################

UPDATED_HOSTS="localhost,localhost:*,127.0.0.1,127.0.0.1:*,${HOSTNAME},${HOSTNAME}:*"

info "Updating ALLOWED_HOSTS..."

ibmcloud ce application update \
    --name "$APP_NAME" \
    --env ALLOWED_HOSTS="$UPDATED_HOSTS" >/dev/null \
    || error "Allowed hosts update failed"

############################################
# Success Output
############################################

info "Deployment Completed Successfully"
info "MCP Endpoint → ${APP_URL}/mcp"
