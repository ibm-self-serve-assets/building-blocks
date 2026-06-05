# Complete Orchestration Examples

## Customer Support System

Multi-agent customer support with supervisor-worker pattern.

### Architecture
- Supervisor Agent: Routes inquiries to specialists
- Billing Agent: Handles billing and payments
- Technical Agent: Handles technical issues
- General Agent: Handles general questions

### Implementation

```python
from ibm_watsonx_orchestrate.agent_builder import Agent

# Create specialist agents
billing_agent = Agent(
    name="billing_specialist",
    description="""
    Specialist in billing, payments, invoices, and account charges.
    Can process payments, generate invoices, handle refunds, and
    explain billing statements. Cannot help with technical issues
    or general product questions.
    """,
    tools=["process_payment", "generate_invoice", "issue_refund"],
    instructions="""
    Be professional and empathetic when discussing billing issues.
    Always verify customer identity before processing payments.
    Explain charges clearly and provide itemized breakdowns.
    """
)

technical_agent = Agent(
    name="technical_specialist",
    description="""
    Technical support specialist for product issues, bugs, and
    troubleshooting. Can diagnose problems, create support tickets,
    and provide technical solutions. Cannot handle billing or
    general inquiries.
    """,
    tools=["diagnose_issue", "create_ticket", "check_system_status"],
    instructions="""
    Gather detailed information about technical issues.
    Provide step-by-step troubleshooting guidance.
    Create tickets for issues requiring engineering team.
    """
)

general_agent = Agent(
    name="general_specialist",
    description="""
    Handles general product questions, account information,
    and basic inquiries. Can provide product information,
    explain features, and guide users. Cannot handle billing
    or technical issues.
    """,
    tools=["get_product_info", "get_account_info"],
    instructions="""
    Be friendly and helpful.
    Provide clear, concise answers.
    Direct complex issues to appropriate specialists.
    """
)

# Create supervisor agent
supervisor = Agent(
    name="customer_service_supervisor",
    description="""
    Customer service supervisor that routes inquiries to
    appropriate specialists based on the nature of the request.
    """,
    collaborators=[billing_agent, technical_agent, general_agent],
    instructions="""
    Analyze the customer's inquiry to determine the appropriate specialist.
    Route billing questions to billing_specialist.
    Route technical issues to technical_specialist.
    Route general questions to general_specialist.
    If unsure, ask clarifying questions before routing.
    """
)

# Import agents
from ibm_watsonx_orchestrate import orchestrate
orchestrate.agents.import_agent(supervisor)
```

### Usage Example
```
User: "I was charged twice for my subscription"
→ Supervisor routes to billing_specialist
→ Billing agent processes refund
→ Returns confirmation to user
```

## Data Processing Pipeline

Sequential workflow with validation and transformation.

### Workflow Structure
```
Start → Data Fetcher → Data Validator → Branch →
[Valid: Transform → Analyze → Report, Invalid: End] → End
```

### Implementation

```python
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END

class DataInput(BaseModel):
    source: str = Field(description="Data source identifier")

class DataOutput(BaseModel):
    report: str = Field(description="Generated analysis report")

@flow(
    name="data_processing_pipeline",
    display_name="Data Processing Pipeline",
    description="Fetch, validate, transform, analyze, and report on data",
    input_schema=DataInput,
    output_schema=DataOutput
)
def build_data_pipeline(aflow: Flow) -> Flow:
    """Complete data processing pipeline with validation"""
    
    # Define nodes
    fetch_data = aflow.tool("fetch_data_source")
    validate = aflow.agent(
        name="validate",
        agent="data_validator",
        message="Validate the fetched data for quality and completeness"
    )
    
    # Add validation branch
    validation_branch = aflow.branch(
        evaluator="flow.state.validation_passed == true"
    )
    
    transform = aflow.tool("transform_data")
    analyze = aflow.agent(
        name="analyze",
        agent="data_analyzer",
        message="Perform statistical analysis on the transformed data"
    )
    generate_report = aflow.tool("generate_report")
    
    # Connect nodes
    aflow.edge(START, fetch_data)
    aflow.edge(fetch_data, validate)
    aflow.edge(validate, validation_branch)
    
    # Validation branch paths
    validation_branch.case(True, transform)   # Validation passed
    validation_branch.case(False, END)        # Validation failed
    
    aflow.edge(transform, analyze)
    aflow.edge(analyze, generate_report)
    aflow.edge(generate_report, END)
    
    return aflow

# Import workflow
# orchestrate tools import -k flow -f data_processing_pipeline.py
```

## Approval Workflow

Human-in-the-loop with conditional branching.

### Workflow Structure
```
Start → Prepare Request → User Approval Form → Branch →
[Approved: Process, Rejected: Notify] → End
```

### Implementation

```python
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END, UserFieldKind

class PurchaseRequest(BaseModel):
    item: str = Field(description="Item to purchase")
    amount: float = Field(description="Purchase amount")

class PurchaseResult(BaseModel):
    status: str = Field(description="Purchase status")
    message: str = Field(description="Result message")

@flow(
    name="purchase_approval_workflow",
    display_name="Purchase Approval Workflow",
    description="Human-in-the-loop approval with conditional branching",
    input_schema=PurchaseRequest,
    output_schema=PurchaseResult
)
def build_approval_workflow(aflow: Flow) -> Flow:
    """Purchase approval workflow with user form"""
    
    # Prepare request
    prepare_request = aflow.agent(
        name="prepare",
        agent="request_preparer",
        message="Prepare purchase request for: {flow.input.item}"
    )
    
    # Create user flow
    user_flow = aflow.userflow()
    user_flow.spec.display_name = "Purchase Approval Required"
    
    # Create form
    approval_form = user_flow.form(
        name="approval",
        display_name="Purchase Approval"
    )
    
    # Add fields
    approval_form.checkbox_field(
        name="approved",
        display_name="Approve this purchase?",
        kind=UserFieldKind.Checkbox
    )
    approval_form.text_input_field(
        name="comments",
        display_name="Comments",
        kind=UserFieldKind.TextInput
    )
    approval_form.number_field(
        name="amount_approved",
        display_name="Approved Amount (if different)",
        kind=UserFieldKind.Number
    )
    
    # Add button
    approval_form.button(name="submit", display_name="Submit Decision")
    
    # Connect form
    user_flow.sequence(START, approval_form, END)
    
    # Create decision branch
    decision_branch = aflow.branch(
        evaluator="flow.state.approved == true"
    )
    
    # Processing nodes
    process_purchase = aflow.agent(
        name="process",
        agent="purchase_processor",
        message="Process approved purchase"
    )
    
    send_rejection = aflow.agent(
        name="reject",
        agent="notification_agent",
        message="Send rejection notification"
    )
    
    # Connect workflow
    aflow.edge(START, prepare_request)
    aflow.edge(prepare_request, user_flow)
    aflow.edge(user_flow, decision_branch, button_label="submit")
    
    decision_branch.case(True, process_purchase)
    decision_branch.case(False, send_rejection)
    
    aflow.edge(process_purchase, END)
    aflow.edge(send_rejection, END)
    
    return aflow
```

## Parallel Data Gathering

Execute multiple agents concurrently.

### Workflow Structure
```
Start → [Weather Agent, News Agent, Stock Agent] → Aggregator → End
```

### Implementation

```python
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END

class DataRequest(BaseModel):
    location: str = Field(description="Location for data gathering")

class AggregatedData(BaseModel):
    summary: str = Field(description="Combined data summary")

@flow(
    name="parallel_data_gathering",
    display_name="Parallel Data Gathering",
    description="Parallel execution of multiple data sources",
    input_schema=DataRequest,
    output_schema=AggregatedData
)
def build_parallel_workflow(aflow: Flow) -> Flow:
    """Gather data from multiple sources in parallel"""
    
    # Create parallel agents
    weather_agent = aflow.agent(
        name="weather",
        agent="weather_specialist",
        message="Get weather for {flow.input.location}"
    )
    
    news_agent = aflow.agent(
        name="news",
        agent="news_specialist",
        message="Get news for {flow.input.location}"
    )
    
    stock_agent = aflow.agent(
        name="stocks",
        agent="stock_specialist",
        message="Get stock market data"
    )
    
    # Aggregator
    aggregator = aflow.agent(
        name="aggregate",
        agent="data_aggregator",
        message="Combine and summarize all data"
    )
    
    # Parallel branches - all start from START
    aflow.edge(START, weather_agent)
    aflow.edge(START, news_agent)
    aflow.edge(START, stock_agent)
    
    # All converge at aggregator
    aflow.edge(weather_agent, aggregator)
    aflow.edge(news_agent, aggregator)
    aflow.edge(stock_agent, aggregator)
    
    aflow.edge(aggregator, END)
    
    return aflow
```

## Batch Processing with Foreach

Iterate over multiple items.

### Workflow Structure
```
Start → Fetch Items → Foreach Item → [Process] → Summary → End
```

### Implementation

```python
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END

class ItemList(BaseModel):
    items: list[str] = Field(description="Items to process")

class ProcessingSummary(BaseModel):
    summary: str = Field(description="Summary of processed items")
    count: int = Field(description="Number processed")

class ItemSchema(BaseModel):
    item: str = Field(description="Single item")

@flow(
    name="batch_processing",
    display_name="Batch Processing Workflow",
    description="Process multiple items iteratively",
    input_schema=ItemList,
    output_schema=ProcessingSummary
)
def build_batch_workflow(aflow: Flow) -> Flow:
    """Process multiple items iteratively"""
    
    # Fetch items
    fetch_items = aflow.tool("fetch_items_list")
    
    # Create foreach sub-workflow
    foreach_flow = aflow.foreach(item_schema=ItemSchema)
    
    # Add processing to sub-workflow
    process_agent = foreach_flow.agent(
        name="processor",
        agent="item_processor",
        message="Process: {flow.input.item}"
    )
    
    foreach_flow.sequence(START, process_agent, END)
    
    # Generate summary
    generate_summary = aflow.agent(
        name="summary",
        agent="summary_generator",
        message="Generate summary of all processed items"
    )
    
    # Connect main workflow
    aflow.edge(START, fetch_items)
    aflow.edge(fetch_items, foreach_flow)
    aflow.edge(foreach_flow, generate_summary)
    aflow.edge(generate_summary, END)
    
    return aflow
```

## External Agent Integration

Integrate LangGraph agent via A2A protocol.

### External Agent (LangGraph)

```python
from typing import Annotated, List, TypedDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "conversation history"]

def research_node(state: AgentState) -> AgentState:
    """Research agent that searches and analyzes."""
    llm = ChatOpenAI(model="gpt-4")
    
    user_query = state["messages"][-1].content
    research_prompt = f"Research: {user_query}"
    response = llm.invoke([HumanMessage(content=research_prompt)])
    
    return {"messages": state["messages"] + [response]}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("research", research_node)
graph.add_edge(START, "research")
graph.add_edge("research", END)

# Compile and serve with A2A
app = graph.compile()
```

### watsonx Orchestrate Integration

```python
from ibm_watsonx_orchestrate.agent_builder import (
    Agent, ExternalAgent, AgentKind, ExternalAgentAuthScheme
)

# Register external agent
research_agent = ExternalAgent(
    kind=AgentKind.EXTERNAL,
    name="research_agent",
    title="Research Specialist",
    provider="external_chat/A2A/0.3.0",
    description="External research agent for information gathering",
    api_url="https://my-langgraph-agent.example.com/a2a",
    auth_scheme=ExternalAgentAuthScheme.BEARER_TOKEN,
    auth_config={"token": "${RESEARCH_AGENT_TOKEN}"},
    chat_params={
        "sendHistory": True,
        "stream": False
    }
)

# Use as collaborator
supervisor = Agent(
    name="information_supervisor",
    description="Coordinates information gathering",
    collaborators=[research_agent]
)
```

## AI Gateway Model Integration

Complete setup for OpenAI GPT-4.

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

# 5. Create agent using model
cat > agent.yaml <<EOF
spec_version: v1
kind: agent
name: gpt4_agent
model: gpt-4-turbo
description: Agent powered by GPT-4 Turbo
instructions: You are a helpful assistant.
EOF

# 6. Import agent
orchestrate agents import -f agent.yaml
```

## MCP Server Integration

Database operations via MCP.

### MCP Server Code

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import sqlite3

server = Server("database-tools")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_database",
            description="Execute SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "params": {"type": "array"}
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_database":
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(arguments["query"], arguments.get("params", []))
        results = cursor.fetchall()
        conn.close()
        return [TextContent(type="text", text=str(results))]

if __name__ == "__main__":
    server.run()
```

### Configuration and Usage

```bash
# Import toolkit
orchestrate tools import --mcp database-tools

# Use in agent
cat > db-agent.yaml <<EOF
spec_version: v1
kind: agent
name: database_agent
description: Agent that can query database
tools:
  - database-tools:query_database
EOF

orchestrate agents import -f db-agent.yaml
```

## Testing Examples

### Unit Test

```python
import pytest
from ibm_watsonx_orchestrate.agent_builder import Agent

def test_billing_agent_description():
    agent = Agent(
        name="billing_specialist",
        description="Handles billing inquiries"
    )
    assert "billing" in agent.description.lower()

def test_agent_tool_configuration():
    agent = Agent(
        name="test_agent",
        tools=["tool1", "tool2"]
    )
    assert len(agent.tools) == 2
```

### Integration Test

```python
import pytest
from ibm_watsonx_orchestrate import orchestrate

def test_workflow_execution():
    # Import workflow
    result = orchestrate.tools.import_tool(
        "workflows/test_flow.py",
        kind="flow"
    )
    assert result.success
    
    # Execute workflow
    instance = orchestrate.flows.run(
        "test_flow",
        inputs={"test_data": "value"}
    )
    
    # Verify results
    assert instance.status == "completed"
    assert instance.output is not None