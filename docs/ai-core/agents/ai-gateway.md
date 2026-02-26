# Agent Gateway

A unified gateway for selecting the right LLM model and securely accessing the right tools and agents across your enterprise.

## Why It Matters for Enterprises

- **Model compliance and governance** - Customers have clearance to only use specific approved models
- **Fine-tuned model support** - Customers have a need to use their fine-tuned models for agents
- **Centralized control** - Manage all model access, policies, and telemetry from one place
- **Seamless integration** - Connect to multiple providers without rewriting applications
- **ContextForge** Federates MCP servers, A2A agents, and REST APIs into one governed endpoint

## Supported LLM Providers

The AI Gateway provides unified access to multiple foundation model providers:

**Enterprise Platforms:**
- IBM watsonx.ai
- AWS Bedrock
- Azure OpenAI

**Leading AI Providers:**
- OpenAI
- Anthropic
- Google (Gemini)

**Open Source & Specialized:**
- Mistral
- Ollama

## Key Features & Capabilities

### Model Gateway
- **Unified API & orchestration layer** for multiple foundation models
- **Seamless model switching, routing, and failover** without rewriting applications
- **Select the model of choice** based on use case requirements
- **Configure models** with parameters, model policies, and custom settings

### Enterprise Controls
- **Enforce approved models and tools** across the organization
- **Central telemetry and observability** for all AI traffic
- **Consistent governance** across hybrid and multi-cloud deployments
- **Policy enforcement** for security, compliance, and cost management

### Advanced Capabilities
- **Unified credential storage** - Secure management of API keys and tokens
- **Load balancing** - Distribute requests across multiple model instances
- **Failover and retries** - Automatic fallback to alternative models
- **Custom API settings** - Fine-tune request parameters per model
- **Usage tracking** - Monitor consumption, costs, and performance metrics

### Legacy Modernization
- **Virtualize existing REST/gRPC services** as MCP tools
- **No need to rewrite agents** - Integrate legacy systems seamlessly
- **Gradual migration path** from traditional APIs to modern AI workflows

### ContextForge
- **Federation** Single catalog/entry point across multiple MCP and REST services
- **REST-to-MCP** Adapter: Virtualize REST APIs as MCP-compliant tools
- **gRPC Translation**: Reflection-based discovery and translation to MCP
- **Multi-Transport** HTTP, JSON-RPC, WebSocket, SSE, stdio, streamable-HTTP
- **Built-in Security** Auth, rate limiting, retries, OAuth token support

## How It Works

1. **Select the model** - Choose the most suitable model for your agent or use case
2. **Configure policies** - Set parameters, rate limits, and governance rules
3. **Route requests** - AI Gateway handles routing, authentication, and failover
4. **Monitor and optimize** - Track usage, performance, and costs through central telemetry

## Use Cases

### Model Compliance & Governance
- **Approved model enforcement** - Ensure only certified models are used in production
- **Audit and compliance** - Track which models are used for which purposes
- **Regional restrictions** - Route to compliant models based on data residency requirements

### Fine-Tuned Model Deployment
- **Custom model integration** - Deploy and manage organization-specific fine-tuned models
- **A/B testing** - Compare performance between base and fine-tuned models
- **Gradual rollout** - Route percentage of traffic to new model versions

### Multi-Provider Model Management
- **Cost optimization** - Route to most cost-effective model for each task
- **Performance optimization** - Select fastest or most accurate model per use case
- **Vendor diversification** - Avoid lock-in by supporting multiple providers

### Legacy System Integration
- **API modernization** - Expose legacy systems as AI-accessible tools
- **Hybrid workflows** - Combine traditional APIs with modern AI agents
- **Incremental transformation** - Modernize systems without full rewrites

## Github Repository
Get started with [Agents gateway building blocks](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/agents/agent-gateway)