# SPEC-04: ServiceNow Procurement Workflow

Back to [specs index](README.md) | [main README](../../README.md)

---

## 1. Purpose

When the risk engine raises a CRITICAL control tower alert, a procurement manager must act immediately. Today that action is manual. This spec adds a consumer that reads the `control_tower_alerts` Kafka topic and automatically creates a **ServiceNow Incident** (or a custom Procurement Escalation record) for every CRITICAL event, pre-populated with component ID, supplier ID, risk score, root cause, and recommended action.

The result: the moment Kafka emits a CRITICAL alert, a ServiceNow ticket is open and assigned to the procurement team — with no human intervention.

**Architecture layer extended:** Layer 5 — Downstream applications and integrations.

**New file:** `code/scrc/servicenow_consumer.py`

---

## 2. Input

| Property | Value |
|----------|-------|
| Topic consumed | `control_tower_alerts` |
| Consumer group | `scrc-servicenow-consumer` |
| Filter | `alert["severity"] == "CRITICAL"` — LOW and MEDIUM alerts are skipped |
| Alert schema | `alert_id`, `risk_id`, `severity`, `title`, `message`, `recommended_action`, `event_time` |

---

## 3. Output

| Output | Description |
|--------|-------------|
| ServiceNow Incident | Created via Table API `POST /api/now/table/incident` |
| Incident fields | Short description, description, urgency, impact, category, assignment group, work notes |

---

## 4. Prerequisites

| Requirement | Details |
|-------------|---------|
| ServiceNow instance | Developer instance (free): [https://developer.servicenow.com](https://developer.servicenow.com) → Start Building |
| ServiceNow user | A user with `itil` role, or a dedicated integration user |
| Basic auth or OAuth | This spec uses basic auth; see notes in step 1 for OAuth option |
| Assignment group | Create or note the name of the procurement group in your instance (e.g. `Procurement`) |
| Python package | `requests` — already a dependency |

---

## 5. Implementation steps

### Step 1: Obtain ServiceNow credentials

For a developer instance:

1. Log in at `https://YOUR_INSTANCE.service-now.com`.
2. Create an integration user: **User Management → Users → New**. Give them the `itil` role.
3. Note the username and password.

For production, use OAuth 2.0 with a dedicated OAuth app. Replace basic auth in `code/scrc/servicenow_consumer.py` with a token exchange call.

### Step 2: Find or create the assignment group

1. In ServiceNow, navigate to **User Administration → Groups**.
2. Find or create a group named `Procurement` (or your preferred name).
3. Note the exact group name — it is passed as `assignment_group` in the API call.

### Step 3: Add `.env` variables

Add all variables from section 7 to `.env`.

### Step 4: Create `code/scrc/servicenow_consumer.py`

Create the file with the complete code from section 6.

### Step 5: Run the consumer

```bash
source .venv/bin/activate
python -m scrc.servicenow_consumer
```

### Step 6: Produce a CRITICAL event and verify the ticket

```bash
python -m scrc.producer --scenario inventory_drop --count 10
```

Then check the ServiceNow Incidents list for a new record.

---

## 6. Complete code

### `code/scrc/servicenow_consumer.py` — new file

```python
from __future__ import annotations

"""
ServiceNow consumer — reads control_tower_alerts from Kafka and creates
a ServiceNow Incident for every CRITICAL severity event.

Run:
    python -m scrc.servicenow_consumer
"""

import os
from typing import Any

import requests
import typer
from rich.console import Console

from .kafka_utils import consume_loop, consumer_config
from .settings import TOPICS, load_settings

app = typer.Typer(help="Create ServiceNow incidents from CRITICAL control tower alerts.")
console = Console()

# ServiceNow urgency and impact values:
#   1 = High, 2 = Medium, 3 = Low
CRITICAL_URGENCY = 1
CRITICAL_IMPACT = 1


def _create_incident(
    instance_url: str,
    username: str,
    password: str,
    alert: dict[str, Any],
    assignment_group: str,
) -> dict[str, Any]:
    """Create a ServiceNow Incident via the Table API.

    Returns the created record as a dict.
    """
    url = f"{instance_url.rstrip('/')}/api/now/table/incident"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    description_lines = [
        f"Alert ID     : {alert.get('alert_id', '')}",
        f"Risk ID      : {alert.get('risk_id', '')}",
        f"Severity     : {alert.get('severity', '')}",
        f"Message      : {alert.get('message', '')}",
        f"Recommended  : {alert.get('recommended_action', '')}",
        f"Event time   : {alert.get('event_time', '')}",
    ]

    payload = {
        "short_description": alert.get("title", "Supply Chain CRITICAL Risk Alert"),
        "description": "\n".join(description_lines),
        "urgency": str(CRITICAL_URGENCY),
        "impact": str(CRITICAL_IMPACT),
        "category": "procurement",
        "subcategory": "supply_chain_risk",
        "assignment_group": assignment_group,
        "work_notes": (
            f"Automatically created by Supply Chain Risk Control Tower.\n"
            f"Recommended action: {alert.get('recommended_action', '')}"
        ),
    }

    response = requests.post(url, json=payload, headers=headers, auth=(username, password), timeout=15)
    response.raise_for_status()
    return response.json().get("result", {})


def _handle_alert(
    topic: str,
    key: str | None,
    event: dict[str, Any],
    instance_url: str,
    username: str,
    password: str,
    assignment_group: str,
) -> None:
    if event.get("severity") != "CRITICAL":
        console.print(f"[dim]Skipped {event.get('severity', 'UNKNOWN')} alert {event.get('alert_id', '')}[/dim]")
        return

    console.print(f"[yellow]CRITICAL alert received — creating ServiceNow incident...[/yellow] {event.get('alert_id', '')}")
    try:
        result = _create_incident(instance_url, username, password, event, assignment_group)
        sys_id = result.get("sys_id", "unknown")
        number = result.get("number", "unknown")
        console.print(f"[green]Incident created:[/green] {number} (sys_id={sys_id})")
    except requests.HTTPError as exc:
        console.print(f"[red]ERROR creating incident: {exc}[/red]")
        console.print(f"[red]Response: {exc.response.text if exc.response else 'no response'}[/red]")


@app.command()
def main() -> None:
    settings = load_settings()

    if not settings.kafka.is_configured:
        console.print("[red]ERROR: Kafka credentials missing. Check .env.[/red]")
        raise typer.Exit(1)

    instance_url = os.getenv("SERVICENOW_INSTANCE_URL", "")
    username = os.getenv("SERVICENOW_USERNAME", "")
    password = os.getenv("SERVICENOW_PASSWORD", "")
    assignment_group = os.getenv("SERVICENOW_ASSIGNMENT_GROUP", "Procurement")

    if not all([instance_url, username, password]):
        console.print("[red]ERROR: SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD must be set in .env.[/red]")
        raise typer.Exit(1)

    console.print(f"ServiceNow instance : {instance_url}")
    console.print(f"Assignment group    : {assignment_group}")

    from confluent_kafka import Consumer
    consumer = Consumer(consumer_config(settings.kafka, group_id="scrc-servicenow-consumer"))
    topics = [TOPICS["alerts"]]
    console.print(f"Subscribing to: {', '.join(topics)}")

    consume_loop(
        consumer,
        topics,
        lambda topic, key, event: _handle_alert(
            topic, key, event, instance_url, username, password, assignment_group
        ),
    )


if __name__ == "__main__":
    app()
```

---

## 7. New `.env` variables

Add to `.env` and `.env.example`:

```dotenv
# ServiceNow — procurement incident automation (SPEC-04)
SERVICENOW_INSTANCE_URL=https://YOUR_INSTANCE.service-now.com
SERVICENOW_USERNAME=integration-user
SERVICENOW_PASSWORD=replace-me
SERVICENOW_ASSIGNMENT_GROUP=Procurement
```

---

## 8. Verification

1. Start the ServiceNow consumer:

   ```bash
   source .venv/bin/activate
   python -m scrc.servicenow_consumer
   ```

2. Produce events that generate CRITICAL alerts:

   ```bash
   python -m scrc.producer --scenario inventory_drop --count 10
   ```

3. The consumer terminal should print:

   ```
   CRITICAL alert received — creating ServiceNow incident...  ALERT-xxxx
   Incident created: INC0010001 (sys_id=abc123...)
   ```

4. In ServiceNow, navigate to **Incidents → All Open Incidents**. The new incident should appear with:
   - Short description matching the alert title
   - Urgency and Impact both set to 1 (High)
   - Category `procurement`
   - Assignment group `Procurement`
   - Work notes containing the recommended action

5. To test without running the full Kafka stack, call `_create_incident` directly:

   ```python
   import os, json, pathlib
   from code.scrc.servicenow_consumer import _create_incident
   alert = {
       "alert_id": "TEST-001", "risk_id": "RISK-001", "severity": "CRITICAL",
       "title": "Test incident", "message": "Integration test from SPEC-04.",
       "recommended_action": "Verify API connectivity.", "event_time": "2026-01-01T00:00:00Z",
   }
   result = _create_incident(
       os.getenv("SERVICENOW_INSTANCE_URL"),
       os.getenv("SERVICENOW_USERNAME"),
       os.getenv("SERVICENOW_PASSWORD"),
       alert, "Procurement",
   )
   print(result["number"], result["sys_id"])
   ```
