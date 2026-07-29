#!/usr/bin/env python3
"""
Purchase Approval Workflow
Human-in-the-loop approval with conditional branching
"""

from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END, UserFieldKind


class PurchaseRequest(BaseModel):
    """Purchase request input"""
    item: str = Field(description="Item to purchase")
    amount: float = Field(description="Purchase amount")


class PurchaseResult(BaseModel):
    """Purchase result output"""
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
    """
    Purchase approval workflow with user form
    
    Flow: Start → Prepare → User Form → Branch → [Process/Reject] → End
    """
    
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


if __name__ == "__main__":
    print("Purchase approval workflow defined")
    print("Import with: orchestrate tools import -k flow -f approval_workflow.py")

# Made with Bob
