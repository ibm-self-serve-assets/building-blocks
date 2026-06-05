# AI Gateway Model Integration

## Overview

Integrate third-party LLM models into watsonx Orchestrate via the Agent Model Gateway. This enables using models from OpenAI, Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, and other providers.

## Critical First Step

**ALWAYS search ADK documentation before implementation:**

```
Use: search_ibm_watsonx_orchestrate_adk
Query: "AI Gateway model integration" or provider-specific queries
```

This ensures you have the latest syntax, correct field names, and working examples.

## Interactive Workflow

### Step 1: Choose Provider

Select your LLM provider:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus/Haiku)
- Google Gemini (Gemini 1.5 Pro/Flash)
- Azure OpenAI (GPT-4, GPT-3.5)
- AWS Bedrock (Claude, Llama, Mistral)
- Mistral AI
- Groq
- Ollama (local models)
- watsonx.ai

### Step 2: Gather Credentials

Collect required information:
- API key or access token
- Endpoint URL (if applicable)
- Model identifiers
- Region (for cloud providers)

### Step 3: Create Connection

Use ADK CLI to create connection:

```bash
# Create connection
orchestrate connections add -a <connection-name>

# Configure for both environments
for env in draft live; do
    orchestrate connections configure \
        -a <connection-name> \
        --env $env \
        --type team \
        --kind key_value
    
    orchestrate connections set-credentials \
        -a <connection-name> \
        --env $env \
        -e "API_KEY=<your-api-key>"
done
```

### Step 4: Add Model Configuration

Create model YAML configuration based on provider (see Provider Templates below).

### Step 5: Import Model

```bash
orchestrate models add -f model-config.yaml
```

### Step 6: Verify Model

```bash
# List models
orchestrate models list

# Test model
orchestrate models test <model-name>
```

### Step 7: Use in Agent

Reference model in agent configuration:

```yaml
spec_version: v1
kind: agent
name: my_agent
model: <model-name>  # Your imported model
description: Agent using third-party LLM
```

## Provider Templates

### OpenAI

```yaml
spec_version: v1
kind: model
name: gpt-4-turbo
provider: openai
model_id: gpt-4-turbo-preview
model_type: chat
connections:
  - openai_connection
config:
  temperature: 0.7
  max_tokens: 4096
```

### Anthropic

```yaml
spec_version: v1
kind: model
name: claude-3-5-sonnet
provider: anthropic
model_id: claude-3-5-sonnet-20241022
model_type: chat
connections:
  - anthropic_connection
config:
  temperature: 0.7
  max_tokens: 8192
```

### Google Gemini

```yaml
spec_version: v1
kind: model
name: gemini-1-5-pro
provider: google
model_id: gemini-1.5-pro
model_type: chat
connections:
  - google_connection
config:
  temperature: 0.7
  max_output_tokens: 8192
```

### Azure OpenAI

```yaml
spec_version: v1
kind: model
name: azure-gpt-4
provider: azure_openai
model_id: gpt-4
deployment_name: my-gpt4-deployment
endpoint: https://my-resource.openai.azure.com
model_type: chat
connections:
  - azure_connection
config:
  temperature: 0.7
  max_tokens: 4096
```

### AWS Bedrock

```yaml
spec_version: v1
kind: model
name: bedrock-claude
provider: aws_bedrock
model_id: anthropic.claude-3-5-sonnet-20241022-v2:0
region: us-east-1
model_type: chat
connections:
  - aws_connection
config:
  temperature: 0.7
  max_tokens: 8192
```

### Mistral AI

```yaml
spec_version: v1
kind: model
name: mistral-large
provider: mistral
model_id: mistral-large-latest
model_type: chat
connections:
  - mistral_connection
config:
  temperature: 0.7
  max_tokens: 32768
```

### Groq

```yaml
spec_version: v1
kind: model
name: groq-llama
provider: groq
model_id: llama-3.1-70b-versatile
model_type: chat
connections:
  - groq_connection
config:
  temperature: 0.7
  max_tokens: 8192
```

### Ollama (Local)

```yaml
spec_version: v1
kind: model
name: ollama-llama
provider: ollama
model_id: llama3.1:8b
endpoint: http://localhost:11434
model_type: chat
config:
  temperature: 0.7
```

## Model Policies

Create policies for load balancing or fallback:

```yaml
spec_version: v1
kind: model_policy
name: high-availability-policy
description: Load balance across multiple models
models:
  - model: gpt-4-turbo
    weight: 50
  - model: claude-3-5-sonnet
    weight: 50
fallback:
  - gpt-3.5-turbo
```

Import policy:

```bash
orchestrate model-policies add -f policy.yaml
```

Use in agent:

```yaml
model: high-availability-policy  # Use policy instead of single model
```

## Model Types

Only these types are compatible with agents:
- `chat` - Standard chat completion models
- `chat_vision` - Models with vision capabilities

## Environment Management

### Draft vs Live Environments

Models and connections exist in both draft and live:

```bash
# Configure for draft
orchestrate connections set-credentials \
    -a my_connection \
    --env draft \
    -e "API_KEY=draft-key"

# Configure for live
orchestrate connections set-credentials \
    -a my_connection \
    --env live \
    -e "API_KEY=prod-key"
```

### Migration

Move models from draft to live:

```bash
# Export from draft
orchestrate models export <model-name> > model.yaml

# Import to live
orchestrate env set live
orchestrate models add -f model.yaml
```

## Security Best Practices

### Credential Management
- Never hardcode API keys in configurations
- Use environment variables: `${ENV_VAR_NAME}`
- Rotate credentials regularly
- Use separate keys for draft and live

### Access Control
- Limit model access to specific teams
- Use RBAC for model management
- Audit model usage regularly

### Data Privacy
- Understand provider data retention policies
- Use on-premises models for sensitive data
- Implement data masking where appropriate

## Troubleshooting

### Model Not Found
```bash
# List all models
orchestrate models list

# Check model name spelling
# Verify model was imported successfully
```

### Authentication Errors
```bash
# Verify connection credentials
orchestrate connections list

# Test connection
orchestrate connections test -a <connection-name>

# Update credentials if needed
orchestrate connections set-credentials -a <connection-name> --env draft -e "API_KEY=new-key"
```

### Rate Limiting
- Implement retry logic with exponential backoff
- Use model policies for load distribution
- Monitor usage against provider limits

### Model Performance Issues
- Adjust temperature and max_tokens
- Use smaller models for simple tasks
- Implement caching for repeated queries
- Consider model policies for fallback

## ADK CLI Reference

### Models
```bash
# Add model
orchestrate models add -f model.yaml

# List models
orchestrate models list

# Export model
orchestrate models export <model-name>

# Remove model
orchestrate models remove <model-name>

# Test model
orchestrate models test <model-name>
```

### Connections
```bash
# Add connection
orchestrate connections add -a <name>

# Configure connection
orchestrate connections configure -a <name> --env <env> --type team --kind key_value

# Set credentials
orchestrate connections set-credentials -a <name> --env <env> -e "KEY=value"

# List connections
orchestrate connections list

# Test connection
orchestrate connections test -a <name>
```

### Model Policies
```bash
# Add policy
orchestrate model-policies add -f policy.yaml

# List policies
orchestrate model-policies list

# Remove policy
orchestrate model-policies remove <policy-name>
```

## Complete Example

End-to-end setup for OpenAI GPT-4:

```bash
# 1. Create connection
orchestrate connections add -a openai

# 2. Configure for both environments
for env in draft live; do
    orchestrate connections configure \
        -a openai \
        --env $env \
        --type team \
        --kind key_value
    
    orchestrate connections set-credentials \
        -a openai \
        --env $env \
        -e "OPENAI_API_KEY=$OPENAI_API_KEY"
done

# 3. Create model configuration
cat > gpt4-model.yaml <<EOF
spec_version: v1
kind: model
name: gpt-4-turbo
provider: openai
model_id: gpt-4-turbo-preview
model_type: chat
connections:
  - openai
config:
  temperature: 0.7
  max_tokens: 4096
EOF

# 4. Import model
orchestrate models add -f gpt4-model.yaml

# 5. Verify
orchestrate models list | grep gpt-4-turbo

# 6. Create agent using model
cat > agent.yaml <<EOF
spec_version: v1
kind: agent
name: gpt4_agent
model: gpt-4-turbo
description: Agent powered by GPT-4 Turbo
instructions: You are a helpful assistant.
EOF

# 7. Import agent
orchestrate agents import -f agent.yaml
```

## Important Notes

- Always search ADK documentation for latest syntax
- Test in draft environment before deploying to live
- Monitor costs and usage across providers
- Keep credentials secure and rotate regularly
- Use model policies for high availability
- Only `chat` and `chat_vision` types work with agents