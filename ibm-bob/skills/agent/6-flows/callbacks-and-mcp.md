# Callbacks and MCP Integration

---

## Flow Callbacks — `aflow.add_callback()`

Register a deployed tool to be invoked when specific lifecycle events occur during a flow. Callbacks are **fire-and-forget** — the flow engine invokes the tool and ignores its return value.

```python
from ibm_watsonx_orchestrate.flow_builder.flow_callback_types import FlowCallbackEventKind

@flow(name="my_flow", input_schema=FlowInput, output_schema=FlowOutput)
def build_flow(aflow: Flow) -> Flow:
    node = aflow.tool(my_tool)
    aflow.sequence(START, node, END)

    # Register callback for flow-level events
    aflow.add_callback(
        tool="flow_audit_logger",                       # deployed tool name
        events=[
            FlowCallbackEventKind.ON_FLOW_START,
            FlowCallbackEventKind.ON_FLOW_END,
            FlowCallbackEventKind.ON_FLOW_ERROR,
        ]
    )

    # Register callback for task-level events with batching
    aflow.add_callback(
        tool="monitoring_toolkit:task_event_handler",  # toolkit:tool_name format
        events=[
            FlowCallbackEventKind.ON_TASK_WAIT,
            FlowCallbackEventKind.ON_TASK_ERROR,
            FlowCallbackEventKind.ON_TASK_MESSAGE,
        ],
        batch_interval=30_000                           # batch events for 30 seconds
    )
    return aflow
```

### `add_callback()` Parameters

| Parameter | Required | Description |
|---|---|---|
| `tool` | ✅ | Deployed tool identifier (see formats below) |
| `events` | ✅ | List of `FlowCallbackEventKind` values |
| `batch_interval` | | Milliseconds to accumulate events before dispatching. Server default if omitted. |

### Tool Identifier Formats

| Format | Example |
|---|---|
| Tool name only | `"audit_logger"` |
| Tool name + UUID | `"audit_logger:abc-123-def-456"` |
| Toolkit-scoped | `"monitoring_toolkit:task_handler"` |
| Toolkit + UUID | `"monitoring_toolkit:task_handler:abc-123"` |

### `FlowCallbackEventKind` Values

| Event | Wire value | When it fires |
|---|---|---|
| `ON_FLOW_START` | `flow:on_flow_start` | Flow began execution |
| `ON_FLOW_END` | `flow:on_flow_end` | Flow completed successfully |
| `ON_FLOW_ERROR` | `flow:on_flow_error` | Flow failed with error |
| `ON_FLOW_ABORT` | `flow:on_flow_abort` | External action aborted the flow |
| `ON_FLOW_DELETE` | `flow:on_flow_delete` | Flow instance was deleted |
| `ON_TASK_WAIT` | `task:on_task_wait` | Task waiting for user input (elicitation) |
| `ON_TASK_ERROR` | `task:on_task_error` | Task failed |
| `ON_TASK_MESSAGE` | `task:on_task_message` | Task generated a message |

### Callback Payload Schema

Your callback tool receives a `FlowCallbackEventsPayload`:

```
FlowCallbackEventsPayload
├── events: List[FlowCallbackEventPayload]
│   ├── event: EventMetadata
│   │   ├── id, kind, created_at, instance_id
│   │   ├── flow_name, environment_id, state
│   │   ├── parent_instance_id (child flows only)
│   │   ├── task_id, task_name, task_display_name (ON_TASK_* only)
│   │   └── error: {message, code} (ON_FLOW_ERROR / ON_TASK_ERROR only)
│   ├── output: dict (present only when state = completed)
│   └── elicitation: ElicitationDetails (present only when state = input_required)
│       ├── mode, message, elicitationId
│       ├── requestedSchema
│       └── meta.assignee, meta.response_items
```

### Limitations on Flow Callbacks

When using a **Flow as a callback tool**, the callback flow must **not contain user activity nodes** (userflow). Callback flows run asynchronously and cannot deliver user interactions to the originating chat thread.

> **Recommended:** Use OpenAPI tools as callbacks — clean, stateless, no user interaction complexity.

See [`assets/callback_flow.py`](./assets/callback_flow.py) for a complete callback example.

---

## Direct FlowCallback Construction

Alternative to `add_callback()` for explicit spec manipulation:

```python
from ibm_watsonx_orchestrate.flow_builder.types import FlowCallback
from ibm_watsonx_orchestrate.flow_builder.flow_callback_types import FlowCallbackEventKind

callback = FlowCallback(
    tool="audit_toolkit:audit_logger:xyz-789-ghi-012",
    events=[FlowCallbackEventKind.ON_FLOW_START, FlowCallbackEventKind.ON_FLOW_END],
    batch_interval=60_000
)
aflow.spec.callbacks.append(callback)
```

Prefer `add_callback()` unless you need to manipulate the spec list directly.

---

## MCP Flow Server (Public Preview)

The Flow MCP server exposes each imported flow as a set of MCP tools, enabling MCP-compatible clients to discover, invoke, and query flows.

### Connection

```
Endpoint: https://api.<hostname>/instances/<tenant_id>/v1/orchestrate/flows/mcp
Auth: Bearer token (generated from API key — refresh when expired)
```

### Tool Registration Per Flow

Each flow model registers **3 tools**:

| Tool name | Pattern | Purpose |
|---|---|---|
| Synchronous execution | `run_flow__<model_name>` | Run and wait for completion or user input |
| Asynchronous execution | `run_flow_async__<model_name>` | Start and return `instance_id` immediately |
| Status query | `query_flow__<model_name>` | Check status + output for an instance |

Draft vs versioned: draft uses `run_flow__<name>`, specific version uses `run_flow__<name>_<version>`.

### Synchronous Execution

Runs the flow and waits for completion or interruption.

**Input:** flow schema fields + optional `_context` object (`thread_id`, `environment_id`, `channel_id`, `agent_id`, `agent_version`).

**Returns on completion:**
```json
{
  "output": { "<your flow output fields>" },
  "status": { "instance_id": "abc-123", "state": "completed", ... }
}
```

**Returns when user input required:**
```json
{
  "status": { "instance_id": "abc-123", "state": "input_required", ... }
}
```

### Asynchronous Execution (Claim-Check)

Start the flow and return `instance_id` immediately:

```json
{ "instance_id": "flow-abc123-def456" }
```

Then poll with `query_flow__<name>` using the `instance_id`.

### Elicitation Handling

When a flow needs user input, an elicitation request is automatically issued. Default timeout: **5 minutes**.

On timeout, recover by calling `submit_flow_elicitation`:
```json
{
  "instance_id": "flow-abc123",
  "elicitation_id": "task-789",
  "response": {
    "action": "accept",
    "content": { "...user response fields..." }
  }
}
```

### Management Tools

| Tool | Purpose |
|---|---|
| `subscribe_flow` | Subscribe to flow events |
| `replay_flow_pending_elicitation` | Replay a timed-out elicitation |
| `submit_flow_elicitation` | Submit response to a pending elicitation |
| `list_flows` | List available flow instances |
| `cancel_flow` | Cancel a running flow instance |

### Tool Lifecycle States

| State | Description |
|---|---|
| Active | Tool available and executable |
| Deactivated | Tool registered but marked `[DEACTIVATED]` |
| Deleted | Tool registered but marked `[DELETED]` |

Clients are notified via `notifications/tools/list_changed` when availability changes.

### Authorization Model

- Each request is authenticated per principal
- Initiators can query, subscribe, replay, and cancel their **own** flow instances
- Session binding: operations validated per MCP session

### MCP Context Forge

Compatible with MCP Context Forge for enhanced context management. **Note:** Current Context Forge clients do not support MCP elicitations — human-in-the-loop features are unavailable through that path.

See [`assets/mcp_flow_tools.json`](./assets/mcp_flow_tools.json) for the full tool schema reference.
