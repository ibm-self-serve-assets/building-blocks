#!/bin/bash
# Voice Agent Deployment Script
# Automates deployment of voice-enabled agents to watsonx Orchestrate

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${PROJECT_ROOT}/configs"
CREDENTIALS_FILE="${PROJECT_ROOT}/credentials.yaml"
LOG_FILE="${PROJECT_ROOT}/deployment.log"
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')

# Default values
ENVIRONMENT="draft"
DRY_RUN=false
VERBOSE=false

# Functions
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "${LOG_FILE}"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "${LOG_FILE}"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "${LOG_FILE}"
    exit 1
}

debug() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[DEBUG]${NC} $@" | tee -a "${LOG_FILE}"
    fi
}

print_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     Voice Agent Deployment Script for watsonx Orchestrate  ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

print_usage() {
    cat << EOF
Usage: $0 [OPTIONS] COMMAND

Commands:
    deploy-all              Deploy all components (agent, voice config, channels, tools)
    deploy-agent            Deploy agent only
    deploy-voice-config     Deploy voice configuration only
    deploy-channels         Deploy channel integrations only
    deploy-tools            Deploy tools only
    validate                Validate deployment
    rollback                Rollback to previous version
    status                  Check deployment status

Options:
    -e, --environment ENV   Target environment (draft|live) [default: draft]
    -c, --config DIR        Configuration directory [default: ./configs]
    -d, --dry-run           Show what would be deployed without actually deploying
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

Examples:
    $0 deploy-all
    $0 --environment live deploy-agent
    $0 --dry-run deploy-all
    $0 validate

EOF
}

check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    debug "Python 3: $(python3 --version)"
    
    # Check ADK
    if ! command -v wxo &> /dev/null; then
        error "watsonx Orchestrate ADK not installed. Run: pip install ibm-watsonx-orchestrate --with-voice"
    fi
    debug "ADK: $(wxo --version)"
    
    # Check credentials file
    if [ ! -f "${CREDENTIALS_FILE}" ]; then
        error "Credentials file not found: ${CREDENTIALS_FILE}"
    fi
    debug "Credentials file found: ${CREDENTIALS_FILE}"
    
    # Check config directory
    if [ ! -d "${CONFIG_DIR}" ]; then
        error "Configuration directory not found: ${CONFIG_DIR}"
    fi
    debug "Config directory found: ${CONFIG_DIR}"
    
    success "Prerequisites check passed"
}

load_credentials() {
    info "Loading credentials..."
    
    if [ "$DRY_RUN" = true ]; then
        warning "Dry run mode - credentials not actually loaded"
        return 0
    fi
    
    # Source credentials (in production, use proper secret management)
    if [ -f "${CREDENTIALS_FILE}" ]; then
        # Export variables from YAML (simplified - use proper YAML parser in production)
        export $(grep -v '^#' "${CREDENTIALS_FILE}" | grep -v '^$' | xargs)
        success "Credentials loaded"
    else
        error "Credentials file not found"
    fi
}

deploy_voice_config() {
    info "Deploying voice configuration..."
    
    local voice_config="${CONFIG_DIR}/voice_config.yaml"
    
    if [ ! -f "${voice_config}" ]; then
        warning "Voice config not found: ${voice_config}"
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would deploy: ${voice_config}"
        return 0
    fi
    
    debug "Importing voice config from: ${voice_config}"
    wxo voice-config import "${voice_config}" --environment "${ENVIRONMENT}"
    
    success "Voice configuration deployed"
}

deploy_agent() {
    info "Deploying agent..."
    
    local agent_file="${CONFIG_DIR}/agent.yaml"
    
    if [ ! -f "${agent_file}" ]; then
        error "Agent file not found: ${agent_file}"
    fi
    
    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would deploy: ${agent_file}"
        return 0
    fi
    
    debug "Importing agent from: ${agent_file}"
    wxo agent import "${agent_file}" --environment "${ENVIRONMENT}"
    
    success "Agent deployed"
}

deploy_phone_channel() {
    info "Deploying phone channel..."
    
    local phone_config="${CONFIG_DIR}/channels/phone_config.yaml"
    
    if [ ! -f "${phone_config}" ]; then
        warning "Phone config not found: ${phone_config}"
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would deploy: ${phone_config}"
        return 0
    fi
    
    debug "Importing phone config from: ${phone_config}"
    wxo phone-config import "${phone_config}" --environment "${ENVIRONMENT}"
    
    # Attach agent to phone config (assumes agent name from config)
    local agent_name=$(grep 'name:' "${CONFIG_DIR}/agent.yaml" | head -1 | awk '{print $2}')
    local phone_name=$(grep 'name:' "${phone_config}" | head -1 | awk '{print $2}')
    
    wxo phone-config attach --config-name "${phone_name}" --agent-name "${agent_name}" --environment "${ENVIRONMENT}"
    
    success "Phone channel deployed"
}

deploy_messaging_channels() {
    info "Deploying messaging channels..."
    
    local channels_dir="${CONFIG_DIR}/channels"
    
    if [ ! -d "${channels_dir}" ]; then
        warning "Channels directory not found: ${channels_dir}"
        return 0
    fi
    
    # Deploy WhatsApp
    if [ -f "${channels_dir}/whatsapp_config.yaml" ]; then
        if [ "$DRY_RUN" = true ]; then
            info "[DRY RUN] Would deploy: whatsapp_config.yaml"
        else
            debug "Importing WhatsApp channel"
            wxo channel import "${channels_dir}/whatsapp_config.yaml" --environment "${ENVIRONMENT}"
            success "WhatsApp channel deployed"
        fi
    fi
    
    # Deploy SMS
    if [ -f "${channels_dir}/sms_config.yaml" ]; then
        if [ "$DRY_RUN" = true ]; then
            info "[DRY RUN] Would deploy: sms_config.yaml"
        else
            debug "Importing SMS channel"
            wxo channel import "${channels_dir}/sms_config.yaml" --environment "${ENVIRONMENT}"
            success "SMS channel deployed"
        fi
    fi
    
    # Deploy Slack
    if [ -f "${channels_dir}/slack_config.yaml" ]; then
        if [ "$DRY_RUN" = true ]; then
            info "[DRY RUN] Would deploy: slack_config.yaml"
        else
            debug "Importing Slack channel"
            wxo channel import "${channels_dir}/slack_config.yaml" --environment "${ENVIRONMENT}"
            success "Slack channel deployed"
        fi
    fi
    
    success "Messaging channels deployed"
}

deploy_channels() {
    info "Deploying all channels..."
    deploy_phone_channel
    deploy_messaging_channels
    success "All channels deployed"
}

deploy_tools() {
    info "Deploying tools..."
    
    local tools_dir="${CONFIG_DIR}/tools"
    
    if [ ! -d "${tools_dir}" ]; then
        warning "Tools directory not found: ${tools_dir}"
        return 0
    fi
    
    local tool_count=0
    for tool_file in "${tools_dir}"/*.py; do
        if [ -f "$tool_file" ]; then
            if [ "$DRY_RUN" = true ]; then
                info "[DRY RUN] Would deploy: $(basename $tool_file)"
            else
                debug "Importing tool: $(basename $tool_file)"
                wxo tool import python "$tool_file" --environment "${ENVIRONMENT}"
                success "Deployed tool: $(basename $tool_file)"
            fi
            ((tool_count++))
        fi
    done
    
    if [ $tool_count -eq 0 ]; then
        warning "No tools found in ${tools_dir}"
    else
        success "Deployed ${tool_count} tools"
    fi
}

validate_deployment() {
    info "Validating deployment..."
    
    local agent_name=$(grep 'name:' "${CONFIG_DIR}/agent.yaml" | head -1 | awk '{print $2}')
    
    # Check agent exists
    if wxo agent list --environment "${ENVIRONMENT}" | grep -q "${agent_name}"; then
        success "Agent '${agent_name}' found"
    else
        error "Agent '${agent_name}' not found"
    fi
    
    # Check voice config exists
    if [ -f "${CONFIG_DIR}/voice_config.yaml" ]; then
        local voice_name=$(grep 'name:' "${CONFIG_DIR}/voice_config.yaml" | head -1 | awk '{print $2}')
        if wxo voice-config list --environment "${ENVIRONMENT}" | grep -q "${voice_name}"; then
            success "Voice config '${voice_name}' found"
        else
            warning "Voice config '${voice_name}' not found"
        fi
    fi
    
    success "Deployment validation passed"
}

deploy_all() {
    info "Starting full deployment..."
    check_prerequisites
    load_credentials
    deploy_voice_config
    deploy_agent
    deploy_channels
    deploy_tools
    validate_deployment
    success "Full deployment completed successfully!"
}

rollback() {
    warning "Rollback functionality not yet implemented"
    info "Manual rollback steps:"
    info "1. Identify previous version"
    info "2. Re-deploy previous configuration"
    info "3. Verify functionality"
    info "4. Update documentation"
}

show_status() {
    info "Checking deployment status..."
    
    echo ""
    echo "=== Agents ==="
    wxo agent list --environment "${ENVIRONMENT}" || warning "Failed to list agents"
    
    echo ""
    echo "=== Voice Configurations ==="
    wxo voice-config list --environment "${ENVIRONMENT}" || warning "Failed to list voice configs"
    
    echo ""
    echo "=== Channels ==="
    wxo channel list --environment "${ENVIRONMENT}" || warning "Failed to list channels"
    
    echo ""
    echo "=== Tools ==="
    wxo tool list --environment "${ENVIRONMENT}" || warning "Failed to list tools"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_DIR="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        deploy-all|deploy-agent|deploy-voice-config|deploy-channels|deploy-tools|validate|rollback|status)
            COMMAND="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Main execution
print_banner

if [ -z "${COMMAND:-}" ]; then
    error "No command specified"
    print_usage
    exit 1
fi

info "Command: ${COMMAND}"
info "Environment: ${ENVIRONMENT}"
info "Config directory: ${CONFIG_DIR}"
if [ "$DRY_RUN" = true ]; then
    warning "DRY RUN MODE - No actual changes will be made"
fi

# Execute command
case "${COMMAND}" in
    deploy-all)
        deploy_all
        ;;
    deploy-agent)
        check_prerequisites
        load_credentials
        deploy_agent
        ;;
    deploy-voice-config)
        check_prerequisites
        load_credentials
        deploy_voice_config
        ;;
    deploy-channels)
        check_prerequisites
        load_credentials
        deploy_channels
        ;;
    deploy-tools)
        check_prerequisites
        load_credentials
        deploy_tools
        ;;
    validate)
        validate_deployment
        ;;
    rollback)
        rollback
        ;;
    status)
        show_status
        ;;
    *)
        error "Unknown command: ${COMMAND}"
        ;;
esac

info "Script completed at $(date)"

# Made with Bob
