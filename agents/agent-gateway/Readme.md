# AI Gateway

## Overview

The **AI Gateway** building block provides a unified gateway for selecting the right LLM model and securely accessing the right tools and agents. It serves as a centralized orchestration layer that enables seamless integration with multiple foundation models and external systems while maintaining enterprise-grade security and governance.

## What It Does

- **Model Gateway**: Unified API and orchestration layer for multiple foundation models (OpenAI, Anthropic, Google, IBM watsonx.ai)
- **Seamless Model Switching**: Route and failover between models without rewriting applications
- **ContextForge**: Federates MCP servers, A2A agents, and REST APIs into one governed endpoint
- **Legacy Modernization**: Virtualize existing REST/gRPC services as MCP tools without rewriting agents
- **Enterprise Controls**: Enforce approved models/tools with central telemetry and consistent governance

## Why Use It?

- ✅ **Model Flexibility**: Choose the right model for the right use case with approved, fine-tuned options
- ✅ **Centralized Access**: Unify discovery, auth, rate-limits, and observability in one place
- ✅ **Legacy Integration**: Modernize existing systems by virtualizing REST/gRPC into MCP-compliant tools
- ✅ **Enterprise Governance**: Maintain security, compliance, and control across hybrid deployments

## Key Components

### Model Gateway
Select and configure the optimal model for each use case:
- Access to approved models only
- Support for fine-tuned models
- Configurable model parameters and policies
- Multi-provider support (OpenAI, Anthropic, Google, IBM watsonx.ai, and more)

### ContextForge
A Model Context Protocol (MCP) Gateway, Proxy, and Registry that provides:
- **Federation**: Single catalog/entry point across multiple MCP and REST services
- **REST-to-MCP Adapter**: Virtualize REST APIs as MCP-compliant tools
- **gRPC Translation**: Reflection-based discovery and translation to MCP
- **Multi-Transport**: HTTP, JSON-RPC, WebSocket, SSE, stdio, streamable-HTTP
- **Built-in Security**: Auth, rate limiting, retries, OAuth token support

**GitHub Repository**: [IBM MCP Context Forge](https://github.com/IBM/mcp-context-forge)

## How to Use

### 1. Explore Pre-existing Assets
Browse guides and examples to understand AI Gateway capabilities:
- Review the [Model Gateway Guide](./model-gateway-guide/) for step-by-step integration instructions
- Study model configuration and policy examples

### 2. Configure Your Gateway
Set up model gateway and ContextForge for your use case:
- Select and configure approved models
- Set up MCP server federation
- Configure authentication and rate limiting
- Implement routing policies and failover strategies

## Bob Modes for AI Gateway

> 🚧 **Coming Soon**: Documentation for Agent Gateway Bob Modes will be available here.

## Guides & Documentation

- [Model Gateway Guide](./model-gateway-guide/) - Complete guide for integrating third-party LLMs with watsonx Orchestrate

## Assets & Resources

- [IBM MCP Context Forge](https://github.com/IBM/mcp-context-forge) - Open-source MCP Gateway, Proxy, and Registry
- [Model Gateway Guide](./model-gateway-guide/) - Integration examples for OpenAI, Anthropic, Google Gemini, and more

---

## Related Building Blocks

- [Agent Builder](../agent-builder/)
- [Multi-Agent Orchestration](../multi-agent-orchestration/)
