"""
hello_flow.py — Minimal @flow example with two sequential tool nodes.

Demonstrates:
- @flow decorator with input/output schemas
- aflow.tool() with Python function references
- aflow.edge() chaining
- compile_deploy(), invoke(), and event-handler patterns for local testing

Usage:
    python -m asyncio hello_flow.py
"""

import asyncio
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END


# ── Schemas ─────────────────────────────────────────────────────────────────

class Name(BaseModel):
    first_name: str = Field(description="Person's first name")
    last_name:  str = Field(description="Person's last name")

class Message(BaseModel):
    msg: str = Field(description="Hello message")


# ── Tool stubs (replace with your real @tool functions) ──────────────────────

def combine_names(first_name: str, last_name: str) -> dict:
    """Combine first and last name into a full name."""
    return {"full_name": f"{first_name} {last_name}"}

def get_hello_message(full_name: str) -> dict:
    """Generate a hello message for the given full name."""
    return {"msg": f"Hello, {full_name}! Welcome to watsonx Orchestrate."}


# ── Flow definition ──────────────────────────────────────────────────────────

@flow(
    name="hello_message_flow",
    display_name="Hello Message Flow",
    description="Combines a name and produces a greeting message.",
    input_schema=Name,
    output_schema=Message
)
def build_hello_message_flow(aflow: Flow = None) -> Flow:
    """Sequence two tools: combine_names → get_hello_message."""

    combine_node      = aflow.tool(combine_names)
    hello_message_node = aflow.tool(get_hello_message)

    (aflow
        .edge(START, combine_node)
        .edge(combine_node, hello_message_node)
        .edge(hello_message_node, END))

    return aflow


# ── Test harness ─────────────────────────────────────────────────────────────

async def main():
    flow_def   = build_hello_message_flow()
    compiled   = await flow_def.compile_deploy()

    # --- Option 1: simple invoke (poll for completion) ---
    flow_run = await compiled.invoke({"first_name": "Ada", "last_name": "Lovelace"})

    from ibm_watsonx_orchestrate.experimental.flow_builder.flows.flow import FlowRunStatus
    while flow_run.status not in (FlowRunStatus.COMPLETED, FlowRunStatus.FAILED):
        await asyncio.sleep(1)

    if flow_run.status == FlowRunStatus.COMPLETED:
        print(f"Output: {flow_run.output}")
    else:
        print(f"Error:  {flow_run.error}")

    # --- Option 2: invoke with event handlers ---
    def on_end(result):
        print(f"[handler] Flow completed: {result}")

    def on_error(error):
        print(f"[handler] Flow failed: {error}")

    await compiled.invoke(
        {"first_name": "Alan", "last_name": "Turing"},
        on_flow_end_handler=on_end,
        on_flow_error_handler=on_error
    )


if __name__ == "__main__":
    asyncio.run(main())
