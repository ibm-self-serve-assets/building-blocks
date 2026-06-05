# Agentic Workflow Patterns

## Critical API Update

⚠️ **IMPORTANT**: The FlowBuilder class-based API is DEPRECATED.

**Current API uses the @flow decorator pattern.**

BEFORE generating ANY workflow code:
1. Search ADK documentation for current @flow decorator examples
2. Use the @flow decorator pattern, NOT FlowBuilder
3. Verify syntax against latest documentation

### API Comparison

**OLD (DEPRECATED) - Do NOT use:**
```python
from ibm_watsonx_orchestrate.flow_builder import FlowBuilder
flow = FlowBuilder(name="my_workflow")
```

**CURRENT - Use this pattern:**
```python
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END

@flow(
    name="my_workflow",
    display_name="My Workflow",
    description="Workflow description",
    input_schema=InputSchema,
    output_schema=OutputSchema
)
def build_my_workflow(aflow: Flow) -> Flow:
    """Workflow docstring"""
    # Add nodes and connect them
    return aflow
```

## Documentation-First Principle

**MANDATORY**: Search ADK documentation before implementing any workflow:

```
Use: search_ibm_watsonx_orchestrate_adk
Queries: "agentic workflow @flow decorator", "flow nodes", etc.
```

This ensures you have:
- Latest syntax and working examples
- Current API references
- Correct field names and parameters

## Workflow Fundamentals

### Core Concepts

**Nodes**: Individual units of work
- `start` - Entry point (exactly one per workflow)
- `end` - Exit point (at least one per workflow)
- `agent` - Calls an imported agent
- `tool` - Calls an imported tool
- `flow` - Nested workflow
- `branch` - Conditional branching (if-then-else)
- `foreach` - Iterate over a list
- `loop` - Repeat until condition met
- `decisions` - Decision table with conditions
- `prompt` - LLM call for extraction/classification
- `doc_processing` - Extract text from documents

**Edges**: Connections between nodes
- Single exit point → Sequential execution
- Multiple exit points → Parallel execution
- Branch nodes → Only first matching path followed

**Execution Modes**:
- **Synchronous**: Wait for completion or interruption
- **Asynchronous**: Return instance_id immediately

## Node Implementation Patterns

### Agent Node

Call an agent to perform a task:

```python
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END

class CustomerInput(BaseModel):
    inquiry: str = Field(description="Customer inquiry text")

class CustomerOutput(BaseModel):
    response: str = Field(description="Agent response")

@flow(
    name="customer_service_workflow",
    display_name="Customer Service Workflow",
    description="Handle customer service inquiries",
    input_schema=CustomerInput,
    output_schema=CustomerOutput
)
def build_workflow(aflow: Flow) -> Flow:
    """Process customer service requests"""
    
    agent_node = aflow.agent(
        name="customer_service_agent",
        agent="customer_service",  # Name of imported agent
        display_name="Customer Service Agent",
        message="Handle inquiry: {flow.input.inquiry}",
        description="Process customer requests",
        guidelines="Be polite and helpful",
        input_schema=CustomerInput,
        output_schema=CustomerOutput
    )
    
    aflow.sequence(START, agent_node, END)
    return aflow
```

**Best Practices:**
- Provide clear, specific messages
- Use guidelines to constrain behavior
- Define input/output schemas for type safety

### Tool Node

Call an imported tool:

```python
def build_workflow(aflow: Flow) -> Flow:
    # Call tool by name
    tool_node = aflow.tool(
        name="send_email",
        display_name="Send Email"
    )
    
    # Or by reference
    from .my_tools import send_email_tool
    tool_node = aflow.tool(send_email_tool)
    
    return aflow
```

### Branch Node

Conditional branching:

```python
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, Branch

def build_workflow(aflow: Flow) -> Flow:
    # Create branch with evaluator
    branch_node = aflow.branch(
        name="approval_decision",
        display_name="Check Approval Status",
        evaluator="flow.input.approval_status == 'approved'"
    )
    
    # Define nodes for each path
    approval_node = aflow.tool("send_approval_email")
    rejection_node = aflow.tool("send_rejection_email")
    
    # Connect branch cases
    branch_node.case(True, approval_node)   # When true
    branch_node.case(False, rejection_node)  # When false
    
    aflow.edge(START, branch_node)
    aflow.edge(approval_node, END)
    aflow.edge(rejection_node, END)
    
    return aflow
```

**Expression Syntax:**
- Use JSONPath-like expressions: `$.field_name`
- Operators: `==`, `!=`, `>`, `<`, `&&`, `||`

### Foreach Node

Iterate over a list:

```python
from pydantic import BaseModel

class EmailRecord(BaseModel):
    email: str
    name: str

def build_workflow(aflow: Flow) -> Flow:
    # Create sub-flow for each item
    foreach_flow = aflow.foreach(item_schema=EmailRecord)
    
    # Add nodes to sub-flow
    process_node = foreach_flow.tool("process_single_email")
    foreach_flow.sequence(START, process_node, END)
    
    # Connect to main flow
    get_emails = aflow.tool("get_email_list")
    aflow.edge(START, get_emails)
    aflow.edge(get_emails, foreach_flow)
    aflow.edge(foreach_flow, END)
    
    return aflow
```

**Use Cases:**
- Process multiple customer requests
- Send notifications to multiple recipients
- Validate multiple data records

### Loop Node

Repeat until condition met:

```python
def build_workflow(aflow: Flow) -> Flow:
    # Create loop with evaluator
    loop_node = aflow.loop(
        evaluator="flow.state.retry_count < 3 and not flow.state.success"
    )
    
    # Add nodes inside loop
    api_call = loop_node.tool("call_external_api")
    check_result = loop_node.tool("check_api_result")
    loop_node.sequence(START, api_call, check_result, END)
    
    # Connect to main flow
    aflow.sequence(START, loop_node, END)
    
    return aflow
```

**Best Practices:**
- Always include maximum iteration limit
- Ensure condition will eventually become false
- Track iteration count in workflow data

### Human-in-the-Loop

Include human approval or input:

```python
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, UserFieldKind

def build_workflow(aflow: Flow) -> Flow:
    # Prepare request
    prepare = aflow.tool("prepare_request")
    
    # Create user flow
    user_flow = aflow.userflow()
    user_flow.spec.display_name = "Approval Required"
    
    # Create form
    approval_form = user_flow.form(
        name="approval_form",
        display_name="Request Approval"
    )
    
    # Add fields
    approval_form.checkbox_field(
        name="approved",
        display_name="Approve this request?",
        kind=UserFieldKind.Checkbox
    )
    approval_form.text_input_field(
        name="comments",
        display_name="Comments",
        kind=UserFieldKind.TextInput
    )
    
    # Add button
    approval_form.button(name="submit", display_name="Submit")
    
    # Connect in user flow
    user_flow.sequence(START, approval_form, END)
    
    # Process decision
    process = aflow.tool("process_decision")
    
    # Connect to main flow
    aflow.edge(START, prepare)
    aflow.edge(prepare, user_flow)
    aflow.edge(user_flow, process, button_label="submit")
    aflow.edge(process, END)
    
    return aflow
```

## Workflow Composition Patterns

### Sequential Workflow

Simple linear execution:

```python
@flow(name="sequential_workflow")
def build_sequential_workflow(aflow: Flow) -> Flow:
    """Simple linear execution"""
    
    agent1 = aflow.agent(name="analyzer", agent="data_analyzer")
    tool1 = aflow.tool("data_processor")
    agent2 = aflow.agent(name="reporter", agent="report_generator")
    
    # Connect sequentially
    aflow.sequence(START, agent1, tool1, agent2, END)
    
    return aflow
```

### Parallel Workflow

Execute multiple branches concurrently:

```python
@flow(name="parallel_workflow")
def build_parallel_workflow(aflow: Flow) -> Flow:
    """Execute branches concurrently"""
    
    # Create parallel agents
    agent1 = aflow.agent(name="analyzer1", agent="data_analyzer")
    agent2 = aflow.agent(name="analyzer2", agent="sentiment_analyzer")
    agent3 = aflow.agent(name="analyzer3", agent="trend_analyzer")
    
    # Merge results
    merge = aflow.tool("merge_results")
    
    # Connect all to start (parallel execution)
    aflow.edge(START, agent1)
    aflow.edge(START, agent2)
    aflow.edge(START, agent3)
    
    # All converge at merge
    aflow.edge(agent1, merge)
    aflow.edge(agent2, merge)
    aflow.edge(agent3, merge)
    aflow.edge(merge, END)
    
    return aflow
```

**Use Cases:**
- Gather data from multiple sources
- Run multiple analyses in parallel
- Send notifications to multiple channels

### Conditional Workflow

Branch based on conditions:

```python
@flow(name="conditional_workflow")
def build_conditional_workflow(aflow: Flow) -> Flow:
    """Branch based on conditions"""
    
    # Classify request
    classifier = aflow.agent(name="classifier", agent="priority_classifier")
    
    # Create branch
    priority_branch = aflow.branch(
        evaluator="flow.state.priority == 'high'"
    )
    
    # Create handlers
    urgent = aflow.agent(name="urgent", agent="urgent_handler")
    normal = aflow.agent(name="normal", agent="normal_handler")
    
    # Connect
    aflow.edge(START, classifier)
    aflow.edge(classifier, priority_branch)
    priority_branch.case(True, urgent)
    priority_branch.case(False, normal)
    aflow.edge(urgent, END)
    aflow.edge(normal, END)
    
    return aflow
```

## Data Mapping

Data flows automatically between nodes in current API:

```python
from pydantic import BaseModel, Field

class NodeInput(BaseModel):
    customer_id: str = Field(description="Customer ID")
    email: str = Field(description="Customer email")

def build_workflow(aflow: Flow) -> Flow:
    node = aflow.tool(
        "process_customer",
        input_schema=NodeInput
    )
    # Data from previous node's output automatically maps
    return aflow
```

**Transformation:**
Use tools or agents to transform data:

```python
def build_workflow(aflow: Flow) -> Flow:
    # Transform data
    transform = aflow.tool("transform_customer_data")
    
    # Or use expressions in agent messages
    agent = aflow.agent(
        name="process",
        agent="processor",
        message="Process: {flow.input.first_name} {flow.input.last_name}"
    )
    
    return aflow
```

**Context Window Management:**

```python
@flow(
    name="my_workflow",
    agent_conversation_memory_turns_limit=10  # Limit history
)
def build_workflow(aflow: Flow) -> Flow:
    """Workflow with managed context"""
    # Context automatically managed
    return aflow
```

## Workflow Lifecycle

### Creation
1. Define workflow using Python and ADK
2. Configure nodes with types and parameters
3. Connect nodes with edges
4. Set up data mappings
5. Configure context window if needed

### Import
```bash
orchestrate tools import -k flow -f path/to/workflow.py
```

### Testing
- Test in draft environment
- Validate data flow between nodes
- Check error handling
- Verify output schemas

### Deployment
- Deploy to target environment
- Configure environment-specific settings
- Set up monitoring and logging

### Management
```bash
# List workflows
orchestrate tools list -k flow

# Export workflow
orchestrate tools export -k flow workflow_name

# Update workflow
orchestrate tools update -k flow -f path/to/workflow.py

# Remove workflow
orchestrate tools remove -k flow workflow_name
```

## Best Practices

### Design
- Start simple, add complexity incrementally
- Use descriptive names for nodes and workflows
- Document complex logic with comments
- Keep workflows focused on single responsibilities

### Data Management
- Define clear input/output schemas
- Use data mapping to transform data
- Enable compression for large data workflows
- Validate data at workflow boundaries

### Error Handling
- Include error handling branches
- Set appropriate timeouts
- Implement retry logic for transient failures
- Log errors for debugging

### Performance
- Use parallel execution where possible
- Choose async execution for long-running workflows
- Optimize data passed between nodes
- Monitor workflow execution times

### Testing
- Test with realistic data
- Validate all conditional branches
- Test error scenarios
- Verify data transformations

## Common Use Case Patterns

### Customer Support
```
Start → Classify Request → Branch by Priority →
[High: Urgent Agent, Medium: Standard Agent, Low: Automated] →
Send Notification → End
```

### Data Processing
```
Start → Fetch Data → Foreach Item →
[Validate → Transform → Store] →
Generate Report → End
```

### Approval Workflow
```
Start → Prepare Request → User Approval Form →
Branch on Decision →
[Approved: Process, Rejected: Notify] → End
```

### Multi-Agent Collaboration
```
Start → Coordinator Agent →
[Specialist 1, Specialist 2, Specialist 3] →
Aggregator Agent → End
```

## Troubleshooting

### Workflow Not Completing
**Symptoms:** Hangs or times out

**Solutions:**
- Check for infinite loops
- Verify all branches have paths to end
- Increase timeout settings
- Check for blocking operations

### Data Mapping Errors
**Symptoms:** Incorrect or missing data

**Solutions:**
- Verify JSONPath expressions
- Check output schemas
- Use explicit mapping
- Validate data types

### Parallel Execution Issues
**Symptoms:** Not executing in parallel

**Solutions:**
- Ensure multiple outgoing edges
- Verify edges not accidentally sequential
- Check for resource contention