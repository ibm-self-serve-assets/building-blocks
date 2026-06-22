# SPEC-02: OpenSearch Operational Dashboard

Back to [specs index](README.md) | [main README](../../README.md)

---

## 1. Purpose

The risk engine publishes scored events to three output Kafka topics. This spec adds a dedicated consumer that reads all three topics and writes every event into OpenSearch, enabling:

- A live operational risk dashboard in OpenSearch Dashboards / Kibana.
- Full-text search across risk root causes and recommended actions.
- Time-series visualisations of risk score trends by component, supplier, and risk band.
- Alerting rules in OpenSearch that notify operations teams when CRITICAL events appear.

**Architecture layer extended:** Layer 5 — Downstream applications and integrations.

**New file:** `code/scrc/opensearch_consumer.py`

---

## 2. Input

| Property | Value |
|----------|-------|
| Topics consumed | `supply_chain_risk_scores`, `supply_chain_recommendations`, `control_tower_alerts` |
| Consumer group | `scrc-opensearch-consumer` |
| Message format | JSON, deserialised by `kafka_utils.json_deserializer` |
| Index pattern | `supply-chain-risk-scores-YYYY-MM`, `supply-chain-recommendations-YYYY-MM`, `control-tower-alerts-YYYY-MM` |
| Index template | [`docs/assets/opensearch-index-template.json`](../assets/opensearch-index-template.json) |

---

## 3. Output

| Output | Description |
|--------|-------------|
| OpenSearch documents | One document per Kafka message, written to a date-partitioned index |
| Index | `supply-chain-risk-scores-YYYY-MM` for risk scores, `supply-chain-recommendations-YYYY-MM` for recommendations, `control-tower-alerts-YYYY-MM` for alerts |

---

## 4. Prerequisites

| Requirement | Details |
|-------------|---------|
| OpenSearch or IBM OpenSearch | Local: `docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:2` |
| OpenSearch Dashboards | Local: `docker run -p 5601:5601 opensearchproject/opensearch-dashboards:2` |
| Python package | `opensearch-py>=2.0` — add to `pyproject.toml` |
| Kafka running | Risk engine must be producing events to the three output topics |

---

## 5. Implementation steps

### Step 1: Add the dependency

In [`pyproject.toml`](../../pyproject.toml), add `opensearch-py>=2.0` to `[project] dependencies`:

```toml
dependencies = [
    ...
    "opensearch-py>=2.0",
]
```

Reinstall:

```bash
source .venv/bin/activate
pip install -e .
```

### Step 2: Start OpenSearch locally

```bash
docker run -d --name opensearch \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:2

docker run -d --name opensearch-dashboards \
  -p 5601:5601 \
  -e "OPENSEARCH_HOSTS=http://host.docker.internal:9200" \
  -e "DISABLE_SECURITY_DASHBOARDS_PLUGIN=true" \
  opensearchproject/opensearch-dashboards:2
```

### Step 3: Apply the index template

```bash
curl -X PUT "http://localhost:9200/_index_template/supply_chain_risk" \
  -H "Content-Type: application/json" \
  -d @docs/assets/opensearch-index-template.json
```

### Step 4: Add `.env` variables

Add the variables from section 7 to `.env`.

### Step 5: Create `code/scrc/opensearch_consumer.py`

Create the new file with the complete code from section 6.

### Step 6: Run the consumer

```bash
source .venv/bin/activate
python -m scrc.opensearch_consumer
```

Leave it running alongside the risk engine and producer.

---

## 6. Complete code

### `code/scrc/opensearch_consumer.py` — new file

```python
from __future__ import annotations

"""
OpenSearch consumer — reads supply_chain_risk_scores, supply_chain_recommendations,
and control_tower_alerts from Kafka and indexes each message into OpenSearch.

Run:
    python -m scrc.opensearch_consumer
"""

import json
from datetime import datetime, timezone
from typing import Any

import typer
from opensearchpy import OpenSearch, RequestsHttpConnection
from rich.console import Console

from .kafka_utils import consume_loop, consumer_config
from .settings import TOPICS, load_settings

app = typer.Typer(help="Index risk engine output topics into OpenSearch.")
console = Console()

OUTPUT_TOPIC_KEYS = ["risk_scores", "recommendations", "alerts"]

INDEX_MAP = {
    TOPICS["risk_scores"]: "supply-chain-risk-scores",
    TOPICS["recommendations"]: "supply-chain-recommendations",
    TOPICS["alerts"]: "control-tower-alerts",
}


def _opensearch_client(url: str, username: str | None, password: str | None) -> OpenSearch:
    host = url.replace("http://", "").replace("https://", "")
    use_ssl = url.startswith("https://")
    host_part, _, port_str = host.partition(":")
    port = int(port_str) if port_str else (443 if use_ssl else 9200)

    kwargs: dict[str, Any] = {
        "hosts": [{"host": host_part, "port": port}],
        "use_ssl": use_ssl,
        "verify_certs": use_ssl,
        "connection_class": RequestsHttpConnection,
        "timeout": 10,
    }
    if username and password:
        kwargs["http_auth"] = (username, password)

    return OpenSearch(**kwargs)


def _index_name(base: str) -> str:
    month = datetime.now(tz=timezone.utc).strftime("%Y-%m")
    return f"{base}-{month}"


def _index_event(client: OpenSearch, topic: str, doc_id: str | None, event: dict[str, Any]) -> None:
    base = INDEX_MAP.get(topic)
    if base is None:
        return
    index = _index_name(base)
    client.index(index=index, id=doc_id, body=event)
    console.print(f"[green]Indexed[/green] {index} id={doc_id} score={event.get('risk_score', event.get('severity', ''))}")


@app.command()
def main() -> None:
    settings = load_settings()

    if not settings.kafka.is_configured:
        console.print("[red]ERROR: Kafka credentials missing. Check .env.[/red]")
        raise typer.Exit(1)

    opensearch_url = settings.opensearch_url or "http://localhost:9200"
    username = __import__("os").getenv("OPENSEARCH_USERNAME") or None
    password = __import__("os").getenv("OPENSEARCH_PASSWORD") or None

    client = _opensearch_client(opensearch_url, username, password)

    try:
        info = client.info()
        console.print(f"Connected to OpenSearch: {info['version']['number']} at {opensearch_url}")
    except Exception as exc:
        console.print(f"[red]ERROR: Cannot connect to OpenSearch at {opensearch_url}: {exc}[/red]")
        raise typer.Exit(1) from exc

    from confluent_kafka import Consumer
    consumer = Consumer(consumer_config(settings.kafka, group_id="scrc-opensearch-consumer"))
    topics = [TOPICS[key] for key in OUTPUT_TOPIC_KEYS]
    console.print(f"Subscribing to: {', '.join(topics)}")

    consume_loop(
        consumer,
        topics,
        lambda topic, key, event: _index_event(client, topic, key, event),
    )


if __name__ == "__main__":
    app()
```

---

## 7. New `.env` variables

Add to `.env` and `.env.example`:

```dotenv
# OpenSearch — operational risk dashboard (SPEC-02)
OPENSEARCH_URL=http://localhost:9200
OPENSEARCH_USERNAME=
OPENSEARCH_PASSWORD=
```

For IBM OpenSearch (managed service), set `OPENSEARCH_URL` to the service endpoint and populate username and password from the service credentials.

---

## 8. Verification

1. Start the risk engine and producer in separate terminals:

   ```bash
   source .venv/bin/activate
   python -m scrc.risk_engine
   ```

   ```bash
   source .venv/bin/activate
   python -m scrc.producer --scenario supplier_delay --count 20
   ```

2. Start the OpenSearch consumer:

   ```bash
   python -m scrc.opensearch_consumer
   ```

3. Confirm documents are being written:

   ```bash
   curl -s "http://localhost:9200/supply-chain-risk-scores-*/_count" | python -m json.tool
   ```

   The `count` field should increase with each risk score event.

4. Query for CRITICAL events:

   ```bash
   curl -s -X GET "http://localhost:9200/supply-chain-risk-scores-*/_search" \
     -H "Content-Type: application/json" \
     -d '{"query": {"term": {"risk_band": "CRITICAL"}}}' | python -m json.tool
   ```

5. Open OpenSearch Dashboards at [http://localhost:5601](http://localhost:5601), create an index pattern `supply-chain-risk-scores-*`, and use the Discover view to browse risk events.

### Creating a dashboard

In OpenSearch Dashboards:

1. Go to **Management → Index Patterns → Create index pattern** → `supply-chain-risk-scores-*`, time field `event_time`.
2. Go to **Visualize → Create visualization**:
   - **Metric**: count of CRITICAL events using a filter on `risk_band: CRITICAL`.
   - **Line chart**: average `risk_score` over time, split by `component_id`.
   - **Data table**: top 10 records sorted by `risk_score` descending.
3. Add all three visualisations to a new **Dashboard** named `Supply Chain Risk Control Tower`.
