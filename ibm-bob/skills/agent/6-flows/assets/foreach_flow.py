"""
foreach_flow.py — Foreach loop with sequential and parallel processing policies.

Demonstrates:
- aflow.foreach() to iterate over a list
- ForeachPolicy.SEQUENTIAL and ForeachPolicy.PARALLEL
- item_schema to define per-item type
- Nested tool node inside the foreach sub-flow

Flow:  START
         → get_customer_list (tool — returns list of CustomerRecord)
         → foreach each customer [SEQUENTIAL]
             → send_invitation_email (tool)
         → END
"""

from typing import List
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END
from ibm_watsonx_orchestrate.flow_builder.types import ForeachPolicy


# ── Schemas ───────────────────────────────────────────────────────────────────

class CustomerName(BaseModel):
    name: str = Field(description="Customer name to look up")

class CustomerRecord(BaseModel):
    email:      str = Field(description="Customer email address")
    first_name: str = Field(description="Customer first name")
    last_name:  str = Field(description="Customer last name")

class InvitationResult(BaseModel):
    sent_count: int = Field(description="Number of invitations sent")


# ── Tool stubs ────────────────────────────────────────────────────────────────

def get_emails_from_customer(name: str) -> List[CustomerRecord]:
    """Return a list of customer records for the given customer name."""
    return [
        CustomerRecord(email="alice@example.com", first_name="Alice", last_name="Smith"),
        CustomerRecord(email="bob@example.com",   first_name="Bob",   last_name="Jones"),
    ]

def send_invitation_email(email: str, first_name: str, last_name: str) -> dict:
    """Send an invitation email to a single customer."""
    print(f"Sending invitation to {first_name} {last_name} <{email}>")
    return {"sent": True, "recipient": email}


# ── Flow: sequential foreach ─────────────────────────────────────────────────

@flow(
    name="send_invitation_sequential",
    display_name="Send Invitations (Sequential)",
    description="Fetch customer list and send an invitation to each customer one at a time.",
    input_schema=CustomerName
)
def build_sequential_foreach_flow(aflow: Flow) -> Flow:
    get_list_node = aflow.tool(get_emails_from_customer)

    foreach = aflow.foreach(item_schema=CustomerRecord) \
        .policy(kind=ForeachPolicy.SEQUENTIAL)

    send_node = foreach.tool(send_invitation_email)
    foreach.sequence(START, send_node, END)

    aflow.edge(START,         get_list_node)
    aflow.edge(get_list_node, foreach)
    aflow.edge(foreach,       END)
    return aflow


# ── Flow: parallel foreach ────────────────────────────────────────────────────

@flow(
    name="send_invitation_parallel",
    display_name="Send Invitations (Parallel)",
    description="Fetch customer list and send invitations concurrently.",
    input_schema=CustomerName
)
def build_parallel_foreach_flow(aflow: Flow) -> Flow:
    get_list_node = aflow.tool(get_emails_from_customer)

    foreach = aflow.foreach(item_schema=CustomerRecord) \
        .policy(kind=ForeachPolicy.PARALLEL)   # process all items concurrently

    send_node = foreach.tool(send_invitation_email)
    foreach.sequence(START, send_node, END)

    aflow.edge(START,         get_list_node)
    aflow.edge(get_list_node, foreach)
    aflow.edge(foreach,       END)
    return aflow
