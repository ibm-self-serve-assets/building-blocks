"""
Sample tools for the Customer Support Assistant agent.

These tools demonstrate the @tool decorator pattern used by
watsonx Orchestrate ADK. Each tool is self-contained — all data
is embedded since tools run in an isolated cloud environment.
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Dict, List, Optional, Any


# ── Embedded sample data ──────────────────────────────────────────────
CUSTOMERS = [
    {
        "id": "CUST001",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "plan": "Premium",
        "status": "active",
        "orders": ["ORD-1001", "ORD-1002"],
    },
    {
        "id": "CUST002",
        "name": "Bob Chen",
        "email": "bob@example.com",
        "plan": "Basic",
        "status": "active",
        "orders": ["ORD-1003"],
    },
    {
        "id": "CUST003",
        "name": "Carol Martinez",
        "email": "carol@example.com",
        "plan": "Premium",
        "status": "inactive",
        "orders": ["ORD-1004", "ORD-1005", "ORD-1006"],
    },
]

ORDERS = [
    {"id": "ORD-1001", "customer_id": "CUST001", "product": "Laptop Pro 15", "status": "delivered", "tracking": "TRK-9991"},
    {"id": "ORD-1002", "customer_id": "CUST001", "product": "USB-C Hub", "status": "shipped", "tracking": "TRK-9992"},
    {"id": "ORD-1003", "customer_id": "CUST002", "product": "Wireless Mouse", "status": "processing", "tracking": None},
    {"id": "ORD-1004", "customer_id": "CUST003", "product": "Monitor 27\"", "status": "delivered", "tracking": "TRK-9994"},
    {"id": "ORD-1005", "customer_id": "CUST003", "product": "Keyboard", "status": "returned", "tracking": "TRK-9995"},
    {"id": "ORD-1006", "customer_id": "CUST003", "product": "Webcam HD", "status": "cancelled", "tracking": None},
]


# ── Tool definitions ──────────────────────────────────────────────────

@tool
def get_customer(
    customer_id: Optional[str] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Look up a customer by ID or email address.

    Args:
        customer_id: The unique customer identifier (e.g., CUST001)
        email: The customer's email address

    Returns:
        Customer record with name, plan, status, and order history
    """
    for customer in CUSTOMERS:
        if customer_id and customer["id"] == customer_id:
            return {"status": "found", "customer": customer}
        if email and customer["email"] == email:
            return {"status": "found", "customer": customer}

    return {"status": "not_found", "message": "No customer found with the provided criteria."}


@tool
def get_order_status(
    order_id: str,
) -> Dict[str, Any]:
    """
    Check the status and tracking information for an order.

    Args:
        order_id: The order identifier (e.g., ORD-1001)

    Returns:
        Order details including product, status, and tracking number
    """
    for order in ORDERS:
        if order["id"] == order_id:
            return {"status": "found", "order": order}

    return {"status": "not_found", "message": f"Order {order_id} not found."}


@tool
def create_support_ticket(
    customer_id: str,
    subject: str,
    description: str,
    priority: Optional[str] = "medium",
) -> Dict[str, Any]:
    """
    Create a support ticket for an unresolved customer issue.

    Args:
        customer_id: The customer's ID
        subject: Brief summary of the issue
        description: Detailed description of the problem
        priority: Ticket priority - low, medium, or high (default: medium)

    Returns:
        Confirmation with the new ticket ID
    """
    ticket_id = f"TKT-{hash(subject) % 10000:04d}"
    return {
        "status": "created",
        "ticket": {
            "id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "description": description,
            "priority": priority,
        },
    }
