# Extension Specifications

This folder contains one spec-driven development document per future integration shown in the architecture diagram. Each spec is self-contained — a developer can pick up any one of them and implement it without needing to read the rest of the codebase first.

Back to [main README](../../README.md).

---

## What is already built

The core application is complete and runnable without any of these integrations:

| Component | Location |
|-----------|----------|
| Python risk engine — consumes 7 input topics, scores risk, publishes 3 output topics | `code/scrc/` |
| IBM Carbon Design browser dashboard — simulation and live Kafka modes | `code/ui/` |
| JSON Schema data contracts for all 10 Kafka topics | `code/schemas/` |
| Schema Registry registration script | `code/scrc/register_schemas.py` |
| Flink SQL reference implementation of the risk engine | `code/flink-sql/` |
| Slack alerts for HIGH and CRITICAL severity events | `code/scrc/slack_alerts.py` |
| watsonx.ai prompt templates for manual use in Prompt Lab | `docs/agents/` |
| Confluent Cloud Terraform infrastructure | `code/terraform/` |

---

## What these specs cover

Each spec adds one integration to the existing application. They are ordered from simplest to most complex.

| Spec | Integration | Effort |
|------|-------------|--------|
| [SPEC-01](SPEC-01-watsonx-ai-live.md) | watsonx.ai live API — real-time executive summaries and supplier emails on CRITICAL events | Low |
| [SPEC-02](SPEC-02-opensearch-consumer.md) | OpenSearch — operational risk dashboard that indexes all three output topics | Low |
| [SPEC-03](SPEC-03-teams-alerts.md) | Microsoft Teams — webhook alerts for HIGH and CRITICAL severity events | Low |
| [SPEC-04](SPEC-04-servicenow-itsm.md) | ServiceNow — automated procurement incident workflow from `control_tower_alerts` | Medium |
| [SPEC-05](SPEC-05-ibm-cos-data-lake.md) | IBM Cloud Object Storage — raw event data lake via Confluent S3-compatible sink connector | Medium |
| [SPEC-06](SPEC-06-watsonxdata-tableflow.md) | watsonx.data / Tableflow — governed Apache Iceberg analytics tables from output topics | Medium |
| [SPEC-07](SPEC-07-ibm-maximo.md) | IBM Maximo — maintenance and logistics work order automation from CRITICAL alerts | High |

---

## Reference assets used by these specs

| File | Used by |
|------|---------|
| [`docs/assets/sample_risk_event.json`](../assets/sample_risk_event.json) | All specs — use to test integration payloads without running the full stack |
| [`docs/assets/opensearch-index-template.json`](../assets/opensearch-index-template.json) | SPEC-02 — apply before starting the OpenSearch consumer |

---

## Structure of every spec

Every spec follows the same eight-section structure:

1. **Purpose** — what business problem this integration solves and which layer of the architecture it extends
2. **Input** — the exact Kafka topic name, consumer group, and message schema it reads from
3. **Output** — what the integration produces (API call, index document, webhook payload, connector config, file)
4. **Prerequisites** — all accounts, credentials, packages, and tools required before writing a line of code
5. **Implementation steps** — numbered, copy-pasteable steps from zero to working integration
6. **Complete code** — full source for every new file to create and every existing file to modify
7. **New `.env` variables** — exact variable names and example values to add to `.env` and `.env.example`
8. **Verification** — step-by-step instructions to confirm the integration works end to end

---

## How to use a spec

1. **Read Purpose** — confirm this spec solves the problem you are trying to solve.
2. **Complete Prerequisites** — do not skip this. Missing credentials mid-implementation is the most common blocker.
3. **Follow Implementation steps in order** — each step is independently testable.
4. **Use Complete code as the source of truth** — the code is written to integrate with the existing `code/scrc/` modules and Kafka topic schemas. Do not deviate from the file structure.
5. **Add `.env` variables** — add every variable listed in the spec to your `.env` before running.
6. **Run Verification** — confirm each check passes before moving on.

---

## Combining specs

Specs are independent but some combinations make sense in a single demo:

- **SPEC-01 + SPEC-03**: watsonx.ai generates the summary, Teams posts it as a card — gives the audience a complete AI-to-notification loop.
- **SPEC-02 + SPEC-05**: OpenSearch provides the live operational dashboard, IBM COS holds the historical data lake — covers both hot and cold analytics paths.
- **SPEC-04 + SPEC-07**: ServiceNow handles procurement escalation, Maximo handles the physical asset work order — covers the full enterprise response workflow.
