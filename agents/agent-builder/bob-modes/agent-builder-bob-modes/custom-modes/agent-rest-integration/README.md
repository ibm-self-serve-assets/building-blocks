# 🔗 Agent-Integrate Mode

A comprehensive custom mode for Bob that helps developers integrate IBM watsonx Orchestrate agents into their applications via REST API.

## Overview

The Agent-Integrate mode provides end-to-end support for watsonx Orchestrate integration, from agent creation to production-ready code deployment. It handles authentication, connection testing, code generation, and troubleshooting across all deployment platforms (IBM Cloud, AWS, AWS GovCloud, and On-premises).

## Features

### 🎯 Core Capabilities

- **End-to-End Integration Workflow**
  - Agent creation using MCP ADK documentation
  - Platform detection and configuration
  - Credential setup and management
  - Connection testing and validation
  - Production-ready code generation
  - Testing and deployment

- **Multi-Platform Support**
  - IBM Cloud (IAM authentication)
  - AWS (JWT authentication)
  - AWS GovCloud (JWT authentication)
  - On-premises (Zen API key)

- **Code Generation**
  - Python integration libraries
  - Node.js/Express servers
  - Web UIs (HTML/CSS/JS, React)
  - CLI applications
  - Connection test scripts
  - Deployment scripts

- **Agent Creation**
  - Uses watsonx-orchestrate-adk-docs MCP server
  - Generates agent configuration files (YAML/JSON)
  - Creates deployment scripts
  - Guides through deployment process

### 🛠️ Integration Types

1. **Simple API Testing** - Python/Node.js scripts for testing REST APIs
2. **Backend Servers** - Express/Flask servers with agent endpoints
3. **Full-Stack Applications** - Complete web apps with frontend and backend
4. **Integration Libraries** - Reusable client libraries for any application
5. **CLI Tools** - Command-line interfaces for agent interaction

## Mode Structure

### Configuration Files

```
.bob/
├── custom_modes.yaml              # Mode configuration
└── rules-agent-integrate/         # Mode instructions
    ├── 1_workflow.xml             # Main workflow and phases
    ├── 2_code_templates.xml       # Code generation templates
    ├── 3_troubleshooting_best_practices.xml  # Troubleshooting guide
    ├── 4_ui_templates_examples.xml           # UI templates and examples
    └── README.md                  # This file
```

### Instruction Files

#### 1. `1_workflow.xml` (350+ lines)
5-phase integration workflow with greeting protocol, initial assessment, credential setup, connection testing, code generation, and testing/validation. Includes special cases, error recovery, and MCP-based agent creation.

#### 2. `2_code_templates.xml` (680+ lines)
Production-ready templates for connection tests, Python integration library (`WatsonxOrchestrateClient`), and Node.js/Express server with full API endpoints and middleware.

#### 3. `3_troubleshooting_best_practices.xml` (600+ lines)
Troubleshooting guide for authentication, connection, agent, and code issues. Best practices for security, error handling, performance, and code quality. API documentation reference.

#### 4. `4_ui_templates_examples.xml` (680+ lines)
Web UI templates (HTML/CSS/JS, React), complete examples (Python CLI, Node.js full-stack), README templates, and usage scenarios for different integration patterns.

## Prerequisites

- Bob AI with MCP support enabled
- IBM watsonx Orchestrate access
- Python 3.10+ or Node.js 16+ (depending on integration type)
- `watsonx-orchestrate-adk-docs` MCP server configured (see `.bob/mcp.json`)

---

## Setup & Installation

1. **Download the file `agent-rest-integration.zip`**
   
2. **Uncompress the .zip file. You should see a folder named `agent-rest-integration`, Open this folder as root folder in the Bob application**

3. **That's it!** — The `🔗 Agent-Integrate` mode will automatically appear in Bob's mode selector, ready to use.

---

## How to Use

1. Select **`🔗 Agent-Integrate`** from the Bob mode selector (or say "I need to integrate a watsonx Orchestrate agent")
2. Say "hi" to see all capabilities, or describe your integration needs
3. Bob will guide you through the 5-phase workflow:
   - **Phase 1**: Initial Assessment (agent status, platform, requirements)
   - **Phase 2**: Credential Setup (.env configuration)
   - **Phase 3**: Connection Testing (validate API connectivity)
   - **Phase 4**: Code Generation (integration code, UI if needed)
   - **Phase 5**: Testing & Validation (test and deploy)
4. Follow Bob's prompts to provide agent details and preferences
5. Review and test the generated integration code
6. Deploy your application

---

**Note:**
- Get the project — clone this repo or download the `.bob` folder into your project directory.
- Open Bob and open the project folder (the one containing `.bob/`) in Bob. Important: When starting to use this Bob mode, your project folder should contain only the `.bob` folder downloaded from this custom mode. No additional files or folders should be present in the project folder to ensure Bob does not receive unwanted context while using this mode.

---

## Common Workflows

### 1. Create Agent and Integrate
```
User: "I want to create a new agent and integrate it into my app"
```
Bob uses MCP to search ADK docs, generates agent config, creates deployment scripts, sets up credentials, tests connection, and generates integration code.

### 2. Integrate Existing Agent
```
User: "I have an agent deployed, need to integrate it"
```
Bob asks for agent ID, detects platform, sets up .env, tests connection, generates integration code, and validates.

### 3. Create Web Application
```
User: "Create a web app with chat interface for my agent"
```
Bob asks about UI preferences, gets agent details, sets up credentials, tests connection, generates backend server and frontend UI, creates README, and tests end-to-end.

### 4. Troubleshoot Integration
```
User: "My integration isn't working"
```
Bob diagnoses the issue, provides troubleshooting steps, tests connection, checks credentials, and directs to API documentation if needed.

## Workflow Phases

### Phase 1: Initial Assessment
- Determine if agent exists or needs creation
- Identify deployment platform
- Understand integration requirements

### Phase 2: Credential Setup
- Create/verify .env file
- Configure platform-specific credentials
- Ensure security best practices

### Phase 3: Connection Testing
**CRITICAL** - Always test before building
- Generate platform-specific test script
- Validate API connectivity
- Diagnose connection issues

### Phase 4: Code Generation
- Generate authentication code
- Create agent interaction functions
- Build UI if requested
- Include error handling and logging

### Phase 5: Testing & Validation
- Create test cases
- Run integration tests
- Provide usage documentation

## Special Features

### Agent Creation with MCP

When users need to create agents, the mode uses the `watsonx-orchestrate-adk-docs` MCP server:

```xml
<mcp_usage>
  <server>watsonx-orchestrate-adk-docs</server>
  <tool>search_ibm_watsonx_orchestrate_adk</tool>
  <example_queries>
    - "create agent from scratch"
    - "agent configuration YAML"
    - "deploy agent to watsonx orchestrate"
    - "agent skills and tools"
  </example_queries>
</mcp_usage>
```

### API Documentation Reference

When troubleshooting complex issues, the mode directs users to:

**🔗 [IBM watsonx Orchestrate REST API Documentation](https://developer.ibm.com/apis/catalog/watsonorchestrate--custom-assistants/Introduction)**

This provides:
- Complete endpoint documentation
- Interactive API explorer
- Detailed parameter descriptions
- Request/response examples
- Error code explanations

### Platform Detection

The mode intelligently detects or asks about the deployment platform:

- **IBM Cloud**: Uses IAM authentication
- **AWS/AWS GovCloud**: Uses JWT authentication
- **On-premises**: Uses Zen API key

### Security Best Practices

All generated code includes:
- Environment variable usage (never hardcoded credentials)
- Token management and refresh
- Input validation
- Error handling
- Secure logging (masked credentials)
- HTTPS enforcement

## Code Examples

### Python Integration

```python
from watsonx_client import WatsonxOrchestrateClient

# Initialize client (reads from .env)
client = WatsonxOrchestrateClient()

# Send message to agent
response = client.send_message(
    agent_id="your-agent-id",
    message="Hello, how can you help?"
)

print(response)
```

### Node.js Integration

```javascript
const WatsonxClient = require('./watsonx-client');

const client = new WatsonxClient();

// Send message to agent
const response = await client.sendMessage(
  'your-agent-id',
  'Hello, how can you help?'
);

console.log(response);
```

### Web UI

The mode generates complete, production-ready web interfaces with:
- Modern, responsive design
- Real-time chat functionality
- Loading states and error handling
- Connection to backend API

## Environment Configuration

### IBM Cloud

```env
WATSONX_PLATFORM=ibm_cloud
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_INSTANCE_ID=your_instance_id
WATSONX_REGION=us-south
```

### AWS

```env
WATSONX_PLATFORM=aws
WATSONX_API_KEY=your_aws_api_key
WATSONX_INSTANCE_ID=your_instance_id
WATSONX_REGION=us-east-1
```

### On-Premises

```env
WATSONX_PLATFORM=onprem
WATSONX_USERNAME=your_username
WATSONX_API_KEY=your_api_key
WATSONX_HOST=your_host
WATSONX_PORT=443
WATSONX_NAMESPACE=your_namespace
WATSONX_INSTANCE_ID=your_instance_id
```

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Verify credentials in .env
   - Check platform selection
   - Test network connectivity
   - Run connection test script

2. **Authentication Errors**
   - Regenerate API key
   - Check token expiration
   - Verify platform matches deployment

3. **Agent Not Found**
   - Verify agent ID
   - Check if agent is deployed
   - Confirm instance ID

4. **Unresolved Issues**
   - Refer to [API Documentation](https://developer.ibm.com/apis/catalog/watsonorchestrate--custom-assistants/Introduction)
   - Check for platform-specific issues
   - Review error messages carefully

## Best Practices

### Security
- ✅ Use environment variables for credentials
- ✅ Never commit .env files to version control
- ✅ Rotate API keys regularly (every 90 days)
- ✅ Use different keys for dev/staging/production
- ✅ Implement proper token refresh logic

### Performance
- ✅ Use connection pooling
- ✅ Cache frequently accessed data
- ✅ Implement retry logic with exponential backoff
- ✅ Use async operations for long-running tasks

### Code Quality
- ✅ Include comprehensive error handling
- ✅ Add logging for debugging
- ✅ Write clear documentation
- ✅ Test all integration points
- ✅ Follow platform-specific best practices

## Resources

### Official Documentation
- [IBM watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [REST API Reference](https://developer.ibm.com/apis/catalog/watsonorchestrate--custom-assistants/Introduction)
- [IBM Cloud IAM Documentation](https://cloud.ibm.com/docs/account?topic=account-iamoverview)

### Integration Guide
- [watsonx Orchestrate REST API Integration Guide](../watsonx-orchestrate-rest-api-integration-guide.md) - Comprehensive guide in this repository


## Version History

- **v1.0** (2026-04-29)
  - Initial release
  - End-to-end integration workflow
  - Multi-platform support
  - Agent creation with MCP
  - Comprehensive code templates
  - Troubleshooting guide
  - API documentation reference
