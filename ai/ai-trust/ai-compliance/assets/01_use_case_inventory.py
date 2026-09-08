"""
AI Use Case Inventory Management with IBM watsonx governance

Demonstrates how to programmatically create and manage inventories and
AI use cases using the IBM AI Governance Facts Client SDK.

Capabilities shown:
  - List governance inventories
  - Create AI use cases within an inventory
  - Add custom facts (compliance metadata) to use cases
  - Create approaches for tracking model versions

SDK reference: https://github.com/IBM/ai-governance-factsheet-samples
API patterns verified against IBM's official sample notebooks.

For compliance workflows (regulation mapping, risk assessment,
position reporting), use the IBM OpenPages Governance Console:
  https://www.ibm.com/docs/en/openpages/9.2.0?topic=governance-integrating-watsonxgovernance

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"
  export WXG_CONTAINER_TYPE="project"
  export WXG_CONTAINER_ID="your-project-id"
  export WXG_CATALOG_ID="your-catalog-id"

Usage:
  python 01_use_case_inventory.py
"""

import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# ── Validate credentials ──────────────────────────────────────────────
WATSONX_APIKEY = os.environ.get("WATSONX_APIKEY")
CONTAINER_TYPE = os.environ.get("WXG_CONTAINER_TYPE", "project")
CONTAINER_ID = os.environ.get("WXG_CONTAINER_ID")
CATALOG_ID = os.environ.get("WXG_CATALOG_ID")

if not WATSONX_APIKEY:
    print("ERROR: WATSONX_APIKEY environment variable is not set.")
    sys.exit(1)
if not CONTAINER_ID:
    print("ERROR: WXG_CONTAINER_ID environment variable is not set.")
    sys.exit(1)


# ── Initialize the governance facts client ────────────────────────────
from ibm_aigov_facts_client import AIGovFactsClient

facts_client = AIGovFactsClient(
    api_key=WATSONX_APIKEY,
    experiment_name="compliance_demo",
    container_type=CONTAINER_TYPE,
    container_id=CONTAINER_ID,
    disable_tracing=True,
    external_model=True,
)
print("AIGovFactsClient initialized.\n")


# ── Inventory management ──────────────────────────────────────────────

def list_inventories():
    """List all governance inventories accessible to this account."""
    print("=" * 60)
    print("GOVERNANCE INVENTORIES")
    print("=" * 60)

    try:
        inventories = facts_client.assets.list_inventories()
        if not inventories:
            print("  No inventories found.")
            return

        for inv in inventories:
            name = inv.get("name", "unnamed")
            inv_id = inv.get("metadata", {}).get("asset_id", "unknown")
            print(f"  - {name} (ID: {inv_id})")
    except Exception as e:
        print(f"  Error listing inventories: {e}")


# ── AI use case management ────────────────────────────────────────────

def create_use_case(name: str, description: str, catalog_id: str):
    """Create a new AI use case in the governance inventory.

    Uses facts_client.assets.create_ai_usecase() — verified against
    IBM's official AI-usecase Approach notebook.

    Args:
        name: Name of the AI use case.
        description: Description of the use case.
        catalog_id: ID of the catalog/inventory to create the use case in.

    Returns:
        The created use case object.
    """
    print(f"\nCreating AI use case: '{name}'")
    try:
        use_case = facts_client.assets.create_ai_usecase(
            catalog_id=catalog_id,
            name=name,
            description=description,
        )
        print(f"  Created successfully. ID: {use_case.get_id()}")
        return use_case
    except Exception as e:
        print(f"  Error creating use case: {e}")
        return None


def add_custom_facts(use_case, facts: dict):
    """Add custom metadata/facts to an AI use case.

    Uses individual set_custom_fact() calls — each fact is a key-value
    pair stored on the use case record. Verified against IBM's official
    End-to-End Workflow notebook.
    """
    print(f"  Adding custom facts...")
    try:
        for fact_id, value in facts.items():
            use_case.set_custom_fact(fact_id=fact_id, value=value)
            print(f"    {fact_id}: {value}")
    except Exception as e:
        print(f"  Error adding custom facts: {e}")


def create_approach(use_case, name: str, description: str):
    """Create an approach (model version track) within a use case.

    Approaches let you track different modeling strategies for the
    same use case — e.g., "Decision Tree" vs "Random Forest".
    """
    print(f"  Creating approach: '{name}'")
    try:
        approach = use_case.create_approach(
            name=name,
            description=description,
        )
        print(f"    Approach created. ID: {approach.get_id()}")
        return approach
    except Exception as e:
        print(f"    Error creating approach: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("AI Compliance — Use Case Inventory Management\n")

    # Step 1: List existing inventories
    list_inventories()

    # Step 2: Create sample use cases
    with open("sample_data/sample_use_cases.json") as f:
        use_cases = json.load(f)

    print("\n" + "=" * 60)
    print("CREATING AI USE CASES")
    print("=" * 60)

    if not CATALOG_ID:
        print("\n  WXG_CATALOG_ID not set. Skipping use case creation.")
        print("  To create use cases, set WXG_CATALOG_ID to your inventory's catalog ID.")
        print("  You can find this in the watsonx governance console under Inventories.")
    else:
        for uc_data in use_cases:
            use_case = create_use_case(
                name=uc_data["name"],
                description=uc_data["description"],
                catalog_id=CATALOG_ID,
            )

            if use_case:
                # Add compliance metadata as custom facts
                add_custom_facts(use_case, {
                    "risk_level": uc_data["risk_level"],
                    "model_type": uc_data["model_type"],
                    "applicable_regulations": ", ".join(uc_data["regulations"]),
                    "deployment_region": uc_data["region"],
                    "use_case_owner": uc_data["owner"],
                    "lifecycle_status": uc_data["status"],
                })

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("  1. View use cases in the watsonx governance console")
    print("  2. Run 02_governed_tool_management.py to register AI tools in the catalog")
    print("")
    print("  For compliance workflows (regulation mapping, risk assessment,")
    print("  position reporting), use the IBM OpenPages Governance Console:")
    print("    https://www.ibm.com/docs/en/openpages/9.2.0?topic=governance-integrating-watsonxgovernance")
