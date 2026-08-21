# Error Handling in Flows

Configure how a flow responds when a node fails using `NodeErrorHandlerConfig`. Instead of stopping execution, you can retry the node, show a message to the user, or redirect to a recovery path.

`NodeErrorHandlerConfig` can be attached to **tool nodes** and **agent nodes**.

---

## `NodeErrorHandlerConfig` Parameters

| Parameter | Required | Description |
|---|---|---|
| `error_message` | ✅ | Describes the error for observability/logging. Not shown to users unless explicitly exposed via a user flow. |
| `max_retries` | ✅ | Number of retry attempts. `0` = no retries, go straight to `on_error` behavior. |
| `retry_interval` | ✅ | Delay between retries in milliseconds. Only applies when `max_retries > 0`. |
| `on_error` | ✅ | How the flow responds on failure: `"show_message"` or `"branch"` |
| `error_edge_id` | ✅ (when `on_error="branch"`) | ID of the edge to follow on failure. Must match an `aflow.edge(..., id="...")` definition. |

### `on_error` Values

| Value | Behavior |
|---|---|
| `"show_message"` | Stop the flow and display the error message to the user. Use when no alternate path applies. |
| `"branch"` | Redirect execution to a recovery path via `error_edge_id`. Use for expected failures (API unavailable, external service errors). |

---

## Example: Error Branching to User Message

```python
from ibm_watsonx_orchestrate.flow_builder.types import NodeErrorHandlerConfig, UserFieldKind

@flow(name="fetch_with_fallback", output_schema=PetFacts)
def build_flow(aflow: Flow) -> Flow:

    # Recovery user flow — shown when the tool fails
    error_flow = aflow.userflow()
    error_msg = error_flow.field(
        direction="output",
        name="error_display",
        display_name="Error Message",
        kind=UserFieldKind.Text,
        text="Sorry, we couldn't fetch data right now. Please try again later."
    )
    error_flow.edge(START, error_msg)
    error_flow.edge(error_msg, END)

    # Tool with retry + error branching
    fetch_node = aflow.tool(
        "fetchExternalData",
        error_handler_config=NodeErrorHandlerConfig(
            error_message="External data fetch failed — routing to error message",
            max_retries=2,
            retry_interval=1500,
            on_error="branch",
            error_edge_id="fetch_failed"
        )
    )

    # Main path
    aflow.sequence(START, fetch_node, END)

    # Error path — edge ID must match error_edge_id above
    aflow.edge(fetch_node, error_flow, id="fetch_failed")
    aflow.edge(error_flow, END)

    return aflow
```

---

## Example: Retry with Show Message Fallback

```python
agent_node = aflow.agent(
    name="call_external_agent",
    agent="weather_agent",
    error_handler_config=NodeErrorHandlerConfig(
        error_message="Weather agent unavailable after retries",
        max_retries=3,
        retry_interval=2000,
        on_error="show_message"    # no branch — just stop with message
    )
)
```

---

## Error Handling in Parallel Branches

Each parallel branch can fail independently. Add `error_handler` per branch node:

```python
parallel = aflow.parallel_conditions(name="processing")

task1 = parallel.script(
    name="task1",
    script="...",
    error_handler=NodeErrorHandlerConfig(
        on_error="show_message",
        max_retries=3
    )
)
```

---

## Checklist

1. Set `max_retries=0` if the failure is deterministic (wrong credentials, schema mismatch) — retrying won't help
2. Use `on_error="branch"` for transient external service failures
3. Use `on_error="show_message"` for terminal failures with no recovery path
4. Always define the error edge with a matching `id=` before testing
5. Keep `error_message` meaningful for debugging — it appears in flow logs
6. `retry_interval` is in **milliseconds** — `2000` = 2 seconds

See [`assets/approval_flow.py`](./assets/approval_flow.py) for a complete flow with error handling integrated alongside human-in-the-loop.
