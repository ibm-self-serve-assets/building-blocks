# SPEC-07: IBM Maximo Work Order Automation

Back to [specs index](README.md) | [main README](../../README.md)

---

## 1. Purpose

When the risk engine raises a CRITICAL control tower alert — typically because a component shipment is severely delayed and inventory is critically low — a physical response is often required: expediting a logistics pick-up, scheduling an emergency maintenance inspection, or reallocating parts from another production line. These actions are managed in IBM Maximo.

This spec adds a consumer that reads the `control_tower_alerts` Kafka topic and automatically creates a **Maximo Work Order** for every CRITICAL alert, pre-populated with the affected component, supplier, risk score, and recommended action. The work order is assigned to the logistics or maintenance team and set to priority 1 (Emergency).

**Architecture layer extended:** Layer 5 — Downstream applications and integrations.

**New file:** `code/scrc/maximo_consumer.py`

---

## 2. Input

| Property | Value |
|----------|-------|
| Topic consumed | `control_tower_alerts` |
| Consumer group | `scrc-maximo-consumer` |
| Filter | `alert["severity"] == "CRITICAL"` — HIGH and lower are skipped |
| Alert schema | `alert_id`, `risk_id`, `severity`, `title`, `message`, `recommended_action`, `event_time` |
| Risk score (for WO description) | Joined from `supply_chain_risk_scores` using `risk_id` if available |

---

## 3. Output

| Output | Description |
|--------|-------------|
| Maximo Work Order | Created via Maximo REST API `POST /maximo/oslc/os/mxwo` |
| Work Order fields | `wonum` (auto), `description`, `longdescription`, `wopriority` (1 = Emergency), `siteid`, `orgid`, `status` (WAPPR — Waiting for Approval) |

---

## 4. Prerequisites

| Requirement | Details |
|-------------|---------|
| IBM Maximo Application Suite | MAS 8.x or Maximo 7.6.1+ with REST API enabled |
| Maximo OSLC REST API | Enabled by default in MAS; verify at `https://YOUR_HOST/maximo/oslc/` |
| Maximo user | Integration user with `MXAPIWO` object structure access and `PLUSAPPAUTHOR` security group, or equivalent work order create permission |
| Site ID and Org ID | Find in Maximo: **Administration → Organizations** — note `SITEID` and `ORGID` |
| Python package | `requests` — already a dependency |

### Maximo authentication options

Maximo supports two authentication modes:

- **Basic auth** (used in this spec): `username:password` in the `Authorization` header. Simple but requires HTTPS in production.
- **API key** (recommended for production): Create a Maximo API key under **User → API Keys** and pass it as the `apikey` header instead of basic auth.

---

## 5. Implementation steps

### Step 1: Verify Maximo REST API access

```bash
curl -u YOUR_USER:YOUR_PASSWORD \
  "https://YOUR_MAXIMO_HOST/maximo/oslc/os/mxwo?oslc.pageSize=1" \
  -H "Accept: application/json"
```

A 200 response with a JSON body confirms the API is reachable. A 401 means credentials are wrong. A 403 means the user lacks work order read permission.

### Step 2: Note the Site ID and Org ID

In Maximo, navigate to **Administration → Organizations** and note the `SITEID` and `ORGID` for the site that will own the work orders.

### Step 3: Add `.env` variables

Add all variables from section 7 to `.env`.

### Step 4: Create `code/scrc/maximo_consumer.py`

Create the file with the complete code from section 6.

### Step 5: Run the consumer

```bash
source .venv/bin/activate
python -m scrc.maximo_consumer
```

### Step 6: Produce a CRITICAL event and verify the work order

```bash
python -m scrc.producer --scenario inventory_drop --count 10
```

Then check Maximo: **Work Orders → Work Order Tracking** → filter by description containing `Supply Chain`.

---

## 6. Complete code

### `code/scrc/maximo_consumer.py` — new file

```python
from __future__ import annotations

"""
IBM Maximo consumer — reads control_tower_alerts from Kafka and creates
a Maximo Work Order for every CRITICAL severity event.

Authentication: basic auth by default; set MAXIMO_API_KEY to use API key auth instead.

Run:
    python -m scrc.maximo_consumer
"""

import os
from datetime import datetime, timezone
from typing import Any

import requests
import typer
from rich.console import Console

from .kafka_utils import consume_loop, consumer_config
from .settings import TOPICS, load_settings

app = typer.Typer(help="Create Maximo work orders from CRITICAL control tower alerts.")
console = Console()

# Maximo work order priority: 1 = Emergency, 2 = High, 3 = Medium, 4 = Low
CRITICAL_PRIORITY = 1
INITIAL_STATUS = "WAPPR"  # Waiting for Approval — change to "APPR" to skip approval


def _build_headers(api_key: str | None, username: str | None, password: str | None) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-method-override": "BULK",
    }
    if api_key:
        headers["apikey"] = api_key
    elif username and password:
        import base64
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    return headers


def _create_work_order(
    base_url: str,
    headers: dict[str, str],
    alert: dict[str, Any],
    site_id: str,
    org_id: str,
) -> dict[str, Any]:
    """Create a Maximo Work Order via the OSLC REST API.

    Returns the created work order record.
    """
    url = f"{base_url.rstrip('/')}/maximo/oslc/os/mxwo"

    short_desc = f"Supply Chain CRITICAL Risk — {alert.get('title', 'Alert')}"[:100]

    long_desc_lines = [
        f"Automatically created by Supply Chain Risk Control Tower.",
        f"",
        f"Alert ID         : {alert.get('alert_id', '')}",
        f"Risk ID          : {alert.get('risk_id', '')}",
        f"Severity         : {alert.get('severity', '')}",
        f"",
        f"Details:",
        f"{alert.get('message', '')}",
        f"",
        f"Recommended action:",
        f"{alert.get('recommended_action', '')}",
        f"",
        f"Event time       : {alert.get('event_time', '')}",
        f"Created          : {datetime.now(tz=timezone.utc).isoformat()}",
    ]

    payload = {
        "description": short_desc,
        "description_longdescription": "\n".join(long_desc_lines),
        "wopriority": CRITICAL_PRIORITY,
        "siteid": site_id,
        "orgid": org_id,
        "status": INITIAL_STATUS,
        "worktype": "CM",  # Corrective Maintenance — change to match your Maximo config
    }

    response = requests.post(url, json=payload, headers=headers, timeout=20, verify=True)
    response.raise_for_status()

    # Maximo returns 201 Created with a Location header containing the new WO URI
    location = response.headers.get("Location", "")
    wo_number = location.rstrip("/").split("/")[-1] if location else "unknown"
    return {"wonum": wo_number, "location": location}


def _handle_alert(
    topic: str,
    key: str | None,
    event: dict[str, Any],
    base_url: str,
    headers: dict[str, str],
    site_id: str,
    org_id: str,
) -> None:
    severity = event.get("severity", "")
    if severity != "CRITICAL":
        console.print(f"[dim]Skipped {severity} alert {event.get('alert_id', '')}[/dim]")
        return

    console.print(
        f"[yellow]CRITICAL alert — creating Maximo work order...[/yellow] "
        f"{event.get('alert_id', '')}"
    )

    try:
        result = _create_work_order(base_url, headers, event, site_id, org_id)
        console.print(
            f"[green]Work order created:[/green] {result['wonum']} "
            f"— {result['location']}"
        )
    except requests.HTTPError as exc:
        console.print(f"[red]ERROR creating work order: {exc}[/red]")
        if exc.response is not None:
            console.print(f"[red]Response body: {exc.response.text[:500]}[/red]")
    except requests.ConnectionError as exc:
        console.print(f"[red]Cannot connect to Maximo at {base_url}: {exc}[/red]")


@app.command()
def main() -> None:
    settings = load_settings()

    if not settings.kafka.is_configured:
        console.print("[red]ERROR: Kafka credentials missing. Check .env.[/red]")
        raise typer.Exit(1)

    base_url = os.getenv("MAXIMO_BASE_URL", "")
    api_key = os.getenv("MAXIMO_API_KEY") or None
    username = os.getenv("MAXIMO_USERNAME") or None
    password = os.getenv("MAXIMO_PASSWORD") or None
    site_id = os.getenv("MAXIMO_SITE_ID", "BEDFORD")
    org_id = os.getenv("MAXIMO_ORG_ID", "EAGLENA")

    if not base_url:
        console.print("[red]ERROR: MAXIMO_BASE_URL must be set in .env.[/red]")
        raise typer.Exit(1)

    if not api_key and not (username and password):
        console.print("[red]ERROR: Set either MAXIMO_API_KEY or both MAXIMO_USERNAME and MAXIMO_PASSWORD in .env.[/red]")
        raise typer.Exit(1)

    headers = _build_headers(api_key, username, password)

    auth_mode = "API key" if api_key else "basic auth"
    console.print(f"Maximo base URL : {base_url}")
    console.print(f"Authentication  : {auth_mode}")
    console.print(f"Site ID         : {site_id}")
    console.print(f"Org ID          : {org_id}")
    console.print(f"Initial status  : {INITIAL_STATUS}")

    from confluent_kafka import Consumer
    consumer = Consumer(consumer_config(settings.kafka, group_id="scrc-maximo-consumer"))
    topics = [TOPICS["alerts"]]
    console.print(f"Subscribing to  : {', '.join(topics)}")

    consume_loop(
        consumer,
        topics,
        lambda topic, key, event: _handle_alert(
            topic, key, event, base_url, headers, site_id, org_id
        ),
    )


if __name__ == "__main__":
    app()
```

---

## 7. New `.env` variables

Add to `.env` and `.env.example`:

```dotenv
# IBM Maximo — work order automation (SPEC-07)
MAXIMO_BASE_URL=https://YOUR_MAXIMO_HOST
# Use API key auth (recommended for production):
MAXIMO_API_KEY=
# OR use basic auth (simpler for dev instances):
MAXIMO_USERNAME=
MAXIMO_PASSWORD=
# Site and org from Administration → Organizations in Maximo
MAXIMO_SITE_ID=BEDFORD
MAXIMO_ORG_ID=EAGLENA
```

---

## 8. Verification

1. Verify the Maximo REST API is reachable from your machine:

   ```bash
   curl -u YOUR_USER:YOUR_PASSWORD \
     "https://YOUR_MAXIMO_HOST/maximo/oslc/os/mxwo?oslc.pageSize=1" \
     -H "Accept: application/json"
   ```

   Expect HTTP 200 with a JSON body. A 401 means wrong credentials; a 404 means the OSLC API path is different on your instance — check with your Maximo admin.

2. Start the consumer:

   ```bash
   source .venv/bin/activate
   python -m scrc.maximo_consumer
   ```

3. Produce CRITICAL events:

   ```bash
   python -m scrc.producer --scenario inventory_drop --count 10
   ```

4. The consumer terminal should print:

   ```
   CRITICAL alert — creating Maximo work order...  ALERT-xxxx
   Work order created: 1234 — https://YOUR_HOST/maximo/oslc/os/mxwo/1234
   ```

5. In Maximo, navigate to **Work Orders → Work Order Tracking**. Filter by `Description contains Supply Chain`. The new work order should appear with:
   - Priority: 1 (Emergency)
   - Status: WAPPR (Waiting for Approval)
   - Work Type: CM (Corrective Maintenance)
   - Long description containing the alert ID, risk ID, and recommended action.

6. To test the API call without the full Kafka stack, call `_create_work_order` directly:

   ```python
   import os
   from code.scrc.maximo_consumer import _build_headers, _create_work_order

   headers = _build_headers(
       api_key=os.getenv("MAXIMO_API_KEY"),
       username=os.getenv("MAXIMO_USERNAME"),
       password=os.getenv("MAXIMO_PASSWORD"),
   )
   alert = {
       "alert_id": "TEST-001", "risk_id": "RISK-001", "severity": "CRITICAL",
       "title": "Test work order", "message": "Integration test from SPEC-07.",
       "recommended_action": "Verify Maximo API connectivity.",
       "event_time": "2026-01-01T00:00:00Z",
   }
   result = _create_work_order(
       os.getenv("MAXIMO_BASE_URL"), headers, alert,
       os.getenv("MAXIMO_SITE_ID"), os.getenv("MAXIMO_ORG_ID"),
   )
   print(result)
   ```

### Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| HTTP 401 | Wrong credentials | Verify username/password or re-generate the API key |
| HTTP 403 | User lacks WO create permission | Add user to `PLUSAPPAUTHOR` security group or grant `MXAPIWO` object structure access |
| HTTP 404 on `/maximo/oslc/os/mxwo` | OSLC API path differs on your instance | Try `/maximo/oslc/os/mxwo` → `/maximo/oslc/os/MXWO` (uppercase) or check with Maximo admin |
| HTTP 422 | Invalid `siteid` or `orgid` | Verify the values in Maximo under **Administration → Organizations** |
| `ConnectionError` | Maximo not reachable from your machine | Check VPN, firewall rules, or use a jump host |
