"""
Governed Tool Management with IBM watsonx governance

Register, list, and manage AI tools in the watsonx governance tool
catalog. Governed tools are metadata records that track which AI tools
are deployed, their configurations, and their governance status.

This integrates with the watsonx governance factsheet/inventory system
to provide a centralized view of all AI tools across the enterprise.

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"

Usage:
  python 04_governed_tool_management.py
"""

import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("WATSONX_APIKEY"):
    print("ERROR: WATSONX_APIKEY environment variable is not set.")
    sys.exit(1)


# ── Import watsonx governance SDK ─────────────────────────────────────
# The tool catalog API is available through the ibm_watsonx_gov package.
# Note: These APIs require WATSONX_APIKEY to be set.

def list_tools(search_text: str = None, limit: int = 50) -> list:
    """List governed tools in the watsonx governance catalog.

    Args:
        search_text: Optional search filter.
        limit: Maximum number of tools to return.

    Returns:
        List of governed tool records.
    """
    from ibm_watsonx_gov.tools.clients.ai_tool_client import list_tools as _list_tools

    kwargs = {"limit": limit}
    if search_text:
        kwargs["search_text"] = search_text

    return _list_tools(**kwargs)


def register_tool(tool_definition: dict) -> dict:
    """Register a new AI tool in the governance catalog.

    Args:
        tool_definition: Tool metadata including name, description,
            category, framework, and other governance-relevant fields.

    Returns:
        Registration result.
    """
    from ibm_watsonx_gov.tools.clients.ai_tool_client import register_tool as _register_tool

    return _register_tool(payload=tool_definition)


def get_tool(tool_id: str, inventory_id: str) -> dict:
    """Retrieve full metadata for a specific governed tool.

    Args:
        tool_id: The tool's unique identifier.
        inventory_id: The inventory containing the tool.

    Returns:
        Complete tool metadata record.
    """
    from ibm_watsonx_gov.tools.clients.ai_tool_client import get_tool as _get_tool

    return _get_tool(tool_id=tool_id, inventory_id=inventory_id)


def delete_tool(tool_id: str, inventory_id: str) -> dict:
    """Delete a governed tool record from the catalog.

    Args:
        tool_id: The tool's unique identifier.
        inventory_id: The inventory containing the tool.

    Returns:
        Deletion confirmation.
    """
    from ibm_watsonx_gov.tools.clients.ai_tool_client import delete_tool as _delete_tool

    return _delete_tool(tool_id=tool_id, inventory_id=inventory_id)


# ── Sample tool definitions ───────────────────────────────────────────
SAMPLE_TOOLS = [
    {
        "tool_name": "credit_risk_scorer",
        "description": "Predictive ML model that scores credit risk for loan applicants.",
        "category": "predictive_ml",
        "framework": "scikit-learn",
        "version": "1.2.0",
        "owner": "Risk Analytics Team",
        "deployment": "watsonx.ai",
    },
    {
        "tool_name": "customer_support_rag",
        "description": "RAG pipeline for customer support knowledge base Q&A.",
        "category": "generative_ai",
        "framework": "langchain",
        "version": "0.3.1",
        "owner": "Customer Experience Team",
        "deployment": "watsonx.ai",
    },
    {
        "tool_name": "content_safety_guardrail",
        "description": "Real-time content safety screening for HAP, PII, and jailbreak detection.",
        "category": "guardrails",
        "framework": "ibm-watsonx-gov",
        "version": "1.4.2",
        "owner": "AI Trust Team",
        "deployment": "Code Engine",
    },
]


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("AI Compliance — Governed Tool Management\n")

    # Step 1: List existing tools
    print("=" * 60)
    print("EXISTING GOVERNED TOOLS")
    print("=" * 60)

    try:
        tools = list_tools()
        if tools:
            print(f"\n  Found {len(tools)} governed tool(s):")
            for tool in tools[:10]:  # Show first 10
                if isinstance(tool, dict):
                    name = tool.get("tool_name", tool.get("name", "unnamed"))
                    print(f"    - {name}")
        else:
            print("\n  No governed tools found in catalog.")
    except Exception as e:
        print(f"\n  Could not list tools: {e}")
        print("  This may require additional permissions or configuration.")

    # Step 2: Register sample tools
    print(f"\n{'=' * 60}")
    print("REGISTERING SAMPLE TOOLS")
    print("=" * 60)

    for tool_def in SAMPLE_TOOLS:
        print(f"\n  Registering: {tool_def['tool_name']}")
        try:
            result = register_tool(tool_def)
            print(f"    Status: Registered successfully")
            print(f"    Result: {result}")
        except Exception as e:
            print(f"    Status: Failed — {e}")
            print("    (This is expected if the tool catalog requires specific permissions)")

    # Step 3: Summary
    print(f"\n{'=' * 60}")
    print("GOVERNANCE TOOL CATALOG SUMMARY")
    print("=" * 60)
    print(f"\n  The governed tool catalog provides a centralized registry of all")
    print(f"  AI tools deployed across the enterprise. Each entry tracks:")
    print(f"    - Tool name, description, and version")
    print(f"    - Framework and deployment platform")
    print(f"    - Owner and category")
    print(f"    - Governance metadata and compliance status")
    print(f"\n  Use this catalog to maintain visibility into your AI tool portfolio")
    print(f"  and ensure all tools are properly governed and documented.")
