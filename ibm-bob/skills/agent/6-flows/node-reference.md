# Agentic Workflow Node Reference

Complete reference for all 14 node types in the ADK `@flow` API.

---

## Agent Node — `aflow.agent()`

Call an imported agent to perform a task.

```python
agent_node = aflow.agent(
    name="ask_ibm_agent",           # required — internal node name
    agent="ibm_agent",              # required — imported agent name
    display_name="Ask IBM Agent",
    message="Answer this question about IBM: {flow.input.question}",
    description="Gets a fact about IBM",
    guidelines="Be concise. If you don't know, say so.",
    input_schema=IBMAgentInput,
    output_schema=IBMAgentOutput,
    input_map=data_map              # optional explicit DataMap
)
```

| Parameter | Required | Description |
|---|---|---|
| `name` | ✅ | Internal node identifier |
| `agent` | ✅ | Name of the imported agent |
| `display_name` | | Human-readable name |
| `message` | | Instruction to agent. Default: "Follow the agent instructions" |
| `description` | | What this node does |
| `guidelines` | | Behavior constraints for the agent |
| `input_schema` | | Pydantic model for inputs |
| `output_schema` | | Pydantic model for outputs |
| `input_map` | | `DataMap` for explicit input mapping |

See [`assets/approval_flow.py`](./assets/approval_flow.py) for a complete agent node example.

---

## Tool Node — `aflow.tool()`

Call an imported tool (Python `@tool`, OpenAPI, MCP, or Flow).

```python
# By Python function reference
from .send_emails import send_emails
tool_node = aflow.tool(send_emails)

# By name string
tool_node = aflow.tool("getDogFact")

# With explicit schemas and error handling
from ibm_watsonx_orchestrate.flow_builder.types import NodeErrorHandlerConfig
tool_node = aflow.tool(
    "fetchExternalData",
    name="fetch_data",
    input_schema=FetchInput,
    output_schema=FetchOutput,
    error_handler_config=NodeErrorHandlerConfig(
        max_retries=3,
        retry_interval=2000,
        on_error="branch",
        error_edge_id="fetch_error_path"
    )
)
```

| Parameter | Required | Description |
|---|---|---|
| `tool` | ✅ | Python function or tool name string |
| `name` | | Internal node name |
| `display_name` | | Human-readable name |
| `input_schema` / `output_schema` | | Pydantic models |
| `input_map` | | `DataMap` for explicit input mapping |
| `error_handler_config` | | `NodeErrorHandlerConfig` for retry/branch on error |

See [`assets/hello_flow.py`](./assets/hello_flow.py) and [`assets/approval_flow.py`](./assets/approval_flow.py).

---

## Script Node — `aflow.script()`

Execute inline Python to transform data, initialize state, or perform custom logic. Equivalent to a Logic Block in the Flow Builder UI.

```python
process_node = aflow.script(
    name="prepare_data",
    display_name="Prepare Data",
    output_schema=PreparedData,
    script="""
# Read from flow input
user_id = f"USR-{hash(flow.input.username) % 10000}"
flow.private.user_id = user_id

# Read another node's output
name = flow.nodes['fetch_profile'].output.full_name

# Write to this node's output
self.output.display_name = name.upper()
self.output.user_id = user_id
"""
)
```

### Script Variable Reference

| Variable | Reads | Writes |
|---|---|---|
| `flow.input.<field>` | ✅ | ❌ |
| `flow.output.<field>` | ✅ | ✅ |
| `flow.private.<field>` | ✅ | ✅ |
| `flow.nodes['<name>'].output.<field>` | ✅ | ❌ |
| `self.output.<field>` | ✅ | ✅ |

See [`assets/masking_flow.py`](./assets/masking_flow.py) for comprehensive script node usage.

---

## Branch Node — `aflow.conditions()`

Conditional branching — evaluates conditions top-to-bottom and follows the **first matching path only**.

```python
branch = aflow.conditions()
branch.condition(
    expression="flow.input.kind.strip().lower() == 'dog'",
    to_node=dog_node
).condition(
    expression="flow.input.kind.strip().lower() == 'cat'",
    to_node=cat_node
).condition(
    to_node=default_node,
    default=True          # fallback if no condition matches
)
aflow.edge(START, branch)
```

> ⚠️ Use `aflow.conditions()` — NOT `aflow.branch()`. The `.case()` method is deprecated.

See [`assets/approval_flow.py`](./assets/approval_flow.py).

---

## Parallel Node — `aflow.parallel()` / `aflow.parallel_conditions()`

Run multiple branches concurrently. The flow waits for **all** branches to complete before continuing.

```python
# Unconditional parallel — all branches always run
parallel = aflow.parallel(name="parallel_analysis")
branch1 = parallel.script(name="analyze_sentiment", script="...")
branch2 = parallel.script(name="analyze_keywords", script="...")
parallel.sequence(START, branch1, END)
parallel.sequence(START, branch2, END)

# Conditional parallel — only matching branches run
cond_parallel = aflow.parallel_conditions(name="optional_phases")
design = cond_parallel.script(name="design_work", script="...")
arch   = cond_parallel.script(name="arch_work", script="...")
skip   = cond_parallel.script(name="skip", script="print('skipping')")
cond_parallel.condition(expression="flow.private.design_needed is True", to_node=design)
cond_parallel.condition(expression="flow.private.arch_needed is True",   to_node=arch)
cond_parallel.condition(default=True, to_node=skip)
cond_parallel.sequence(design, END)
cond_parallel.sequence(arch,   END)
cond_parallel.sequence(skip,   END)
```

See [`assets/parallel_flow.py`](./assets/parallel_flow.py) for a complete multi-phase delivery example.

---

## Foreach Node — `aflow.foreach()`

Iterate over a list, running sub-flow nodes for each item.

```python
from ibm_watsonx_orchestrate.flow_builder.types import ForeachPolicy

foreach = aflow.foreach(item_schema=CustomerRecord) \
    .policy(kind=ForeachPolicy.SEQUENTIAL)  # or ForeachPolicy.PARALLEL

process_node = foreach.tool(send_invitation_email)
foreach.sequence(START, process_node, END)

aflow.edge(START, get_list_node)
aflow.edge(get_list_node, foreach)
aflow.edge(foreach, END)
```

| Policy | Behavior |
|---|---|
| `ForeachPolicy.SEQUENTIAL` | Items processed one at a time in order |
| `ForeachPolicy.PARALLEL` | Items processed concurrently |

See [`assets/foreach_flow.py`](./assets/foreach_flow.py).

---

## Loop Node — `aflow.loop()`

Repeat a sub-flow while a condition is true.

```python
loop = aflow.loop(
    evaluator="not flow.nodes['check_status'].output.done and flow.private.attempts < 5",
    input_schema=AttemptSchema,
    output_schema=ResultSchema
)
check_node = loop.tool(check_request_status)
loop.sequence(START, check_node, END)

aflow.sequence(START, start_job_node, loop, END)
```

See [`assets/timer_loop_flow.py`](./assets/timer_loop_flow.py) for a polling loop with timer.

---

## Timer Node — `aflow.timer()`

Add a delay between actions (useful in polling loops).

```python
timer_node = loop.timer(
    name="wait_2_sec",
    delay=2000,           # milliseconds
    display_name="Wait 2 seconds"
)
loop.sequence(START, check_node, timer_node, END)
```

| Parameter | Required | Description |
|---|---|---|
| `name` | ✅ | Internal node identifier |
| `delay` | ✅ | Delay in milliseconds |
| `display_name` | | Human-readable name |

See [`assets/timer_loop_flow.py`](./assets/timer_loop_flow.py).

---

## Generative Prompt Node — `aflow.prompt()`

Make an LLM call to extract, classify, or generate structured content.

```python
from ibm_watsonx_orchestrate.flow_builder.flows import PromptNode

prompt_node = aflow.prompt(
    name="extract_support_info",
    display_name="Extract Support Info",
    system_prompt=["You are a support processing assistant. Extract structured information."],
    user_prompt=["Here is the support request: {message}"],
    llm="meta-llama/llama-3-3-70b-instruct",
    llm_parameters={
        "temperature": 0,
        "max_new_tokens": 400,
        "top_k": 1,
        "stop_sequences": ["Human:", "AI:"]
    },
    input_schema=SupportMessage,
    output_schema=SupportInfo,
    error_handler_config=NodeErrorHandlerConfig(
        error_message="LLM call failed",
        max_retries=1,
        retry_interval=1000
    )
)
```

| Parameter | Description |
|---|---|
| `name` | Unique node identifier |
| `system_prompt` | String or list of strings — LLM behavior instructions |
| `user_prompt` | String or list of strings — the request. Supports `{variable}` expressions |
| `llm` | LLM model identifier |
| `llm_parameters` | `temperature`, `min_new_tokens`, `max_new_tokens`, `top_k`, `top_p`, `stop_sequences` |
| `prompt_examples` | List of `PromptExample(input, expected_output, enabled)` |
| `input_schema` / `output_schema` | Pydantic models |
| `input_map` | `DataMap` for explicit input mapping |
| `error_handler_config` | Retry/branch on error |

---

## Decisions Node — `aflow.decisions()`

Evaluate a decision table — rules are checked top-to-bottom, first match wins.

```python
from ibm_watsonx_orchestrate.flow_builder.flows import DecisionsRule, DecisionsCondition
from ibm_watsonx_orchestrate.flow_builder.types import DecisionTableColumn

rule1 = DecisionsRule()
rule1.condition("flow.input.grade", DecisionsCondition().equal("A"))
rule1.condition("flow.input.loan_amount", DecisionsCondition().less_than(100000))
rule1.action("flow.output.insurance_required", False)

decisions_node = aflow.decisions(
    name="assess_rate",
    display_name="Assess Insurance Rate",
    rules=[rule1, rule2, ...],
    default_actions={"flow.output.error": "No matching rule"},
    decision_table_columns=[
        DecisionTableColumn(variable="flow.input.grade", display_name="Grade"),
        DecisionTableColumn(variable="flow.output.insurance_rate", display_name="Rate"),
    ]
)
```

### `DecisionsCondition` Methods

| Method | Example |
|---|---|
| `.equal(value)` | `.equal("A")` |
| `.not_equal(value)` | `.not_equal("B")` |
| `.less_than(value)` | `.less_than(100000)` |
| `.greater_than_or_equal(value)` | `.greater_than_or_equal(600000)` |
| `.in_range(low, high, incl_low, incl_high)` | `.in_range(100000, 300000, True, False)` |

See [`assets/decisions_flow.py`](./assets/decisions_flow.py) for a complete insurance rate example.

---

## User Flow Node — `aflow.userflow()`

Human-in-the-loop interaction — collect input or display output in chat. See [`forms-and-userflow.md`](./forms-and-userflow.md) for the full field type reference.

```python
user_flow = aflow.userflow()
user_flow.spec.display_name = "Approval Step"

# Multi-user assignment
from ibm_watsonx_orchestrate.flow_builder.types import UserAssignmentPolicy
user_flow.assign_to(
    policy=UserAssignmentPolicy.USER,
    assignees="flow.private.designated_approver"
)
# or: UserAssignmentPolicy.FLOW_INITIATOR (default)

aflow.sequence(START, user_flow, END)
```

See [`assets/approval_flow.py`](./assets/approval_flow.py) and [`assets/masking_flow.py`](./assets/masking_flow.py).

---

## Document Nodes

See [`document-processing.md`](./document-processing.md) for the full reference.

| Node | Method | Purpose |
|---|---|---|
| Text extractor | `aflow.docproc()` | Extract raw text + KVPs from documents |
| Field extractor | `aflow.docext()` | Extract specific named fields using an LLM |
| Classifier | `aflow.docclassifier()` | Classify documents into defined classes |

See [`assets/document_extraction_flow.py`](./assets/document_extraction_flow.py).
