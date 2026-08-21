# Agentic Workflows — Getting Started

Agentic workflows are a type of **tool** with built-in orchestration capabilities. They let you sequence agents, tools, and human interactions with branching, looping, and parallel execution — all defined in Python using the `@flow` decorator.

Use a flow when:
- Repeatable, predictable sequencing of agents/tools is required
- Human-in-the-loop approvals or decisions are needed
- Long-running processes (minutes to hours) are involved
- Scheduling at specific times or intervals is necessary

> **Never use `FlowBuilder`** — it is fully deprecated and removed. The `@flow` decorator is the only current API.

---

## The `@flow` Decorator

```python
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END

class MyInput(BaseModel):
    message: str = Field(description="Input message")

class MyOutput(BaseModel):
    result: str = Field(description="Output result")

class MyPrivate(BaseModel):
    internal_id: str = Field(description="Internal state not exposed to users")

@flow(
    name="my_flow",                                  # unique identifier (snake_case)
    display_name="My Flow",                          # shown in UI
    description="What this flow does",               # used by agents to decide when to invoke
    input_schema=MyInput,                            # Pydantic model for inputs
    output_schema=MyOutput,                          # Pydantic model for outputs
    private_schema=MyPrivate,                        # internal state — NOT exposed to users
    initiators=["my_agent"],                         # agents that can start this flow
    schedulable=False,                               # set True to enable scheduling
    suppress_agent_summarization=True,               # skip post-flow summary by agent
    llm_model="meta-llama/llama-3-3-70b-instruct",  # LLM for this flow's auto-mapping
    agent_conversation_memory_turns_limit=10         # conversation history limit
)
def build_my_flow(aflow: Flow) -> Flow:
    """Flow docstring — used as description if description param is omitted."""
    # build nodes and edges here
    return aflow
```

### `@flow` Decorator Parameters

| Parameter | Type | Description |
|---|---|---|
| `name` | `string` | Unique identifier. Defaults to function name. |
| `display_name` | `string` | Human-readable name shown in UI. |
| `description` | `string` | What this flow does. Defaults to docstring. |
| `input_schema` | `type[BaseModel]` | Pydantic model defining flow inputs. |
| `output_schema` | `type[BaseModel]` | Pydantic model defining flow outputs. |
| `private_schema` | `type[BaseModel]` | Internal flow state — not exposed to users. |
| `initiators` | `Sequence[str]` | Agent names that can invoke this flow. |
| `schedulable` | `bool` | Enable scheduling. Default: `False`. |
| `suppress_agent_summarization` | `bool` | Skip agent summary after flow ends. Default: `True`. |
| `llm_model` | `string` | LLM used for auto data-mapping. |
| `agent_conversation_memory_turns_limit` | `int` | Max conversation turns retained in memory. |

---

## Key Concepts

### Nodes
Individual units of work. Every flow must have exactly one `START` and at least one `END`.

| Node type | Method | Purpose |
|---|---|---|
| Tool | `aflow.tool()` | Call an imported tool |
| Agent | `aflow.agent()` | Call an imported agent |
| Script | `aflow.script()` | Inline Python logic |
| Branch (conditions) | `aflow.conditions()` | If-else conditional routing |
| Parallel | `aflow.parallel()` / `aflow.parallel_conditions()` | Concurrent branches |
| Foreach | `aflow.foreach()` | Iterate over a list |
| Loop | `aflow.loop()` | Repeat until condition is false |
| Timer | `aflow.timer()` | Delay between actions |
| Prompt | `aflow.prompt()` | LLM call for extract/classify/generate |
| Decisions | `aflow.decisions()` | Decision table with rules |
| User flow | `aflow.userflow()` | Human-in-the-loop interactions |
| Doc field extractor | `aflow.docext()` | Extract fields from documents |
| Doc classifier | `aflow.docclassifier()` | Classify documents |
| Doc text extractor | `aflow.docproc()` | Extract text from documents |

### Edges
Connections between nodes.
- `aflow.sequence(START, node1, node2, END)` — sequential shorthand
- `aflow.edge(node1, node2)` — single edge (chainable)
- Multiple edges from one node → **parallel execution**
- `aflow.edge(node, next, button_label="Submit")` — button-triggered transition

### Expressions
Used in branching conditions, loop evaluators, and data mapping:

| Pattern | What it refers to |
|---|---|
| `flow.input.<field>` | Flow input field |
| `flow.output.<field>` | Flow output field |
| `flow.private.<field>` | Private state field |
| `flow.nodes['<node_name>'].output.<field>` | Another node's output |
| `flow.<node_name>.output.<field>` | Shorthand node output |
| `self.output.<field>` | Current node's output (script nodes) |
| `parent.input.<field>` | Parent flow input (inside sub-flows) |
| `parent._current_index` | Current index in foreach loop |
| `parent._current_item` | Current item in foreach loop |

---

## Import CLI

```bash
# Import a flow as a tool
orchestrate tools import -k flow -f path/to/my_flow.py

# Import with translations
orchestrate tools import -k flow -f path/to/my_flow.py --translation translations.csv
```

## Manage Flows

```bash
# List all imported flows
orchestrate tools list -k flow

# Export a flow spec
orchestrate tools export -k flow my_flow_name

# Update (re-import)
orchestrate tools import -k flow -f path/to/my_flow.py

# Remove
orchestrate tools remove -k flow my_flow_name
```

---

## Testing a Flow Locally

```python
import asyncio
from .my_flow import build_my_flow

async def main():
    flow_def = build_my_flow()
    compiled = await flow_def.compile_deploy()
    flow_run = await compiled.invoke({"message": "hello"})
    print(f"Status: {flow_run.status}, Output: {flow_run.output}")

asyncio.run(main())
```

See [`assets/hello_flow.py`](./assets/hello_flow.py) for a complete working example with event handlers and async polling.

---

## Add a Flow to an Agent

After importing, reference the flow by name in an agent's `tools` list:

```yaml
name: my_agent
tools:
  - my_flow
```

---

## Context Window Management (FlowContextWindow)

For flows with large data, configure compression to prevent auto-mapping failures:

```python
from ibm_watsonx_orchestrate.flow_builder.types import FlowContextWindow

@flow(
    name="large_data_flow",
    context_window=FlowContextWindow(
        compression_threshold=4000,           # trigger at 4000 tokens
        compression_instruction="Summarize key facts only, drop raw tables",
        max_tokens=8192,                      # LLM context limit
        allow_compress=True
    )
)
def build_flow(aflow: Flow) -> Flow:
    ...
```

| Field | Description |
|---|---|
| `compression_threshold` | Token count that triggers compression |
| `compression_instruction` | How to summarize/compress the context |
| `max_tokens` | Maximum tokens supported by the LLM |
| `allow_compress` | Whether compression is allowed (default: `True`) |

> If data is not compressed and exceeds token limits, auto-mapping fails with unpredictable agent behavior.
