# 🌉 Agent Model Gateway Mode

A comprehensive Bob mode for integrating third-party LLM models into watsonx Orchestrate via the AI Gateway.

## Overview

The **Agent Model Gateway** mode is a specialized Bob mode designed to streamline the integration of external LLM models from providers like OpenAI, Anthropic, Google, Azure, AWS Bedrock, and many others into your watsonx Orchestrate environment. It provides an interactive, documentation-driven workflow that ensures secure, reliable, and production-ready model integrations.

## Key Features

### 🎯 Interactive Discovery & Planning
- Starts with comprehensive discovery questions to understand your requirements
- Gathers all necessary configuration details before proceeding
- Creates detailed integration plans (`plan.md`) before implementation
- Never executes commands automatically - provides scripts with instructions
- Validates user preferences at each major step

### 📚 Documentation-Driven Approach
- Proactively queries watsonx-orchestrate-adk MCP documentation at each step
- Ensures all configurations match latest ADK specifications
- Validates command syntax and parameters against official docs
- Provides links to relevant documentation sections
- Keeps up-to-date with ADK changes and best practices

### 🔒 Security-First Design
- Never hardcodes credentials in configuration files
- Uses watsonx Orchestrate connections for secure credential management
- Generates deployment scripts with placeholders for secrets
- Implements team vs member credential scoping
- Follows principle of least privilege for access control
- Provides security validation checklists

### 🌐 Comprehensive Provider Support

Supports **12+ LLM providers** with complete configuration templates:

| Provider | Popular Models | Auth Type |
|----------|---------------|-----------|
| **OpenAI** | GPT-4, GPT-4 Turbo, GPT-3.5 | API Key |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku | API Key |
| **Google** | Gemini 1.5 Pro, Gemini 1.5 Flash | API Key |
| **Azure OpenAI** | GPT-4, GPT-3.5 (Azure-hosted) | API Key + Deployment |
| **AWS Bedrock** | Claude, Llama, Titan, Mistral | AWS Credentials |
| **Mistral AI** | Mistral Large, Mistral Medium | API Key |
| **Groq** | Llama 3, Mixtral | API Key |
| **Ollama** | Local models (Llama, Mistral, etc.) | Local |
| **watsonx.ai** | Granite, Llama, Mixtral | API Key |
| **Cohere** | Command, Command R+ | API Key |
| **Fireworks AI** | Various open models | API Key |
| **Together AI** | Various open models | API Key |

### ⚡ Advanced Integration Capabilities
- **Model Policies**: Load balancing and fallback strategies
- **Multi-Environment**: Separate draft and live configurations
- **Cost Optimization**: Smart provider selection and routing
- **High Availability**: Automatic failover between providers
- **Performance Tuning**: Custom timeout and retry configurations
- **Monitoring**: Built-in validation and health checks

## Core Capabilities

### 1. Model Integration
- ✅ Add new models from any supported provider
- ✅ Configure provider-specific settings (API endpoints, regions, etc.)
- ✅ Set up model metadata (display names, descriptions, tags)
- ✅ Define model types (chat, chat_vision, completion, embedding)
- ✅ Update existing model configurations
- ✅ Remove models from environments
- ✅ Export model configurations for backup or migration

### 2. Connection Management
- ✅ Create secure connections for API authentication
- ✅ Configure connection types (key_value, api_key, bearer, OAuth)
- ✅ Set up team vs member credential scoping
- ✅ Manage credentials across draft and live environments
- ✅ Import/export connection configurations
- ✅ Associate connections with models

### 3. Model Policies
- ✅ **Load Balancing**: Distribute requests across multiple models
- ✅ **Fallback**: Automatic failover when primary model unavailable
- ✅ **Retry Logic**: Configure retry attempts and error codes
- ✅ **Custom Weights**: Control traffic distribution percentages
- ✅ **Strategy Configuration**: Define when to trigger fallback
- ✅ **Policy Testing**: Validate policy behavior before production

### 4. Deployment Automation
- ✅ Generate deployment scripts with error handling
- ✅ Multi-environment deployment (draft → live)
- ✅ Multi-provider setup scripts
- ✅ Rollback scripts for safe recovery
- ✅ Validation scripts for post-deployment checks
- ✅ Color-coded output for better readability

### 5. Validation & Testing
- ✅ Pre-deployment validation checklists
- ✅ Post-deployment verification procedures
- ✅ Production readiness assessments
- ✅ Comprehensive troubleshooting guides
- ✅ Diagnostic commands for quick checks
- ✅ Integration testing procedures

## Workflow Phases

The mode follows a structured 6-phase workflow:

### Phase 1: Initial Discovery
**Understand requirements and gather context**
- Ask about integration goals and use cases
- Identify target LLM provider(s)
- Determine environment (draft/live)
- Check for existing project structure
- Understand security and compliance requirements

### Phase 2: Information Gathering
**Collect all necessary configuration details**
- Provider-specific settings (API keys, endpoints, regions)
- Model selection and configuration
- Connection requirements
- Policy needs (load balancing, fallback)
- Environment-specific settings

### Phase 3: Planning
**Create comprehensive integration plan**
- Generate `plan.md` with step-by-step approach
- Document all configuration decisions
- Identify potential risks and mitigations
- Define success criteria
- Get user approval before proceeding

### Phase 4: Asset Generation
**Create all necessary configuration files and scripts**
- Generate model YAML specifications
- Create connection configuration files
- Build deployment scripts with placeholders
- Generate validation scripts
- Create rollback procedures

### Phase 5: Validation
**Review and validate all generated assets**
- Query ADK docs to verify configurations
- Check YAML syntax and structure
- Validate command syntax
- Review security practices
- Ensure completeness of documentation

### Phase 6: Completion
**Provide deployment instructions and next steps**
- Present deployment instructions
- Explain validation procedures
- Provide troubleshooting guidance
- Document monitoring recommendations
- Offer post-deployment support

## Getting Started

### Prerequisites
- ✅ watsonx Orchestrate ADK installed and configured
- ✅ Access to watsonx Orchestrate environment (draft or live)
- ✅ API keys for desired LLM providers
- ✅ Basic understanding of YAML syntax
- ✅ Familiarity with command-line tools

### Quick Start

1. **Switch to Agent Model Gateway mode** in Bob
2. **Answer discovery questions** about your integration needs
3. **Review the generated `plan.md`** file
4. **Execute the deployment script** with your credentials
5. **Validate** the model using `orchestrate models list`
6. **Test** the model with a simple agent

### Your First Integration: OpenAI GPT-4

```bash
# Step 1: Switch to Agent Model Gateway mode
# Tell Bob: "I want to integrate OpenAI GPT-4"

# Step 2: Answer discovery questions
# Provider: OpenAI
# Model: gpt-4
# Environment: draft

# Step 3: Review the generated plan.md

# Step 4: Run the deployment script
./scripts/deploy-openai-gpt4.sh
# Enter your OpenAI API key when prompted

# Step 5: Validate
orchestrate models list

# Step 6: Test with an agent
# Create an agent that uses: llm: virtual-model/openai/gpt-4
```

## Use Cases

### 1. Basic Model Integration
**Scenario**: Add a single model from OpenAI, Anthropic, or another provider

**Steps**:
1. Switch to Agent Model Gateway mode
2. Answer discovery questions about provider and model
3. Review generated `plan.md`
4. Execute deployment script with your API key
5. Validate model is available in watsonx Orchestrate

### 2. Multi-Provider Setup
**Scenario**: Set up multiple models from different providers with load balancing

**Steps**:
1. Specify multiple providers during discovery
2. Configure load balancing policy
3. Review generated configurations for all providers
4. Deploy models and policy
5. Test load balancing behavior

### 3. High Availability Configuration
**Scenario**: Configure fallback between providers for reliability

**Steps**:
1. Identify primary and fallback providers
2. Configure fallback policy with error codes
3. Set up retry logic
4. Deploy to draft environment first
5. Test failover scenarios
6. Promote to live environment

### 4. Cost Optimization
**Scenario**: Route requests to cost-effective providers while maintaining quality

**Steps**:
1. Analyze cost per token for different providers
2. Configure load balancing with cost-based weights
3. Set up fallback to premium providers for critical requests
4. Monitor usage and costs
5. Adjust weights based on performance

### 5. Environment Migration
**Scenario**: Move models from draft to live environment

**Steps**:
1. Export model configurations from draft
2. Review and update for production
3. Deploy to live environment
4. Validate in live
5. Update agents to use live models

## Instruction Files

The mode includes 7 comprehensive instruction files:

| File | Lines | Description |
|------|-------|-------------|
| `1_workflow.xml` | 434 | Complete 6-phase workflow with interactive discovery and step-by-step guidance |
| `2_best_practices.xml` | 598 | Security, configuration, governance, and operational best practices |
| `3_provider_patterns.xml` | 738 | Complete templates for 12+ providers with YAML examples and connection setup |
| `4_adk_commands.xml` | 672 | Comprehensive CLI reference for models, connections, and validation commands |
| `5_examples.xml` | 822 | 8 end-to-end integration examples with complete files and troubleshooting |
| `6_validation.xml` | 738 | 3-phase validation checklists and troubleshooting guides |
| `7_deployment_script_template.xml` | 598 | 5 reusable bash script templates for deployment and validation |

**Total**: 5,398 lines of comprehensive documentation and instructions

## Provider Examples

### OpenAI
```yaml
spec_version: v1
kind: model
name: virtual-model/openai/gpt-4
display_name: GPT-4
description: OpenAI's most capable model
model_type: chat
provider_config: {}
```

```bash
# Create connection
orchestrate connections add -a openai_creds
orchestrate connections configure -a openai_creds --env draft -k key_value -t team
orchestrate connections set-credentials -a openai_creds --env draft -e "api_key=YOUR_KEY"

# Import model
orchestrate models import --file openai-gpt4.yaml --app-id openai_creds
```

### Anthropic Claude
```yaml
spec_version: v1
kind: model
name: virtual-model/anthropic/claude-3-5-sonnet-20241022
display_name: Claude 3.5 Sonnet
description: Anthropic's most intelligent model
model_type: chat
provider_config: {}
```

```bash
# Create connection
orchestrate connections add -a anthropic_creds
orchestrate connections configure -a anthropic_creds --env draft -k key_value -t team
orchestrate connections set-credentials -a anthropic_creds --env draft -e "api_key=YOUR_KEY"

# Import model
orchestrate models import --file anthropic-claude.yaml --app-id anthropic_creds
```

### Azure OpenAI
```yaml
spec_version: v1
kind: model
name: virtual-model/azure-openai/gpt-4
display_name: Azure GPT-4
description: GPT-4 hosted on Azure
model_type: chat
provider_config:
  azure_endpoint: "https://your-resource.openai.azure.com"
  api_version: "2024-02-15-preview"
  azure_deployment: "gpt-4"
```

```bash
# Create connection
orchestrate connections add -a azure_creds
orchestrate connections configure -a azure_creds --env draft -k key_value -t team
orchestrate connections set-credentials -a azure_creds --env draft -e "api_key=YOUR_KEY"

# Import model
orchestrate models import --file azure-gpt4.yaml --app-id azure_creds
```

## Security Best Practices

### Credential Management
- ❌ **Never** hardcode API keys in YAML files
- ✅ **Always** use watsonx Orchestrate connections for credentials
- ✅ Use **team** credentials for shared access, **member** for individual
- ✅ Rotate API keys regularly
- ✅ Use environment variables in deployment scripts
- ✅ Audit credential access and usage

### Access Control
- ✅ Implement least privilege access
- ✅ Separate draft and live credentials
- ✅ Use different API keys per environment
- ✅ Monitor and log all model access
- ✅ Implement rate limiting where appropriate

### Data Privacy
- ✅ Review provider data retention policies
- ✅ Ensure compliance with data residency requirements
- ✅ Use providers with appropriate certifications (SOC 2, GDPR, etc.)
- ✅ Implement data masking for sensitive information
- ✅ Document data flows for audit purposes

## Troubleshooting

### Connection Errors
**Symptoms**: 401 Unauthorized, 403 Forbidden, Connection timeout

**Solutions**:
- Verify API key is correct and active
- Check connection configuration matches provider requirements
- Ensure credentials are set for correct environment
- Verify network connectivity to provider
- Check for API rate limits or quota exhaustion

### Model Not Found
**Symptoms**: Model not appearing in list, 404 Not Found

**Solutions**:
- Verify model was imported successfully
- Check you're in the correct environment (draft/live)
- Ensure model name follows `virtual-model/provider/model` format
- Verify connection is properly associated with model
- Check for typos in model name

### Policy Issues
**Symptoms**: Requests not load balancing, Fallback not triggering

**Solutions**:
- Verify all models in policy are available
- Check strategy configuration (loadbalance vs fallback)
- Ensure `strategy-on-code` includes correct HTTP codes
- Test individual models before testing policy
- Review policy weights and distribution

### Runtime Errors
**Symptoms**: 500 Internal Server Error, Timeout errors

**Solutions**:
- Check provider status page for outages
- Verify model supports requested features
- Review request parameters for compatibility
- Check timeout settings in `provider_config`
- Enable retry logic in policy configuration

## Advanced Topics

### Custom Provider Integration
Integrate models from providers not in the standard list:
- Ensure provider uses OpenAI-compatible API
- Configure `custom_host` in `provider_config`
- Test authentication mechanism
- Verify response format compatibility

### Multi-Region Deployments
Deploy models across multiple regions for latency optimization:
- Set up separate connections per region
- Configure models with region-specific endpoints
- Use load balancing policy to distribute by region
- Monitor latency and adjust weights

### Cost Monitoring & Optimization
Track and optimize LLM usage costs:
- Use cheaper models for simple tasks
- Implement caching where appropriate
- Set up usage alerts and quotas
- Route to cost-effective providers via policies
- Monitor token usage per model

## Project File Structure

```
project-root/
├── .bob/
│   ├── custom_modes.yaml              # Mode configuration
│   ├── README.md                      # This file
│   └── rules-agent-model-gateway/     # Mode instruction files
│       ├── 1_workflow.xml
│       ├── 2_best_practices.xml
│       ├── 3_provider_patterns.xml
│       ├── 4_adk_commands.xml
│       ├── 5_examples.xml
│       ├── 6_validation.xml
│       └── 7_deployment_script_template.xml
├── config/                            # Generated by mode
│   ├── connections.yaml
│   ├── openai-gpt4.yaml
│   ├── anthropic-claude.yaml
│   └── policy-loadbalance.yaml
├── scripts/                           # Generated by mode
│   ├── deploy-openai-gpt4.sh
│   ├── deploy-multi-provider.sh
│   ├── rollback-openai-gpt4.sh
│   └── validate-openai-gpt4.sh
└── plan.md                            # Generated by mode
```

## Resources

### Documentation
- [watsonx Orchestrate ADK Documentation](https://developer.watson-orchestrate.ibm.com)
- [AI Gateway Guide](https://developer.watson-orchestrate.ibm.com/llm/managing_llm)
- [Model Policies](https://developer.watson-orchestrate.ibm.com/llm/model_policies)
- [Connections Guide](https://developer.watson-orchestrate.ibm.com/connections/build_connections)

### MCP Server
- **Name**: watsonx-orchestrate-adk-docs
- **Description**: MCP server for querying latest ADK documentation
- **Usage**: Automatically queried by the mode at each workflow step

### Support
- Use the mode's built-in troubleshooting guides
- Query ADK documentation via MCP server
- Check provider status pages for outages
- Review watsonx Orchestrate community forums

## Version History

### v1.0.0 (2026-03-18)
- ✨ Initial release
- ✨ Support for 12+ LLM providers
- ✨ Interactive discovery workflow
- ✨ Comprehensive documentation
- ✨ Security-focused design
- ✨ Deployment automation
- ✨ Validation and troubleshooting guides

## Contributing

We welcome contributions to improve this mode:
- **Improvements**: Suggestions for enhancing the mode
- **New Providers**: Add support for additional LLM providers
- **Bug Reports**: Report issues with specific provider configurations
- **Documentation**: Help improve examples and troubleshooting guides

## License

This mode is part of the Bob project and follows the same license.

---

**Ready to integrate your first model?** Switch to the Agent Model Gateway mode and let's get started! 🚀