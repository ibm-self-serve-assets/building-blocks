#!/bin/bash
# deploy_orchestration.sh - Complete deployment automation for multi-agent systems

set -e  # Exit on error

# Configuration
DRAFT_ENV="draft"
LIVE_ENV="live"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Backup current live environment
backup_live() {
    log_info "Creating backup of live environment..."
    mkdir -p "$BACKUP_DIR"
    
    # Export all agents
    orchestrate agents export --env live --output "$BACKUP_DIR/agents"
    
    # Export all workflows
    orchestrate tools export --env live --kind flow --output "$BACKUP_DIR/workflows"
    
    # Export all models
    orchestrate models export --env live --output "$BACKUP_DIR/models"
    
    # Export all connections
    orchestrate connections export --env live --output "$BACKUP_DIR/connections"
    
    log_info "Backup completed: $BACKUP_DIR"
}

# Deploy connections
deploy_connections() {
    log_info "Deploying connections..."
    
    for conn_file in connections/*.yaml; do
        if [ -f "$conn_file" ]; then
            conn_name=$(basename "$conn_file" .yaml)
            log_info "Deploying connection: $conn_name"
            
            # Add connection
            orchestrate connections add -f "$conn_file" --env live || true
            
            # Configure connection
            orchestrate connections configure \
                -a "$conn_name" \
                --env live \
                --type team \
                --kind key_value
            
            # Set credentials from environment
            if [ -n "${!conn_name^^}_API_KEY" ]; then
                orchestrate connections set-credentials \
                    -a "$conn_name" \
                    --env live \
                    -e "${conn_name^^}_API_KEY=${!conn_name^^}_API_KEY"
            fi
        fi
    done
}

# Deploy models
deploy_models() {
    log_info "Deploying AI Gateway models..."
    
    for model_file in models/*.yaml; do
        if [ -f "$model_file" ]; then
            model_name=$(basename "$model_file" .yaml)
            log_info "Deploying model: $model_name"
            
            orchestrate models add -f "$model_file" --env live
        fi
    done
}

# Deploy MCP toolkits
deploy_mcp_toolkits() {
    log_info "Deploying MCP toolkits..."
    
    for toolkit in mcp-servers/*; do
        if [ -d "$toolkit" ]; then
            toolkit_name=$(basename "$toolkit")
            log_info "Deploying MCP toolkit: $toolkit_name"
            
            orchestrate tools import \
                --mcp "$toolkit_name" \
                --env live
        fi
    done
}

# Deploy agents
deploy_agents() {
    log_info "Deploying agents..."
    
    for agent_file in agents/*.yaml; do
        if [ -f "$agent_file" ]; then
            agent_name=$(basename "$agent_file" .yaml)
            log_info "Deploying agent: $agent_name"
            
            orchestrate agents import \
                -f "$agent_file" \
                --env live
        fi
    done
}

# Deploy workflows
deploy_workflows() {
    log_info "Deploying workflows..."
    
    for workflow_file in workflows/*.py; do
        if [ -f "$workflow_file" ]; then
            workflow_name=$(basename "$workflow_file" .py)
            log_info "Deploying workflow: $workflow_name"
            
            orchestrate tools import \
                -k flow \
                -f "$workflow_file" \
                --env live
        fi
    done
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # List all agents
    log_info "Checking agents..."
    orchestrate agents list --env live
    
    # List all workflows
    log_info "Checking workflows..."
    orchestrate tools list --env live --kind flow
    
    # List all models
    log_info "Checking models..."
    orchestrate models list --env live
    
    # List all connections
    log_info "Checking connections..."
    orchestrate connections list --env live
}

# Rollback to backup
rollback() {
    log_warn "Rolling back to backup: $BACKUP_DIR"
    
    # Restore agents
    for agent_file in "$BACKUP_DIR/agents"/*.yaml; do
        if [ -f "$agent_file" ]; then
            orchestrate agents import -f "$agent_file" --env live
        fi
    done
    
    # Restore workflows
    for workflow_file in "$BACKUP_DIR/workflows"/*.py; do
        if [ -f "$workflow_file" ]; then
            orchestrate tools import -k flow -f "$workflow_file" --env live
        fi
    done
    
    log_info "Rollback completed"
}

# Main deployment flow
main() {
    log_info "Starting deployment to live environment..."
    
    # Backup current state
    backup_live
    
    # Deploy in order
    deploy_connections
    deploy_models
    deploy_mcp_toolkits
    deploy_agents
    deploy_workflows
    
    # Verify
    verify_deployment
    
    log_info "Deployment completed successfully!"
    log_info "Backup location: $BACKUP_DIR"
}

# Handle errors
trap 'log_error "Deployment failed! Run rollback if needed."; exit 1' ERR

# Run deployment
main

# Made with Bob
