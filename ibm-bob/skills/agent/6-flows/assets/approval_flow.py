"""
approval_flow.py — Human-in-the-loop approval workflow.

Demonstrates:
- Multi-user assignment (UserAssignmentPolicy.USER / FLOW_INITIATOR)
- form() with text_input_field, boolean_input_field, multiple buttons
- aflow.conditions() for if-else branching based on form input
- NodeErrorHandlerConfig with on_error="branch" for resilient tool calls
- private_schema for internal state
- edge() with button_label for form button routing

Flow:  START
         → init_approver (script — looks up approver)
         → submit_request (tool — creates the request)
         → approval_form (userflow assigned to approver)
             [Approve] → process_approval (tool) → END
             [Reject]  → notify_rejection (tool)  → END
         → [on tool error] error_message (userflow) → END
"""

import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END
from ibm_watsonx_orchestrate.flow_builder.flows.flow import UserFlow
from ibm_watsonx_orchestrate.flow_builder.types import (
    UserAssignmentPolicy,
    UserFieldKind,
    NodeErrorHandlerConfig,
)
from ibm_watsonx_orchestrate.flow_builder.data_map import DataMap, Assignment
from ibm_watsonx_orchestrate_core.types.tools.types import WXOUser


# ── Schemas ───────────────────────────────────────────────────────────────────

class PurchaseRequest(BaseModel):
    item:          str   = Field(description="Item to purchase")
    amount:        float = Field(description="Estimated cost in USD")
    justification: str   = Field(description="Business justification")

class ApprovalResult(BaseModel):
    status:   str           = Field(description="approved or rejected")
    approver: Optional[str] = Field(default=None, description="Approver email")
    comments: Optional[str] = Field(default=None, description="Approver comments")

class PrivateState(BaseModel):
    approver: Optional[WXOUser] = Field(default=None, description="Resolved approver user object")
    request_id: str             = Field(default="", description="Created request ID")


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="purchase_approval_flow",
    display_name="Purchase Approval",
    description="Submit a purchase request and route to the designated approver.",
    input_schema=PurchaseRequest,
    output_schema=ApprovalResult,
    private_schema=PrivateState
)
def build_approval_flow(aflow: Flow = None) -> Flow:

    # ── 1. Init: resolve approver from email ──────────────────────────────────
    init_approver = aflow.script(
        name="init_approver",
        display_name="Find Approver",
        script="""
flow.private.approver = system.user.search_by_email('manager@example.com')[0]
"""
    )

    # ── 2. Submit request (tool call with error handling) ─────────────────────
    submit_node = aflow.tool(
        "createPurchaseRequest",
        name="submit_request",
        display_name="Submit Purchase Request",
        input_schema=PurchaseRequest,
        error_handler_config=NodeErrorHandlerConfig(
            error_message="Failed to create purchase request in the system",
            max_retries=2,
            retry_interval=1500,
            on_error="branch",
            error_edge_id="submit_failed"
        )
    )

    # ── 3. Error user flow (shown if submit fails) ─────────────────────────────
    error_flow = aflow.userflow()
    error_flow.spec.display_name = "Submission Error"
    error_msg = error_flow.field(
        direction="output", name="error_display",
        display_name="Error", kind=UserFieldKind.Text,
        text="We couldn't submit your request. Please try again later."
    )
    error_flow.edge(START, error_msg)
    error_flow.edge(error_msg, END)

    # ── 4. Approval form (assigned to resolved approver) ──────────────────────
    approval_flow: UserFlow = aflow.userflow()
    approval_flow.spec.display_name = "Purchase Approval"
    approval_flow.assign_to(
        policy=UserAssignmentPolicy.USER,
        assignees="flow.private.approver"
    )

    form = approval_flow.form(
        name="approval_form",
        display_name="Purchase Approval Request",
        instructions="Review the purchase request and approve or reject below.",
        submit_button_label="Approve",
        cancel_button_label="Reject"
    )

    form.message_output_field(
        name="request_details",
        label="Request Details",
        message="Item: {flow.input.item} | Amount: ${flow.input.amount} | Reason: {flow.input.justification}"
    )
    form.text_input_field(
        name="comments",
        label="Comments",
        required=False,
        single_line=False,
        placeholder_text="Optional comments for the requester"
    )

    approve_btn = approval_flow.add_button("Approve")
    reject_btn  = approval_flow.add_button("Reject")

    approve_script = approval_flow.script(
        name="mark_approved", script='flow.output.status = "approved"'
    )
    reject_script  = approval_flow.script(
        name="mark_rejected", script='flow.output.status = "rejected"'
    )

    approval_flow.edge(START, form)
    approval_flow.edge(approve_btn, approve_script)
    approval_flow.edge(reject_btn,  reject_script)
    approval_flow.edge(approve_script, END)
    approval_flow.edge(reject_script,  END)

    # ── 5. Process result tools ───────────────────────────────────────────────
    process_approval  = aflow.tool("processApproval",  name="process_approval")
    notify_rejection  = aflow.tool("notifyRejection",  name="notify_rejection")

    # ── 6. Wire the main flow ─────────────────────────────────────────────────
    aflow.edge(START,         init_approver)
    aflow.edge(init_approver, submit_node)
    aflow.edge(submit_node,   approval_flow)
    aflow.edge(approval_flow, process_approval,  button_label="Approve")
    aflow.edge(approval_flow, notify_rejection,  button_label="Reject")
    aflow.edge(process_approval, END)
    aflow.edge(notify_rejection, END)

    # Error branch from submit
    aflow.edge(submit_node, error_flow, id="submit_failed")
    aflow.edge(error_flow,  END)

    return aflow


# ── Test harness ──────────────────────────────────────────────────────────────
async def main():
    flow_def = build_approval_flow()
    compiled = await flow_def.compile_deploy()
    run = await compiled.invoke({
        "item": "MacBook Pro M4",
        "amount": 2499.00,
        "justification": "Required for ML model development work"
    })
    print(f"Flow started — instance: {run.instance_id}")

if __name__ == "__main__":
    asyncio.run(main())
