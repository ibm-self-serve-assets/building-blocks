# Deployment Guide

## Overview
Complete guide for deploying voice-enabled agents with automation scripts, credential management, and production best practices.

## Deployment Principles

### Security First
- Never expose credentials in code or version control
- Use environment variables for sensitive data
- Provide sample credential files with placeholders
- Add credential files to .gitignore
- Use connection objects in watsonx Orchestrate

### Automation
- Create deployment scripts for consistency
- Use infrastructure as code
- Document manual steps clearly
- Enable repeatable deployments

### Validation
- Run health checks after deployment
- Test critical paths
- Verify integrations
- Monitor initial traffic

### Rollback Ready
- Document rollback procedures
- Keep previous versions accessible
- Test rollback process
- Have emergency contacts ready

## Credential Management

### Sample Files to Create

**credentials.sample.yaml**
```yaml
# Voice Agent Credentials Template
# Copy to credentials.yaml and fill in actual values
# DO NOT commit credentials.yaml to version control

# Watson Services
watson:
  stt:
    api_key: "YOUR_WATSON_STT_API_KEY"
    service_url: "https://api.us-south.speech-to-text.watson.cloud.ibm.com"
  tts:
    api_key: "YOUR_WATSON_TTS_API_KEY"
    service_url: "https://api.us-south.text-to-speech.watson.cloud.ibm.com"

# watsonx Orchestrate
orchestrate:
  api_key: "YOUR_ORCHESTRATE_API_KEY"
  url: "https://your-instance.watson-orchestrate.ibm.com"
  space_id: "YOUR_SPACE_ID"

# Channel Integrations
channels:
  genesys:
    api_key: "YOUR_GENESYS_API_KEY"
    client_secret: "YOUR_GENESYS_CLIENT_SECRET"
  twilio:
    account_sid: "YOUR_TWILIO_ACCOUNT_SID"
    auth_token: "YOUR_TWILIO_AUTH_TOKEN"
    whatsapp_number: "whatsapp:+14155238886"
  slack:
    bot_token: "xoxb-YOUR-BOT-TOKEN"
    signing_secret: "YOUR_SIGNING_SECRET"
```

**.env.sample**
```bash
# Environment Variables Template
# Copy to .env and fill in actual values

WATSON_STT_API_KEY=your_stt_api_key
WATSON_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com
WATSON_TTS_API_KEY=your_tts_api_key
WATSON_TTS_URL=https://api.us-south.text-to-speech.watson.cloud.ibm.com

WXO_API_KEY=your_orchestrate_api_key
WXO_URL=https://your-instance.watson-orchestrate.ibm.com
WXO_SPACE_ID=your_space_id

ENVIRONMENT=development
LOG_LEVEL=INFO
```

### .gitignore Entries
```
credentials.yaml
credentials.json
.env
.env.local
*.key
*.pem
secrets/
```

### Security Principles
- **NEVER** ask users for actual credentials
- **NEVER** store credentials in code or configuration files
- **ALWAYS** use environment variables for sensitive data
- **ALWAYS** create sample/template files only

## Deployment Plan Template

Create `deployment_plan.md` for each deployment:

```markdown
# Voice Agent Deployment Plan

## Overview
**Project:** [Project Name]
**Deployment Date:** [Date]
**Environment:** [Development/Staging/Production]

### Objectives
- Deploy voice-enabled agent to watsonx Orchestrate
- Configure voice channels
- Set up monitoring and alerting
- Validate end-to-end functionality

### Components
- Agent: [Agent Name]
- Voice Config: [Config Name]
- Channels: [List of channels]
- Integrations: [External systems]

## Pre-Deployment Checklist

### Environment Preparation
- [ ] watsonx Orchestrate instance accessible
- [ ] Required credentials obtained and validated
- [ ] Network connectivity verified
- [ ] Backup of current configuration completed

### Credential Setup
- [ ] credentials.yaml populated with actual values
- [ ] Environment variables configured
- [ ] Orchestrate connections created
- [ ] Channel provider accounts configured

### Testing
- [ ] Agent tested in development environment
- [ ] Voice configuration validated
- [ ] Channel integrations tested
- [ ] Security review passed

## Deployment Steps

### Step 1: Deploy Agent
```bash
./deployment.sh deploy-agent
```
**Expected Output:** Agent created/updated successfully
**Validation:** Verify agent appears in agent list

### Step 2: Deploy Voice Configuration
```bash
./deployment.sh deploy-voice-config
```
**Expected Output:** Voice config imported successfully
**Validation:** Test STT/TTS functionality

### Step 3: Configure Channels
```bash
./deployment.sh deploy-channels
```
**Expected Output:** Channels created and configured
**Validation:** Verify webhook URLs are accessible

### Step 4: Deploy Tools
```bash
./deployment.sh deploy-tools
```
**Expected Output:** All tools imported successfully
**Validation:** Verify tools are accessible to agent

## Post-Deployment Validation

### Health Checks
- [ ] Agent responds to test messages
- [ ] Voice input/output working correctly
- [ ] All channels operational
- [ ] Tool invocations successful

### Smoke Tests
1. Basic interaction test through each channel
2. Voice quality test (STT accuracy, TTS naturalness)
3. Integration test (external API calls)
4. Load test (if applicable)

### Monitoring Setup
- [ ] Logging configured
- [ ] Metrics collection enabled
- [ ] Alerts configured
- [ ] Dashboard created

## Rollback Procedure

### Rollback Triggers
- Critical functionality broken
- Performance degradation > 50%
- Security vulnerability discovered

### Rollback Steps
1. Execute rollback script: `./deployment.sh rollback`
2. Verify previous version functionality
3. Notify stakeholders
4. Schedule post-mortem

## Troubleshooting

### Common Issues
**Agent not responding:** Check agent status, verify credentials
**Voice quality problems:** Verify STT/TTS configuration
**Channel failures:** Verify webhook URLs and authentication

### Contact Information
- Deployment Lead: [Name] - [Email]
- Technical Support: [Team] - [Email]
```

## Deployment Script

Create `deployment.sh` for automation:

```bash
#!/bin/bash
# Voice Agent Deployment Script

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${SCRIPT_DIR}/configs"
CREDENTIALS_FILE="${SCRIPT_DIR}/credentials.yaml"
LOG_FILE="${SCRIPT_DIR}/deployment.log"

# Functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "${LOG_FILE}"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "${LOG_FILE}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "${LOG_FILE}"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    if [ ! -f "${CREDENTIALS_FILE}" ]; then
        error "Credentials file not found: ${CREDENTIALS_FILE}"
    fi
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    
    if ! command -v wxo &> /dev/null; then
        error "watsonx Orchestrate ADK not installed"
    fi
    
    success "Prerequisites check passed"
}

load_credentials() {
    log "Loading credentials..."
    # Load credentials from file
    export $(cat "${CREDENTIALS_FILE}" | grep -v '^#' | xargs)
    success "Credentials loaded"
}

deploy_agent() {
    log "Deploying agent..."
    wxo agent import "${CONFIG_DIR}/agent.yaml"
    success "Agent deployed"
}

deploy_voice_config() {
    log "Deploying voice configuration..."
    wxo voice-config import "${CONFIG_DIR}/voice_config.yaml"
    success "Voice configuration deployed"
}

deploy_channels() {
    log "Deploying channels..."
    
    if [ -f "${CONFIG_DIR}/channels/phone_config.yaml" ]; then
        wxo phone-config import "${CONFIG_DIR}/channels/phone_config.yaml"
        success "Phone config deployed"
    fi
    
    if [ -f "${CONFIG_DIR}/channels/whatsapp_config.yaml" ]; then
        wxo channel import "${CONFIG_DIR}/channels/whatsapp_config.yaml"
        success "WhatsApp channel deployed"
    fi
    
    success "All channels deployed"
}

deploy_tools() {
    log "Deploying tools..."
    
    for tool_file in "${CONFIG_DIR}"/tools/*.py; do
        if [ -f "$tool_file" ]; then
            wxo tool import python "$tool_file"
            success "Deployed tool: $(basename $tool_file)"
        fi
    done
    
    success "All tools deployed"
}

validate_deployment() {
    log "Validating deployment..."
    
    # Check agent exists
    wxo agent list | grep -q "agent-name" || error "Agent not found"
    
    # Check voice config exists
    wxo voice-config list | grep -q "voice-config-name" || error "Voice config not found"
    
    success "Deployment validation passed"
}

rollback() {
    log "Rolling back deployment..."
    warning "Rollback not yet implemented"
    # Add rollback logic here
}

deploy_all() {
    check_prerequisites
    load_credentials
    deploy_agent
    deploy_voice_config
    deploy_channels
    deploy_tools
    validate_deployment
    success "Deployment completed successfully!"
}

# Main script
case "${1:-}" in
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
    *)
        echo "Usage: $0 {deploy-all|deploy-agent|deploy-voice-config|deploy-channels|deploy-tools|validate|rollback}"
        exit 1
        ;;
esac
```

## Deployment Workflow

### Phase 1: Preparation
1. Create deployment plan
2. Set up credentials (sample files only)
3. Review security checklist
4. Backup current configuration

### Phase 2: Deployment
1. Deploy voice configuration
2. Deploy agent
3. Configure channels
4. Deploy tools (if needed)

### Phase 3: Validation
1. Run health checks
2. Execute smoke tests
3. Verify integrations
4. Monitor initial traffic

### Phase 4: Monitoring
1. Set up logging
2. Configure alerts
3. Create dashboards
4. Document issues

## Environment Strategy

### Development
- Use for initial testing
- Rapid iteration
- No production data
- Relaxed security

### Staging
- Mirror production setup
- Full integration testing
- Production-like data
- Production security

### Production
- Live user traffic
- Full monitoring
- Strict security
- Change control

## Best Practices

### Before Deployment
- Create comprehensive deployment plan
- Test in staging environment
- Review security checklist
- Prepare rollback procedure
- Notify stakeholders

### During Deployment
- Follow deployment plan exactly
- Log all actions
- Validate each step
- Monitor for errors
- Be ready to rollback

### After Deployment
- Run health checks
- Execute smoke tests
- Monitor metrics
- Gather feedback
- Document lessons learned

### Ongoing
- Monitor performance
- Track errors
- Analyze usage
- Iterate improvements
- Update documentation

## Monitoring and Alerting

### Key Metrics
- Response time
- Error rate
- User satisfaction
- Channel availability
- STT/TTS quality

### Alert Thresholds
- Error rate > 5%
- Response time > 3 seconds
- Channel downtime > 1 minute
- STT accuracy < 90%

### Logging Strategy
- Log all interactions
- Capture errors with context
- Track performance metrics
- Store for analysis
- Comply with privacy regulations

## Troubleshooting Deployment Issues

### Agent Not Deploying
**Symptoms:** Import fails

**Checks:**
- Verify YAML syntax
- Check credentials
- Review agent specification
- Validate tool references

**Solutions:**
- Fix YAML errors
- Update credentials
- Correct specification
- Verify tool availability

### Voice Config Issues
**Symptoms:** Voice not working

**Checks:**
- Verify provider credentials
- Check model availability
- Review audio settings
- Test STT/TTS separately

**Solutions:**
- Update provider credentials
- Use available models
- Adjust audio configuration
- Test components individually

### Channel Integration Failures
**Symptoms:** Channels not connecting

**Checks:**
- Verify webhook URLs
- Check provider credentials
- Review firewall rules
- Test connectivity

**Solutions:**
- Update webhook configuration
- Refresh credentials
- Open required ports
- Test with curl/Postman

## Security Checklist

- [ ] Credentials stored securely
- [ ] Environment variables used
- [ ] Sample files only in repo
- [ ] .gitignore configured
- [ ] SSL/TLS enabled
- [ ] Webhook signatures verified
- [ ] Access controls configured
- [ ] Audit logging enabled
- [ ] Data encryption at rest
- [ ] Data encryption in transit

## Compliance Considerations

### Data Privacy
- Handle PII appropriately
- Comply with GDPR/CCPA
- Implement data retention policies
- Enable user data deletion

### Recording and Monitoring
- Disclose call recording
- Obtain consent where required
- Secure recording storage
- Implement access controls

### Accessibility
- Support multiple input methods
- Provide text alternatives
- Handle disabilities gracefully
- Test with assistive technologies

## Post-Deployment Checklist

- [ ] All components deployed successfully
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Documentation updated
- [ ] Stakeholders notified
- [ ] Rollback procedure tested
- [ ] Performance baseline established
- [ ] User feedback mechanism in place