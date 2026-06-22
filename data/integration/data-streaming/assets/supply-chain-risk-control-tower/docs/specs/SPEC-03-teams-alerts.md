# SPEC-03: Microsoft Teams Alerts

Back to [specs index](README.md) | [main README](../../README.md)

---

## 1. Purpose

The existing [`code/scrc/slack_alerts.py`](../../code/scrc/slack_alerts.py) sends HIGH and CRITICAL alerts to Slack. This spec adds a parallel Teams integration using the same trigger logic and the same `Alert` payload, so organisations that use Microsoft Teams instead of (or alongside) Slack receive the same real-time notifications.

Alerts are delivered as an **Adaptive Card** in a Teams channel, showing the severity, component, risk score, root cause, and recommended action in a structured, scannable format.

**Architecture layer extended:** Layer 5 — Downstream applications and integrations.

**Pattern:** Mirrors `slack_alerts.py` exactly — the risk engine calls both if both webhooks are configured.

---

## 2. Input

| Property | Value |
|----------|-------|
| Trigger | `Alert.severity in {"HIGH", "CRITICAL"}` — evaluated in `RiskPublisher.publish()` |
| Alert schema | `Alert` dataclass fields: `alert_id`, `risk_id`, `severity`, `title`, `message`, `recommended_action`, `event_time` |
| Risk score (for card) | `RiskResult.risk_score`, `RiskResult.component_id`, `RiskResult.supplier_id` |

---

## 3. Output

| Output | Description |
|--------|-------------|
| Teams Adaptive Card | Posted to the configured Teams channel via incoming webhook |
| Card fields | Severity badge, risk score, component ID, supplier ID, root cause, recommended action, timestamp |

---

## 4. Prerequisites

| Requirement | Details |
|-------------|---------|
| Microsoft Teams | Any Teams workspace |
| Incoming Webhook connector | Add to a channel: Channel settings → Connectors → Incoming Webhook → Configure → Copy URL |
| No new Python packages | Uses `requests`, which is already a dependency |

### Creating the Teams incoming webhook

1. In Teams, open the target channel.
2. Click the three-dot menu (ellipsis) next to the channel name → **Connectors**.
3. Find **Incoming Webhook** → **Configure**.
4. Give it a name (e.g. `Supply Chain Risk Tower`) and optionally upload an icon.
5. Click **Create** and copy the webhook URL.
6. Click **Done**.

The URL looks like: `https://YOUR_ORG.webhook.office.com/webhookb2/...`

---

## 5. Implementation steps

### Step 1: Add the webhook URL to `.env`

Add the variable from section 7 to `.env`.

### Step 2: Update `code/scrc/settings.py`

Add `teams_webhook_url` to `AppSettings`.

### Step 3: Create `code/scrc/teams_alerts.py`

Create the new file with the complete code from section 6.

### Step 4: Update `code/scrc/risk_engine.py`

Add the Teams call alongside the Slack call in `RiskPublisher.publish()`.

### Step 5: Test

Run a dry-run scenario that produces CRITICAL events and verify the card appears in Teams.

---

## 6. Complete code

### `code/scrc/teams_alerts.py` — new file

```python
from __future__ import annotations

"""
Microsoft Teams alert integration.
Posts an Adaptive Card to a Teams channel for HIGH and CRITICAL severity events.

Mirror of slack_alerts.py — same trigger, different delivery format.
"""

from typing import Any

import requests


def send_teams_alert(webhook_url: str, alert: dict[str, Any], risk: dict[str, Any] | None = None) -> None:
    """Post an Adaptive Card to a Teams channel via incoming webhook.

    Args:
        webhook_url: Teams incoming webhook URL.
        alert: Alert dict with severity, title, message, recommended_action, event_time.
        risk: Optional RiskResult dict for additional card fields (risk_score, component_id, supplier_id).
    """
    severity = alert.get("severity", "UNKNOWN")
    colour = "attention" if severity == "CRITICAL" else "warning"

    facts = [
        {"title": "Severity", "value": severity},
        {"title": "Alert", "value": alert.get("title", "")},
        {"title": "Recommended action", "value": alert.get("recommended_action", "")},
        {"title": "Time", "value": alert.get("event_time", "")},
    ]

    if risk:
        facts.insert(1, {"title": "Risk score", "value": str(risk.get("risk_score", ""))})
        facts.insert(2, {"title": "Component", "value": risk.get("component_id", "")})
        facts.insert(3, {"title": "Supplier", "value": risk.get("supplier_id", "")})

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"Supply Chain Risk — {severity}",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": colour,
                        },
                        {
                            "type": "TextBlock",
                            "text": alert.get("message", ""),
                            "wrap": True,
                        },
                        {
                            "type": "FactSet",
                            "facts": facts,
                        },
                    ],
                },
            }
        ],
    }

    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()
```

### Changes to `code/scrc/settings.py`

Add `teams_webhook_url` to `AppSettings`:

```python
@dataclass(frozen=True)
class AppSettings:
    kafka: KafkaSettings
    schema_registry: SchemaRegistrySettings
    slack_webhook_url: str | None
    teams_webhook_url: str | None    # add this line
    opensearch_url: str | None
    watsonx_url: str | None
```

In `load_settings()`:

```python
return AppSettings(
    ...
    teams_webhook_url=os.getenv("TEAMS_WEBHOOK_URL") or None,
    ...
)
```

### Changes to `code/scrc/risk_engine.py`

In `RiskPublisher.__init__`, add `teams_webhook_url`:

```python
class RiskPublisher:
    def __init__(
        self,
        producer: Any | None,
        slack_webhook_url: str | None,
        teams_webhook_url: str | None = None,
    ) -> None:
        self.producer = producer
        self.slack_webhook_url = slack_webhook_url
        self.teams_webhook_url = teams_webhook_url
```

In `RiskPublisher.publish()`, add after the Slack block:

```python
        if self.teams_webhook_url and alert.get("severity") in {"HIGH", "CRITICAL"}:
            from .teams_alerts import send_teams_alert
            send_teams_alert(self.teams_webhook_url, alert, risk)
```

In `main()`, pass `teams_webhook_url` to `RiskPublisher`:

```python
    publisher = RiskPublisher(
        producer=producer,
        slack_webhook_url=settings.slack_webhook_url,
        teams_webhook_url=settings.teams_webhook_url,
    )
```

---

## 7. New `.env` variables

Add to `.env` and `.env.example`:

```dotenv
# Microsoft Teams — webhook alerts (SPEC-03)
TEAMS_WEBHOOK_URL=https://YOUR_ORG.webhook.office.com/webhookb2/...
```

---

## 8. Verification

1. Run the risk engine in dry-run mode with a scenario that produces CRITICAL events:

   ```bash
   source .venv/bin/activate
   python -m scrc.risk_engine --dry-run --scenario inventory_drop --count 6
   ```

2. Open the Teams channel. Within a few seconds of the terminal printing a CRITICAL alert, a card should appear with the severity badge, risk score, component, recommended action, and timestamp.

3. To test the card payload without running the full engine, send it directly:

   ```python
   import os, json, pathlib
   from code.scrc.teams_alerts import send_teams_alert
   sample = json.loads(pathlib.Path("docs/assets/sample_risk_event.json").read_text())
   alert = {"severity": "CRITICAL", "title": "Test alert", "message": "Integration test.",
            "recommended_action": "Review immediately.", "event_time": "2026-01-01T00:00:00Z"}
   send_teams_alert(os.getenv("TEAMS_WEBHOOK_URL"), alert, sample)
   ```

4. If the card does not appear, check the webhook URL is correct and the connector has not been disabled in the Teams admin centre.
