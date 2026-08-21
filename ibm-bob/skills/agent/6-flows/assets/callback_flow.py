"""
callback_flow.py — Flow lifecycle callbacks with FlowCallbackEventKind.

Demonstrates:
- aflow.add_callback() for flow-level and task-level events
- Multiple callbacks on the same flow
- batch_interval for event batching
- Direct FlowCallback construction (advanced pattern)
- Compatible callback tool schema (FlowCallbackEventsPayload)

The callback tools referenced here ("flow_audit_logger", "task_monitor") must
be deployed in your watsonx Orchestrate environment before importing this flow.
"""

from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END
from ibm_watsonx_orchestrate.flow_builder.flow_callback_types import FlowCallbackEventKind


# ── Schemas ───────────────────────────────────────────────────────────────────

class FlowInput(BaseModel):
    message: str = Field(description="Input message to process")

class FlowOutput(BaseModel):
    result: str = Field(description="Processing result")


# ── Tool stub ─────────────────────────────────────────────────────────────────

def process_message(message: str) -> dict:
    """Process the input message."""
    return {"result": f"Processed: {message.upper()}"}


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="flow_with_callbacks",
    display_name="Flow With Lifecycle Callbacks",
    description="Demonstrates flow and task lifecycle callbacks for audit and monitoring.",
    input_schema=FlowInput,
    output_schema=FlowOutput
)
def build_flow_with_callbacks(aflow: Flow) -> Flow:

    node = aflow.tool(process_message)
    aflow.sequence(START, node, END)

    # ── Callback 1: Flow-level audit logging (no batching) ────────────────────
    # "flow_audit_logger" must be a deployed tool that accepts FlowCallbackEventsPayload
    aflow.add_callback(
        tool="flow_audit_logger",
        events=[
            FlowCallbackEventKind.ON_FLOW_START,   # fires when flow begins
            FlowCallbackEventKind.ON_FLOW_END,     # fires on successful completion
            FlowCallbackEventKind.ON_FLOW_ERROR,   # fires on failure
            FlowCallbackEventKind.ON_FLOW_ABORT,   # fires on external abort
        ]
        # no batch_interval — server default applies
    )

    # ── Callback 2: Task-level monitoring with 30-second batch window ─────────
    # Toolkit-scoped tool: "monitoring_toolkit:task_monitor"
    aflow.add_callback(
        tool="monitoring_toolkit:task_monitor",
        events=[
            FlowCallbackEventKind.ON_TASK_WAIT,      # fires when user input required
            FlowCallbackEventKind.ON_TASK_ERROR,     # fires when a task fails
            FlowCallbackEventKind.ON_TASK_MESSAGE,   # fires when a task emits a message
        ],
        batch_interval=30_000   # accumulate events for 30s before dispatching
    )

    return aflow


# ── Advanced: Direct FlowCallback construction ────────────────────────────────

def build_flow_with_direct_callback(aflow: Flow) -> Flow:
    """
    Alternative approach using direct FlowCallback construction.
    Use when you need to manipulate the spec.callbacks list explicitly.
    Prefer add_callback() for normal usage.
    """
    from ibm_watsonx_orchestrate.flow_builder.types import FlowCallback

    callback = FlowCallback(
        tool="audit_toolkit:audit_logger:xyz-789-ghi-012",
        events=[FlowCallbackEventKind.ON_FLOW_START, FlowCallbackEventKind.ON_FLOW_END],
        batch_interval=60_000   # 1 minute batching
    )
    aflow.spec.callbacks.append(callback)
    return aflow
