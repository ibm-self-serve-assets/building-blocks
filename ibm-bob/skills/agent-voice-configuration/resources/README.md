# Voice Agent Resources

This folder contains deployment scripts, credential templates, and configuration examples for voice-enabled watsonx Orchestrate agents.

## Contents

### Deployment Scripts
- **`deploy_voice_agent.sh`** - Automated deployment script for voice agents
  - Deploys agents, voice configurations, channels, and tools
  - Supports dry-run mode for testing
  - Includes validation and rollback capabilities
  - Comprehensive logging and error handling

### Credential Templates
- **`credentials.sample.yaml`** - YAML format credential template
  - Watson STT/TTS credentials
  - watsonx Orchestrate API keys
  - Channel provider credentials (Genesys, Twilio, Slack)
  - Optional provider credentials (Google, Azure)

- **`.env.sample`** - Environment variables template
  - Alternative to YAML format
  - Suitable for containerized deployments
  - Easy integration with CI/CD pipelines

## Quick Start

### 1. Set Up Credentials

**Option A: Using YAML (Recommended for local development)**
```bash
# Copy the sample file
cp credentials.sample.yaml credentials.yaml

# Edit with your actual credentials
nano credentials.yaml

# Add to .gitignore
echo "credentials.yaml" >> .gitignore
```

**Option B: Using Environment Variables (Recommended for production)**
```bash
# Copy the sample file
cp .env.sample .env

# Edit with your actual credentials
nano .env

# Add to .gitignore
echo ".env" >> .gitignore

# Source the variables
source .env
```

### 2. Prepare Configuration Files

Create a `configs/` directory structure:
```
configs/
├── agent.yaml              # Agent definition
├── voice_config.yaml       # Voice configuration
├── channels/
│   ├── phone_config.yaml   # Phone channel
│   ├── whatsapp_config.yaml # WhatsApp channel
│   ├── sms_config.yaml     # SMS channel
│   └── slack_config.yaml   # Slack channel
└── tools/
    ├── tool1.py            # Custom tools
    └── tool2.py
```

### 3. Deploy Voice Agent

**Full Deployment:**
```bash
# Make script executable
chmod +x deploy_voice_agent.sh

# Deploy everything
./deploy_voice_agent.sh deploy-all
```

**Dry Run (Test without deploying):**
```bash
./deploy_voice_agent.sh --dry-run deploy-all
```

**Deploy Specific Components:**
```bash
# Deploy only agent
./deploy_voice_agent.sh deploy-agent

# Deploy only voice configuration
./deploy_voice_agent.sh deploy-voice-config

# Deploy only channels
./deploy_voice_agent.sh deploy-channels

# Deploy only tools
./deploy_voice_agent.sh deploy-tools
```

**Deploy to Different Environment:**
```bash
# Deploy to live environment
./deploy_voice_agent.sh --environment live deploy-all
```

### 4. Validate Deployment

```bash
# Check deployment status
./deploy_voice_agent.sh validate

# View current status
./deploy_voice_agent.sh status
```

## Deployment Script Usage

### Commands

- **`deploy-all`** - Deploy all components (agent, voice config, channels, tools)
- **`deploy-agent`** - Deploy agent only
- **`deploy-voice-config`** - Deploy voice configuration only
- **`deploy-channels`** - Deploy channel integrations only
- **`deploy-tools`** - Deploy tools only
- **`validate`** - Validate deployment
- **`rollback`** - Rollback to previous version (placeholder)
- **`status`** - Check deployment status

### Options

- **`-e, --environment ENV`** - Target environment (draft|live) [default: draft]
- **`-c, --config DIR`** - Configuration directory [default: ./configs]
- **`-d, --dry-run`** - Show what would be deployed without actually deploying
- **`-v, --verbose`** - Enable verbose output
- **`-h, --help`** - Show help message

### Examples

```bash
# Deploy to production with verbose output
./deploy_voice_agent.sh --environment live --verbose deploy-all

# Test deployment without making changes
./deploy_voice_agent.sh --dry-run deploy-all

# Deploy from custom config directory
./deploy_voice_agent.sh --config ./my-configs deploy-all

# Check status of live environment
./deploy_voice_agent.sh --environment live status
```

## Security Best Practices

### Credential Management

1. **Never commit credentials to version control**
   ```bash
   # Add to .gitignore
   echo "credentials.yaml" >> .gitignore
   echo "credentials.json" >> .gitignore
   echo ".env" >> .gitignore
   echo ".env.local" >> .gitignore
   echo "*.key" >> .gitignore
   echo "*.pem" >> .gitignore
   echo "secrets/" >> .gitignore
   ```

2. **Use environment-specific credentials**
   - Development: Test credentials with limited access
   - Staging: Production-like credentials in isolated environment
   - Production: Full credentials with proper access controls

3. **Rotate credentials regularly**
   - Set up 90-day rotation schedule
   - Document rotation procedures
   - Test with new credentials before deactivating old ones

4. **Use secret management services in production**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - watsonx Orchestrate Connections

### File Permissions

```bash
# Restrict access to credential files
chmod 600 credentials.yaml
chmod 600 .env

# Make deployment script executable
chmod +x deploy_voice_agent.sh
```

## Troubleshooting

### Common Issues

**Script fails with "wxo: command not found"**
```bash
# Install watsonx Orchestrate ADK with voice support
pip install ibm-watsonx-orchestrate --with-voice
```

**Credentials not loading**
```bash
# Verify credentials file exists
ls -la credentials.yaml

# Check file format (YAML syntax)
python3 -c "import yaml; yaml.safe_load(open('credentials.yaml'))"
```

**Deployment fails with authentication error**
```bash
# Verify credentials are correct
# Check API key format
# Ensure credentials haven't expired
# Test credentials manually with wxo CLI
```

**Channel integration not working**
```bash
# Verify webhook URLs are accessible
curl -X POST https://your-webhook-url

# Check provider credentials
# Review firewall rules
# Test with provider's testing tools
```

### Getting Help

1. Check deployment logs: `cat deployment.log`
2. Run with verbose mode: `./deploy_voice_agent.sh --verbose deploy-all`
3. Validate configuration: `./deploy_voice_agent.sh validate`
4. Review ADK documentation: `wxo --help`

## Configuration Examples

### Minimal Agent Configuration

```yaml
spec_version: v1
kind: Agent
name: simple-voice-agent
description: Simple voice-enabled agent

instructions: |
  You are a helpful voice assistant.
  Keep responses under 30 seconds.
  Use conversational language.

voice_configuration: my-voice-config
```

### Minimal Voice Configuration

```yaml
spec_version: v1
kind: VoiceConfiguration
name: my-voice-config
description: Basic voice configuration

stt_provider:
  provider: watson_stt
  model: en-US_Telephony

tts_provider:
  provider: watson_tts
  voice: en-US_MichaelV3Voice

audio_config:
  sample_rate: 8000
  encoding: mulaw
  channels: 1
```

## Additional Resources

- **Main Skill Documentation**: See parent directory for comprehensive guides
- **ADK Documentation**: Search using `wxo docs search [topic]`
- **watsonx Orchestrate**: https://www.ibm.com/products/watsonx-orchestrate
- **Watson Speech Services**: https://cloud.ibm.com/catalog/services/speech-to-text

## Support

For issues or questions:
1. Review the main skill documentation in parent directory
2. Check ADK documentation: `wxo docs`
3. Consult watsonx Orchestrate documentation
4. Contact your watsonx Orchestrate administrator

## License

These resources are provided as examples for building voice-enabled agents with watsonx Orchestrate. Modify as needed for your specific use case.