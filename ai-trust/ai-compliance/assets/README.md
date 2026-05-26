# AI Compliance — Technical Assets

Python scripts for managing AI compliance using IBM watsonx governance APIs — use case inventory management and governed tool catalog.

For compliance workflows (regulation mapping, risk assessment, position reporting), use the **IBM OpenPages Governance Console** integrated with watsonx governance. See [Integration docs](https://www.ibm.com/docs/en/openpages/9.2.0?topic=governance-integrating-watsonxgovernance).

## What's Inside

| Script | What It Does |
|--------|-------------|
| `01_use_case_inventory.py` | Create and manage AI use cases and governance inventories using the IBM AI Governance Facts Client SDK. Add custom facts (compliance metadata) to track risk level, regulations, and ownership. |
| `02_governed_tool_management.py` | Register, list, and manage AI tools in the watsonx governance tool catalog |

## Prerequisites

- Python >= 3.11
- IBM Cloud API key with access to watsonx governance
- For script 01: watsonx governance project/space ID and catalog ID
- `pip install -r requirements.txt`

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set credentials
export WATSONX_APIKEY="your-ibm-cloud-api-key"
export WXG_CONTAINER_TYPE="project"
export WXG_CONTAINER_ID="your-project-id"
export WXG_CATALOG_ID="your-catalog-id"

# 3. Run scripts
python 01_use_case_inventory.py
python 02_governed_tool_management.py
```

## SDK Reference

### AI Governance Facts Client (script 01)

Verified against [IBM's official sample notebooks](https://github.com/IBM/ai-governance-factsheet-samples).

```python
from ibm_aigov_facts_client import AIGovFactsClient

# Initialize client
client = AIGovFactsClient(
    api_key="your-api-key",
    experiment_name="my_experiment",
    container_type="project",
    container_id="your-project-id",
    disable_tracing=True,
    external_model=True,
)

# List inventories
inventories = client.assets.list_inventories()

# Create an AI use case
use_case = client.assets.create_ai_usecase(
    catalog_id="your-catalog-id",
    name="Credit Risk Scoring",
    description="Predictive model for loan risk assessment",
)

# Add compliance metadata as custom facts
use_case.set_custom_fact(fact_id="risk_level", value="high")
use_case.set_custom_fact(fact_id="regulations", value=["EU AI Act", "ECOA"])
use_case.set_custom_fact(fact_id="owner", value="Risk Analytics Team")

# Create an approach (model version track)
approach = use_case.create_approach(
    name="Gradient Boosting",
    description="XGBoost-based credit scoring model",
)
```

### Governed Tool Catalog (script 02)
```python
from ibm_watsonx_gov.tools.clients.ai_tool_client import list_tools, register_tool

tools = list_tools(search_text="credit", limit=10)
register_tool(payload={"tool_name": "my_tool", "description": "..."})
```

## Compliance Workflows (OpenPages Governance Console)

The following compliance capabilities are available through the **IBM OpenPages Governance Console** integrated with watsonx governance — not via the Python SDK:

| Capability | How to Access |
|-----------|--------------|
| Map AI use cases to regulations (EU AI Act, NIST AI RMF, etc.) | OpenPages Regulatory Compliance Management (RCM) solution |
| Risk identification and assessment | OpenPages risk assessment workflows with questionnaires |
| Position reporting and compliance gap analysis | OpenPages dashboards and reports |
| Mandate management | Sample AI Mandates loaded via FastMap import |
| AI Risk Atlas | Built-in content loaded during OpenPages integration setup |

### Setting up OpenPages integration

1. Provision an OpenPages instance with "Model Risk Governance" solution
2. Integrate with watsonx governance ([setup guide](https://www.ibm.com/docs/en/openpages/9.2.0?topic=governance-integrating-watsonxgovernance))
3. Load solution files (questionnaire templates, risk atlas content, sample AI mandates)
4. Create AI use cases in the Governance Console to access compliance workflows

### Key resources

- [Integrating watsonx governance with Governance Console](https://www.ibm.com/docs/en/openpages/9.2.0?topic=governance-integrating-watsonxgovernance)
- [Managing risk and compliance with Governance Console](https://dataplatform.cloud.ibm.com/docs/content/svc-watsonxgov/wxgov-console.html?context=wx)
- [Creating use cases in Governance Console](https://dataplatform.cloud.ibm.com/docs/content/svc-watsonxgov/wxgov-model-use-cases.html?context=wx)
- [IBM AI Governance Facts Client samples (GitHub)](https://github.com/IBM/ai-governance-factsheet-samples)
- [OpenPages REST API V2](https://cloud.ibm.com/apidocs/openpages)
