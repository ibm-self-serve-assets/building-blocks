# IBM WatsonX Orchestrate AI Gateway: Integrating Third-Party LLMs

IBM WatsonX Orchestrate provides powerful capabilities for integrating third-party Large Language Models (LLMs) through its **AI Gateway** system. This enables organizations to leverage a wide range of AI models from leading providers while maintaining the orchestration and management capabilities of the WatsonX platform.

## IBM's AI Gateway Capabilities

The AI Gateway system in WatsonX Orchestrate offers:

- **Multi-Provider Support**: Integration with 10+ leading AI providers including OpenAI, Azure OpenAI, AWS Bedrock, Anthropic, Google, watsonx.ai, Mistral, OpenRouter, and Ollama
- **Secure Credential Management**: API keys and sensitive configuration stored securely in connections
- **Advanced Routing Policies**: Load balancing, fallback mechanisms, and retry strategies across multiple models
- **Flexible Configuration**: Custom endpoints, timeouts, and provider-specific settings
- **Enterprise-Grade Security**: Secure handling of API credentials and model configurations

For comprehensive documentation on all supported providers and advanced features, see the [IBM WatsonX Orchestrate AI Gateway Documentation](https://developer.watson-orchestrate.ibm.com/llm/managing_llm#supported-providers).

## Example: Integrating OpenAI Models

This guide demonstrates how to integrate OpenAI models into WatsonX Orchestrate using the AI Gateway. This example can be adapted for any of the supported providers.

### Step 1: Configure Provider Settings

Create a JSON configuration for the OpenAI provider. The `api_key` is excluded for security and will be stored separately in a connection:

```json
{
  "custom_host": "https://api.openai.com/v1",
  "request_timeout": 500
}
```

### Step 2: Secure API Key Storage

Store your OpenAI API key securely in a WatsonX Orchestrate connection:

```bash
# Create a connection for OpenAI credentials
orchestrate connections add -a openai_creds

# Configure the connection as key-value type
orchestrate connections configure -a openai_creds --env draft -k key_value -t team

# Store the API key securely
orchestrate connections set-credentials -a openai_creds --env draft -e "api_key=your_openai_api_key"
```

**Security Note**: Replace `your_openai_api_key` with your actual OpenAI API key (format: `sk-...`). The connection system ensures credentials are stored securely and encrypted.

### Step 3: Register the OpenAI Model

Add the OpenAI model to WatsonX Orchestrate using the AI Gateway:

```bash
orchestrate models add \
  --name openai/gpt-4 \
  --app-id openai_creds \
  --provider-config '{"custom_host": "https://api.openai.com/v1", "request_timeout": 5000}' \
  --type chat
```

**Parameters Explained**:
- `--name openai/gpt-4`: Specifies the provider (`openai`) and model name (`gpt-4`)
- `--app-id openai_creds`: Links to the connection containing the API key
- `--provider-config`: JSON configuration for custom settings
- `--type chat`: Indicates this is a chat-completion model

**Alternative Models**: Replace `gpt-4` with other OpenAI models like `gpt-3.5-turbo`, `gpt-4-turbo`, etc.

### Step 4: Verify Integration

Confirm the model was successfully added to your WatsonX Orchestrate environment:

```bash
orchestrate models list
```
<img width="875" alt="image" src="https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/f5f65523-5667-4949-8c3e-4a106c9bd810">

**Model shows up on the model drop down in the Orchestrate**
![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/ab9e3475-2b9f-4b6d-973d-b7860bc056d6)


## Advanced AI Gateway Features

### Model Policies for Load Balancing and Fallback

WatsonX Orchestrate supports sophisticated model policies for enterprise scenarios:

```bash
# Create a load-balancing policy between multiple models
orchestrate models policy add \
  --name balanced_gpt \
  --model openai/gpt-4 \
  --model openai/gpt-3.5-turbo \
  --strategy loadbalance \
  --retry-on-code 503 \
  --retry-attempts 3
```

### Provider-Specific Configurations

Each supported provider has specific configuration options:

- **Azure OpenAI**: Requires `azure_resource_name`, `azure_deployment_id`, `azure_api_version`
- **AWS Bedrock**: Supports AWS IAM roles, regions, and Bedrock-specific models
- **watsonx.ai**: Integrates with IBM's watsonx.ai platform using Space ID, Project ID, or Deployment ID
- **Anthropic**: Supports Claude models with version and beta features

## Benefits of IBM WatsonX Orchestrate AI Gateway

1. **Unified Management**: Manage multiple AI providers from a single platform
2. **Enterprise Security**: Secure credential management and access controls
3. **Scalability**: Load balancing and failover capabilities across models
4. **Flexibility**: Support for custom endpoints and provider-specific features
5. **Integration**: Seamless integration with WatsonX Orchestrate agents and tools

## Next Steps

- Explore [all supported providers](https://developer.watson-orchestrate.ibm.com/llm/managing_llm#supported-providers) in the official documentation
- Learn about [model policies](https://developer.watson-orchestrate.ibm.com/llm/managing_llm#configuring-model-policies) for advanced routing
- Discover [connection management](https://developer.watson-orchestrate.ibm.com/connections/overview) for secure credential handling
- Build agents that leverage multiple AI providers through the AI Gateway

This integration capability demonstrates IBM's commitment to providing flexible, enterprise-grade AI orchestration that works with the tools and models your organization already uses.
