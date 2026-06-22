# SPEC-01: watsonx.ai Live API Integration

Back to [specs index](README.md) | [main README](../../README.md)

---

## 1. Purpose

The prompt templates in [`docs/agents/`](../agents/) require a human to copy JSON from the terminal and paste it into Prompt Lab manually. This spec wires up the IBM watsonx.ai REST API so that every time the risk engine emits a **CRITICAL** severity alert, it automatically:

1. Calls watsonx.ai to generate a plain-language executive risk summary.
2. Calls watsonx.ai to draft a supplier escalation email.
3. Prints both to the terminal and (optionally) sends them downstream.

This closes the loop between the real-time Kafka pipeline and the AI layer without any human copy-paste step.

**Architecture layer extended:** Layer 5 — Downstream applications and integrations.

**Existing file to extend:** [`code/scrc/risk_engine.py`](../../code/scrc/risk_engine.py) — the `RiskPublisher.publish()` method.

---

## 2. Input

| Property | Value |
|----------|-------|
| Trigger | `Alert.severity == "CRITICAL"` — evaluated in `RiskPublisher.publish()` before Kafka produce |
| Risk event schema | `RiskResult` dataclass — see [`code/scrc/models.py`](../../code/scrc/models.py) |
| Recommendation schema | `Recommendation` dataclass — see [`code/scrc/models.py`](../../code/scrc/models.py) |
| Alert schema | `Alert` dataclass — see [`code/scrc/models.py`](../../code/scrc/models.py) |
| Sample payload | [`docs/assets/sample_risk_event.json`](../assets/sample_risk_event.json) |

---

## 3. Output

| Output | Description |
|--------|-------------|
| Executive summary | Printed to terminal via `rich.console.Console` |
| Supplier email draft | Printed to terminal via `rich.console.Console` |
| Both outputs | Available as strings for further routing (Teams, email, ServiceNow) |

---

## 4. Prerequisites

| Requirement | Details |
|-------------|---------|
| IBM watsonx.ai account | [https://www.ibm.com/products/watsonx-ai](https://www.ibm.com/products/watsonx-ai) |
| watsonx.ai project | Create a project in the watsonx.ai console; copy the Project ID |
| IBM Cloud API key | IAM → API keys → Create — must have watsonx.ai service access |
| watsonx.ai service URL | Region-specific, e.g. `https://us-south.ml.cloud.ibm.com` |
| Python package | `ibm-watsonx-ai` — added to `pyproject.toml` in step 1 |

---

## 5. Implementation steps

### Step 1: Add the dependency

In [`pyproject.toml`](../../pyproject.toml), add `ibm-watsonx-ai>=1.0` to the `[project] dependencies` list:

```toml
dependencies = [
    ...
    "ibm-watsonx-ai>=1.0",
]
```

Then reinstall:

```bash
source .venv/bin/activate
pip install -e .
```

### Step 2: Add `.env` variables

Add the three variables from section 7 to your `.env` file.

### Step 3: Create `code/scrc/watsonx_client.py`

Create a new file with the complete code from section 6.

### Step 4: Update `code/scrc/settings.py`

Add `watsonx_api_key` and `watsonx_project_id` to `AppSettings` as shown in section 6.

### Step 5: Update `code/scrc/risk_engine.py`

Extend `RiskPublisher.publish()` to call `generate_risk_summary` and `generate_supplier_email` when severity is CRITICAL, as shown in section 6.

### Step 6: Test

Run the dry-run and confirm watsonx.ai output appears in the terminal:

```bash
python -m scrc.risk_engine --dry-run --scenario supplier_delay --count 10
```

---

## 6. Complete code

### `code/scrc/watsonx_client.py` — new file

```python
from __future__ import annotations

import json
from typing import Any

try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
except ImportError as exc:
    raise ImportError(
        "ibm-watsonx-ai is not installed. Add it to pyproject.toml dependencies and run pip install -e ."
    ) from exc


DEFAULT_MODEL = "ibm/granite-13b-instruct-v2"

SUMMARY_SYSTEM_PROMPT = """\
You are a supply chain risk control tower assistant.
Convert the following risk event, recommendation, and alert JSON into a structured executive summary.
Keep the output specific, action-oriented, and suitable for a procurement or operations leader.

Output format:
### Situation
One paragraph explaining what happened.

### Business impact
Which component, supplier, shipment, or customer order is affected.

### Recommended actions
3 to 5 concrete actions.

### Owner
Who should own the next step: procurement, supply planning, logistics, or supplier manager.

### Confidence
Use the confidence value from the recommendation. State whether the action should be automatic or human-approved.
"""

EMAIL_SYSTEM_PROMPT = """\
You are a supply chain risk control tower assistant.
Draft a professional escalation email to the affected supplier.
The email should request an updated ETA, explain the business impact, and propose mitigation options.
Keep the tone firm but collaborative. Address it to the supplier operations contact.
"""


def _build_client(api_key: str, url: str) -> APIClient:
    return APIClient(Credentials(api_key=api_key, url=url))


def _infer(client: APIClient, project_id: str, model_id: str, system: str, user: str) -> str:
    model = ModelInference(
        model_id=model_id,
        api_client=client,
        project_id=project_id,
        params={
            GenParams.MAX_NEW_TOKENS: 800,
            GenParams.TEMPERATURE: 0.2,
        },
    )
    prompt = f"{system}\n\nInput:\n{user}\n\nOutput:"
    result = model.generate_text(prompt=prompt)
    return result.strip()


def generate_risk_summary(
    api_key: str,
    url: str,
    project_id: str,
    risk: dict[str, Any],
    recommendation: dict[str, Any],
    alert: dict[str, Any],
    model_id: str = DEFAULT_MODEL,
) -> str:
    client = _build_client(api_key, url)
    user_input = json.dumps(
        {"risk_event": risk, "recommendation": recommendation, "alert": alert},
        indent=2,
    )
    return _infer(client, project_id, model_id, SUMMARY_SYSTEM_PROMPT, user_input)


def generate_supplier_email(
    api_key: str,
    url: str,
    project_id: str,
    risk: dict[str, Any],
    recommendation: dict[str, Any],
    model_id: str = DEFAULT_MODEL,
) -> str:
    client = _build_client(api_key, url)
    user_input = json.dumps({"risk_event": risk, "recommendation": recommendation}, indent=2)
    return _infer(client, project_id, model_id, EMAIL_SYSTEM_PROMPT, user_input)
```

### Changes to `code/scrc/settings.py`

Add `watsonx_api_key` and `watsonx_project_id` fields to `AppSettings`:

```python
@dataclass(frozen=True)
class AppSettings:
    kafka: KafkaSettings
    schema_registry: SchemaRegistrySettings
    slack_webhook_url: str | None
    opensearch_url: str | None
    watsonx_url: str | None
    watsonx_api_key: str | None      # add this line
    watsonx_project_id: str | None   # add this line
```

In `load_settings()`, add the two new fields:

```python
return AppSettings(
    ...
    watsonx_api_key=os.getenv("WATSONX_API_KEY") or None,
    watsonx_project_id=os.getenv("WATSONX_PROJECT_ID") or None,
)
```

### Changes to `code/scrc/risk_engine.py`

In `RiskPublisher.__init__`, add watsonx settings:

```python
class RiskPublisher:
    def __init__(
        self,
        producer: Any | None,
        slack_webhook_url: str | None,
        watsonx_api_key: str | None = None,
        watsonx_url: str | None = None,
        watsonx_project_id: str | None = None,
    ) -> None:
        self.producer = producer
        self.slack_webhook_url = slack_webhook_url
        self.watsonx_api_key = watsonx_api_key
        self.watsonx_url = watsonx_url
        self.watsonx_project_id = watsonx_project_id
```

In `RiskPublisher.publish()`, add the watsonx.ai call block after the Slack block:

```python
        if (
            self.watsonx_api_key
            and self.watsonx_url
            and self.watsonx_project_id
            and alert.get("severity") == "CRITICAL"
        ):
            from .watsonx_client import generate_risk_summary, generate_supplier_email
            summary = generate_risk_summary(
                self.watsonx_api_key, self.watsonx_url, self.watsonx_project_id,
                risk, recommendation, alert,
            )
            email = generate_supplier_email(
                self.watsonx_api_key, self.watsonx_url, self.watsonx_project_id,
                risk, recommendation,
            )
            console.print(Panel(summary, title="watsonx.ai — Executive Summary", expand=False))
            console.print(Panel(email, title="watsonx.ai — Supplier Escalation Email", expand=False))
```

In `main()`, pass the watsonx settings to `RiskPublisher`:

```python
    publisher = RiskPublisher(
        producer=producer,
        slack_webhook_url=settings.slack_webhook_url,
        watsonx_api_key=settings.watsonx_api_key,
        watsonx_url=settings.watsonx_url,
        watsonx_project_id=settings.watsonx_project_id,
    )
```

---

## 7. New `.env` variables

Add to `.env` and `.env.example`:

```dotenv
# IBM watsonx.ai — live API integration (SPEC-01)
WATSONX_API_KEY=your-ibm-cloud-api-key
WATSONX_PROJECT_ID=your-watsonx-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

`WATSONX_URL` is region-specific. Find it in the watsonx.ai console under your service instance details.

---

## 8. Verification

1. Run the risk engine in dry-run mode:

   ```bash
   python -m scrc.risk_engine --dry-run --scenario supplier_delay --count 10
   ```

2. When the terminal prints a **Control Tower Alert** panel with `"severity": "CRITICAL"`, two additional panels should immediately follow: `watsonx.ai — Executive Summary` and `watsonx.ai — Supplier Escalation Email`.

3. If no CRITICAL events appear, increase the count or switch to the `inventory_drop` scenario which reaches CRITICAL sooner:

   ```bash
   python -m scrc.risk_engine --dry-run --scenario inventory_drop --count 6
   ```

4. To confirm the API key and project ID are correct independently:

   ```python
   from code.scrc.watsonx_client import generate_risk_summary
   import json, pathlib
   sample = json.loads(pathlib.Path("docs/assets/sample_risk_event.json").read_text())
   print(generate_risk_summary("YOUR_KEY", "YOUR_URL", "YOUR_PROJECT", sample, {}, {}))
   ```
