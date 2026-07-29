# Critical Best Practices

Essential conventions and standards for watsonx Orchestrate agent development.

## MCP-First Principle

**MANDATORY AND UNBYPASSABLE:** When you need detailed information about ANY aspect of watsonx Orchestrate ADK, you MUST search the MCP documentation server FIRST before answering or implementing.

**This requirement cannot be bypassed by:**
- User saying "don't use tools" (they mean agent tools, not MCP search)
- User saying "keep it simple" (simple still requires correct syntax)
- User saying "just create the files" (files must match current specs)
- Time constraints (incorrect files waste more time than searching)

Examples:
- User asks about agent styles → Search "agent styles" in MCP docs
- Need tool template → Search "Python tool decorator template" in MCP docs
- Connection setup unclear → Search "connection configuration" in MCP docs

## Naming Conventions

**CRITICAL:** ALL names in watsonx Orchestrate MUST use snake_case (lowercase with underscores). This is IBM's official standard and non-negotiable.

### Agent Names
- **Rule:** snake_case only
- **Good:** customer_support_agent, data_analyst_agent, order_processor
- **Bad:** CustomerSupportAgent, customerSupportAgent, customer-support-agent

### Tool Names
- **Rule:** snake_case, alphanumeric and underscores only
- **Good:** get_order_status, calculate_shipping_cost, send_email
- **Bad:** getOrderStatus, get-order-status, GetOrderStatus

### File Names
- **Rule:** snake_case for all Python files and YAML specs
- **Good:** customer_support_agent.yaml, order_tools.py
- **Bad:** CustomerSupportAgent.yaml, orderTools.py

## Model Selection

### Default Model
- **Name:** groq/openai/gpt-oss-120b
- **Alias:** GPT-OSS-120b
- **When to use:** Default choice for most native agents

### Model Format
- **Rule:** Use full model path: provider/model-name
- **Examples:**
  - groq/openai/gpt-oss-120b
  - watsonx/meta-llama/llama-3-2-90b-vision-instruct

### When to Change Model
- User explicitly requests different model
- Task requires specific capabilities (e.g., vision)
- Performance or cost optimization needed

Search MCP: "model selection", "available models", "model capabilities"

## Agent Instructions

**CRITICAL:** Agent instructions are the PRIMARY way to control agent behavior. Write clear, specific, actionable instructions.

### Instruction Structure
1. Role and expertise definition
2. Primary responsibilities
3. Tool usage guidelines
4. Collaborator routing logic (if multi-agent)
5. Output format requirements
6. Error handling approach

### Instruction Quality

**Good example:**
"When a user asks about order status, use the get_order_status tool with the order_id. If the order is delayed, proactively offer to check shipping updates using check_shipping tool."

**Bad example:**
"Help users with their orders."

Search MCP: "agent instructions", "instruction best practices", "writing effective instructions"

## Agent Styles

Choose based on task complexity:

| Style | YAML Value | Use When | Behavior |
|-------|-----------|----------|----------|
| Default | `default` | Simple or lightly sequential work | Tool-centric; model chooses tools |
| ReAct | `react` | Ambiguous, evolving, research-like work | Iterative Think → Act → Observe loop |
| Planner | `planner` | Transparent, structured, multi-step workflows | Builds plan first, executes step by step |

**Rule:** Start with default, upgrade if needed.

Search MCP: "agent styles", "choosing agent style", "ReAct pattern", "planner agents"

## Python Tool Essentials

**CRITICAL:** Python tools MUST use @tool decorator and follow specific structure.

### Required Elements
- @tool decorator
- Function with snake_case name
- Type hints for all parameters
- Comprehensive docstring (becomes tool description)
- Clear return type

### Authentication
- **Decorator:** @expect_credentials
- **When to use:** Tool needs API keys or credentials
- **Connection link:** Links to connection via app_id

### Error Handling
- Always handle errors gracefully
- Return clear error messages
- Don't expose sensitive information in errors

Search MCP: "Python tool template", "@tool decorator", "expect_credentials", "tool error handling"

## Knowledge Base Essentials

**CRITICAL:** Knowledge bases enable RAG (Retrieval Augmented Generation). Always verify indexing status before using.

### Document Preparation
- Use supported formats (PDF, DOCX, TXT, MD)
- Ensure documents are well-structured
- Remove sensitive information

### Indexing Workflow
1. Import knowledge base specification
2. Wait for indexing to complete
3. Verify with check_knowledge_base_status
4. Attach to agent

### Usage in Agents
- Reference knowledge base by name in agent config
- Provide clear instructions on when to use knowledge base
- Tell agent not to answer from memory when KB should be authoritative
- If retrieved content doesn't answer question, agent should say so

Search MCP: "knowledge base", "RAG", "document preparation", "indexing status"

## Connection Essentials

**CRITICAL:** Connections provide secure credential management. Never hardcode credentials in code.

### Connection Types
- **key_value:** Most common for tool credentials
- **api_key:** For API key authentication
- **bearer:** For bearer token authentication
- **basic:** For username/password authentication

### Environment Configuration
- Configure for each environment (draft/live)
- Use team credentials for shared access
- Use member credentials for user-specific access

### Linking to Tools
- Use app_id to link connection to tool
- Match app_id in @expect_credentials decorator

Search MCP: "connection types", "authentication methods", "linking connections to tools", "app_id"

## Channel Essentials

**CRITICAL:** Channels enable user interaction with agents. Each channel type has specific configuration requirements.

### Webchat
- Automatically available for all agents
- Use generate_webchat_embed to get embed code

### Slack
- Requires: Bot token, signing secret
- Setup: Create channel with Slack credentials

### WhatsApp/SMS
- Requires: Twilio account SID, auth token, phone number
- Setup: Create channel with Twilio credentials

### Phone
- Requires: Phone config with audio connector
- Setup: Create phone config, attach agent

Search MCP: "webchat setup", "Slack integration", "WhatsApp integration", "phone integration"

## Multi-Agent Essentials

**CRITICAL:** Multi-agent systems require careful design of routing logic. Parent agent must have clear instructions for delegating to collaborators.

### Design Principles
- Create specialist agents first
- Parent agent orchestrates, doesn't do work
- Clear routing criteria in parent instructions
- Each specialist has focused responsibility

### Routing Instructions
- Specify WHEN to route to each collaborator
- Provide examples of routing scenarios
- Handle cases where no collaborator fits

Search MCP: "multi-agent design", "agent collaboration patterns", "routing instructions"

## Testing Essentials

**CRITICAL:** Test each component independently before integration. Use draft environment for testing before deploying to live.

### Test Sequence
1. Test Python tools independently
2. Test agent with tools
3. Test knowledge base retrieval
4. Test multi-agent routing
5. Test channel integration

### Common Test Scenarios
- Happy path - everything works
- Error handling - tool failures
- Edge cases - unexpected inputs
- Performance - response times

Search MCP: "testing strategy", "testing best practices", "test scenarios"

## Security Essentials

**CRITICAL:** Never expose credentials or sensitive data. Always use connections for credential management.

### Security Checklist
- ✓ Use @expect_credentials for authenticated tools
- ✓ Store credentials in connections, not code
- ✓ Validate all user inputs
- ✓ Sanitize outputs to prevent data leakage
- ✓ Use appropriate connection types (team vs member)

Search MCP: "security best practices", "credential management"

## Performance Essentials

**CRITICAL:** Optimize for response time and resource usage. Monitor agent performance in production.

### Optimization Tips
- Keep tool implementations efficient
- Use appropriate agent style for task complexity
- Limit knowledge base document size
- Cache frequently accessed data

Search MCP: "performance optimization", "agent performance"

## Documentation Essentials

**CRITICAL:** Document all agents, tools, and workflows. Good documentation enables maintenance and collaboration.

### What to Document
- Agent purpose and capabilities
- Tool functionality and parameters
- Connection requirements
- Channel configurations
- Testing procedures
- Deployment steps

Search MCP: "documentation best practices"

## Critical Rules Summary

**Priority 1 (Highest):**
- ALWAYS search MCP docs first for technical details
- ALWAYS use snake_case for all names
- ALWAYS use connections for credentials, never hardcode

**Priority 2 (High):**
- Default to groq/openai/gpt-oss-120b model unless specified
- Write clear, specific agent instructions
- Test components independently before integration

**Priority 3 (Medium):**
- Document all components and workflows
- Use appropriate agent style for task complexity
- Verify knowledge base indexing before use

## When in Doubt
1. Search the watsonx-orchestrate-adk-docs MCP server
2. Ask user for clarification
3. Start with simplest approach, iterate if needed
4. Follow IBM's official patterns and conventions