# Agent Communication Patterns

## Overview

Enable agents to communicate and collaborate using native collaboration, Agent-to-Agent (A2A) protocol, or external chat APIs.

## A2A Protocol

### Current Version

**Version 0.3.0** - Current supported version  
**Version 0.2.1** - Deprecated, will be removed

**Transport:** JSON-RPC 2.0 over HTTP  
**Provider Format:** `external_chat/A2A/0.3.0`

### Registering A2A Agents

External agents (LangGraph, CrewAI, BeeAI) can be registered as A2A agents.

**YAML Configuration:**
```yaml
spec_version: v1
kind: external
name: news_agent
title: News Agent
nickname: news_agent
provider: external_chat/A2A/0.3.0  # A2A protocol identifier
description: |
  Agent built in LangGraph that searches and analyzes news articles.
  Can fetch latest news, filter by topic, and provide summaries.
tags:
  - news
  - research
api_url: "https://my-agent.example.com/a2a"
auth_scheme: BEARER_TOKEN
auth_config:
  token: "${NEWS_AGENT_TOKEN}"
chat_params:
  sendHistory: true          # Send conversation history
  stream: false              # Use streaming or REST
  pushNotifications: true    # Support async updates
config:
  hidden: false              # Show in UI
  enable_cot: true           # Return chain-of-thought steps
```

**Python Configuration:**
```python
from ibm_watsonx_orchestrate.agent_builder.agents import (
    ExternalAgent, AgentKind, ExternalAgentAuthScheme
)

news_agent = ExternalAgent(
    kind=AgentKind.EXTERNAL,
    name="news_agent",
    title="News Agent",
    nickname="news_agent",
    provider="external_chat/A2A/0.3.0",
    description="Agent built in LangGraph that searches news.",
    tags=['news', 'research'],
    api_url="https://my-agent.example.com/a2a",
    auth_scheme=ExternalAgentAuthScheme.BEARER_TOKEN,
    auth_config={"token": "${NEWS_AGENT_TOKEN}"},
    chat_params={
        "sendHistory": True,
        "stream": False,
        "pushNotifications": True
    },
    config={
        "hidden": False,
        "enable_cot": True
    }
)

# External agents must be used as collaborators
from ibm_watsonx_orchestrate.agent_builder import Agent

supervisor = Agent(
    name="research_supervisor",
    description="Coordinates research tasks",
    collaborators=[news_agent]
)
```

### A2A Configuration Parameters

**sendHistory** (boolean, default: false)
- Whether to send conversation history to external agent
- Enable for agents that need context from previous turns

**stream** (boolean, default: false)
- Use Server-Sent Events streaming or REST calls
- Enable for real-time response streaming

**pushNotifications** (boolean, default: false)
- Agent supports push notifications for async updates
- Enable for long-running tasks with status updates

### Push Notifications

For long-running tasks, A2A supports asynchronous updates via push notifications.

**Use Cases:**
- Tasks taking minutes, hours, or days
- Mobile applications that can't maintain persistent connections
- Serverless functions with connection limits

**Configuration:**
- Set `pushNotifications: true` in `chat_params`
- External agent must implement push notification endpoint
- Include `corr_id` from initial request in notifications

**Notification Flow:**
1. watsonx Orchestrate sends initial request with callback URL
2. External agent starts long-running task
3. Agent returns acknowledgment immediately
4. Agent processes task asynchronously
5. Agent sends push notifications to callback URL with updates
6. watsonx Orchestrate receives and processes updates

**Authentication:**
- Bearer token authentication
- Generate from API keys using documented process
- Include complete task update in notification payload

**Notification Payload Requirements:**
- Include complete update (message, task, artifact details)
- Include `corr_id` from initial request metadata
- Follow A2A protocol's task object specification
- Partial status updates are not sufficient

## External Chat Protocol

Integrate agents using OpenAI-style Chat Completions API.

**Configuration:**
```yaml
spec_version: v1
kind: external
name: custom_agent
title: Custom Agent
provider: external_chat  # OpenAI-style API
description: |
  Custom agent built with any framework supporting Chat Completions API
api_url: "https://my-agent.example.com/v1/chat/completions"
auth_scheme: BEARER_TOKEN
auth_config:
  token: "${AGENT_TOKEN}"
chat_params:
  stream: true
config:
  hidden: false
  enable_cot: true
```

**API Specification:**
- Endpoint: `POST /v1/chat/completions`
- Request: `messages` array, `model` (optional), `stream` boolean
- Response: `choices` array with `message` and `content`

## LangGraph Agent Integration

LangGraph agents can be imported directly with automatic A2A protocol application.

**Supported Features:**
- Python implementations only
- Runs inside watsonx Orchestrate with isolation
- Supports messages in agent graph between turns
- Lifecycle tasks: update, delete, export

**Limitations:**
- Complex custom state objects lost between turns
- Must use messages for state persistence

**Example Agent:**
```python
from typing import Annotated, List, TypedDict
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    """Simple state with messages."""
    messages: Annotated[List[BaseMessage], "conversation history"]

def process_node(state: AgentState) -> AgentState:
    """Process user message and generate response."""
    user_message = state["messages"][-1].content if state["messages"] else ""
    
    response = AIMessage(
        content=f"Processed: {user_message}"
    )
    
    return {"messages": state["messages"] + [response]}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("process", process_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)

# Compile
app = graph.compile()
```

**Import Process:**
1. Create LangGraph agent following A2A patterns
2. Import using ADK CLI or UI
3. watsonx Orchestrate applies A2A protocol automatically
4. Agent available for use in workflows and collaborations

## Native Collaboration

Native watsonx Orchestrate agents can use other agents as collaborators without external protocols.

**Configuration:**
```python
from ibm_watsonx_orchestrate.agent_builder import Agent

# Create specialized agents
billing_agent = Agent(
    name="billing_specialist",
    description="Handles billing and payment inquiries",
    tools=["process_payment", "generate_invoice"]
)

technical_agent = Agent(
    name="technical_specialist",
    description="Handles technical support issues",
    tools=["diagnose_issue", "create_ticket"]
)

# Create supervisor with collaborators
supervisor = Agent(
    name="customer_service_supervisor",
    description="Routes customer inquiries to appropriate specialists",
    collaborators=[billing_agent, technical_agent]
)
```

**Routing Behavior:**
- Supervisor automatically routes requests to appropriate collaborators
- Based on collaborator descriptions and capabilities
- Write clear, distinct descriptions for accurate routing

## Communication Best Practices

### Clear Agent Descriptions

**Critical for proper routing and collaboration**

**Guidelines:**
- Be specific about capabilities and limitations
- Use action-oriented language
- Mention specific domains or data sources
- Differentiate from other agents

**Good Example:**
```yaml
description: |
  A customer billing specialist that handles invoice inquiries, payment processing,
  and billing disputes. Can access customer account data, generate invoices,
  process refunds, and update payment methods. Cannot handle technical support
  or product questions.
```

**Bad Example:**
```yaml
description: "Helps with billing stuff"
```

### Error Handling

**Ensure graceful degradation**

**Guidelines:**
- Implement timeouts for external agent calls
- Provide fallback behaviors
- Return clear error messages
- Log communication failures

### Context Management

**Maintain conversation coherence**

**Guidelines:**
- Use `sendHistory` for context-dependent agents
- Pass relevant context in each request
- Use `thread_id` for conversation tracking
- Clean up context after completion

### Performance Optimization

**Minimize latency and resource usage**

**Guidelines:**
- Use streaming for real-time responses
- Implement caching where appropriate
- Use async patterns for long operations
- Monitor and optimize response times

## Testing Agent Communication

### Unit Tests

Test individual agent responses:
- Agent handles various input types
- Agent returns expected format
- Agent handles errors gracefully

### Integration Tests

Test agent-to-agent communication:
- Supervisor routes to correct collaborator
- Context passes correctly between agents
- External agents respond properly
- A2A protocol works as expected

### End-to-End Tests

Test complete multi-agent workflows:
- Full conversation flows
- Complex routing scenarios
- Error recovery
- Performance under load

## Troubleshooting

### Agent Not Responding

**Symptoms:** External agent doesn't respond or times out

**Solutions:**
- Verify agent URL is correct and accessible
- Check authentication credentials
- Verify agent is running and healthy
- Check network connectivity
- Review agent logs for errors

### Incorrect Routing

**Symptoms:** Supervisor routes to wrong collaborator

**Solutions:**
- Review and improve agent descriptions
- Make descriptions more distinct
- Add specific keywords to descriptions
- Test with various input types

### Context Loss

**Symptoms:** Agent doesn't remember previous conversation

**Solutions:**
- Enable `sendHistory` in `chat_params`
- Verify `thread_id` is passed correctly
- Check agent state management
- Review conversation history handling

### A2A Protocol Errors

**Symptoms:** A2A communication fails

**Solutions:**
- Verify using correct A2A version (0.3.0)
- Check JSON-RPC 2.0 format
- Verify agent implements A2A spec correctly
- Review A2A protocol documentation

## Collaboration Patterns

### Supervisor-Worker Pattern

One supervisor coordinates multiple worker agents:

```python
# Create workers
worker1 = Agent(name="worker1", description="Handles task type A")
worker2 = Agent(name="worker2", description="Handles task type B")

# Create supervisor
supervisor = Agent(
    name="supervisor",
    description="Routes tasks to appropriate workers",
    collaborators=[worker1, worker2]
)
```

**When to Use:**
- Complex tasks requiring multiple specialties
- Need for intelligent task routing
- Dynamic agent selection based on context

### Peer-to-Peer Pattern

Agents communicate directly without central coordinator:

```python
# Each agent can call others as needed
agent1 = Agent(
    name="agent1",
    collaborators=[agent2, agent3]
)

agent2 = Agent(
    name="agent2",
    collaborators=[agent1, agent3]
)
```

**When to Use:**
- Highly collaborative tasks
- No clear hierarchy
- Emergent behavior desired

### Sequential Pipeline

Agents process tasks in defined sequence:

```python
# Use agentic workflow to chain agents
@flow(name="pipeline")
def build_pipeline(aflow: Flow) -> Flow:
    agent1 = aflow.agent(name="step1", agent="agent1")
    agent2 = aflow.agent(name="step2", agent="agent2")
    agent3 = aflow.agent(name="step3", agent="agent3")
    
    aflow.sequence(START, agent1, agent2, agent3, END)
    return aflow
```

**When to Use:**
- Clear, linear workflow
- Each step depends on previous output
- Predictable processing pipeline

## Reference Implementations

**LangGraph A2A Sample:**
https://github.com/ibm/a2a-samples

**External Chat Reference:**
watsonx-orchestrate-developer-toolkit

**Agent Swarm Pattern:**
https://achan2013.medium.com/building-agent-swarm-c412b0668f7b