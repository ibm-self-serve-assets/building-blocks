# Real-Time Guardrails Bob Skills

Bob skill for adding **production-grade runtime safety and quality guardrails** to AI/RAG agents using IBM's `real-time-guardrails` package (backed by **watsonx.governance**).

## Overview

The `real-time-guardrails` skill turns IBM Bob into a guardrails-aware assistant. When you ask Bob to add guardrails to an LLM app, it drives you end-to-end — from IBM Cloud setup, through designing the 4-choke-point pattern (input → retrieval → generation → output), implementing enforcement, tuning thresholds against a sample workload, to deploying with compliance audit logging and dashboards. Enforcement follows a three-state **Pass / Flag / Block** action model.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `real-time-guardrails` | [`real-time-guardrails.zip`](real-time-guardrails.zip) | Adding runtime safety/quality enforcement to an AI, RAG, or watsonx Orchestrate agent before production |

---

### `real-time-guardrails`

An end-to-end, five-phase workflow:

1. **Setup** — IBM Cloud provisioning, credentials wired safely (no key leaks)
2. **Design** — 4-choke-point pattern, metric set per choke point, threshold policy, fallback messages
3. **Implement** — explicit wiring or auto-trigger (middleware / decorator / framework callback), with reference implementations for FastAPI, Flask, LangChain, and watsonx Orchestrate
4. **Test & tune** — sample-workload tuning and `jq` queries against the audit log
5. **Deploy & observe** — library / REST / MCP modes, Splunk/ELK audit sinks, compliance dashboards

Covers a **28-metric catalog** across safety, RAG generation/retrieval, output quality, topic, pattern, and tool-call categories, plus **custom LLM-as-judge** authoring and a 5-layer threshold-override model for multi-tenant policies.

---

## Installation

### Step 1 — Install the skill

The zip is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip real-time-guardrails.zip
```

This creates:

```
.bob/skills/real-time-guardrails/SKILL.md
```

(along with the skill's `reference/`, `examples/`, `assets/`, and `setup.sh`).

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `real-time-guardrails`. Bob will use it as active context for every prompt in this workspace. The bundled `setup.sh` provisions a dedicated venv, clones the package, and runs the dependency pre-flight when you're ready to integrate.

### Step 3 — Verify

Ask Bob: *"What guardrail metrics and choke points do you know about?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"I need to add safety guardrails to my RAG agent before going to production"*
- *"My LangChain chatbot needs PII detection and HAP screening on outputs"*
- *"How do I add guardrails to a watsonx Orchestrate agent that uses 3 tools?"*
- *"Wire a chat widget to a backend proxy so I don't leak my API key to the browser"*
- *"Author a custom LLM-as-judge metric for answer completeness"*

Bob loads this skill and drives the workflow.

---

## What Bob Can Help You Build

1. **Choke-point enforcement**: input, retrieval, generation, and output guardrails with Pass/Flag/Block
2. **Framework integration**: FastAPI/Flask middleware, LangChain callbacks, watsonx Orchestrate tool wrappers
3. **Metric selection & tuning**: picking from the 28-metric catalog and tuning thresholds per data shape
4. **Custom guardrails**: domain-specific LLM-as-judge metrics
5. **Compliance & observability**: JSONL audit trails, Splunk/ELK sinks, and compliance dashboards
6. **Safe frontends**: chat widgets backed by a server-side guardrails proxy

---

## Prerequisites

Before using this skill, ensure you have:

- **IBM Cloud** account with a **watsonx.governance** subscription (always required)
- (Optional) **watsonx.ai** project with Watson Machine Learning associated — only for the 3 LLM-as-judge metrics
- **Python 3.11–3.13** (3.14 not yet supported by the IBM SDK chain)
- Outbound HTTPS to `*.ml.cloud.ibm.com` and your watsonx.governance regional endpoint (air-gapped not supported)

See [`.bob/skills/real-time-guardrails/USAGE-GUIDE.md`](real-time-guardrails.zip) inside the zip for full installation and first-run instructions.

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **4 choke points** | Input → retrieval → generation → output enforcement |
| **28-metric catalog** | Safety, RAG, quality, topic, pattern, and tool-call categories |
| **Pass / Flag / Block** | Three-state action model with fallback messages + audit logging |
| **Three interfaces** | Library (in-process), REST server, and MCP server |
| **Framework integration** | FastAPI, Flask, LangChain, watsonx Orchestrate |
| **Custom LLM-as-judge** | Author domain-specific guardrail metrics |
| **5-layer thresholds** | per-call > constructor > YAML > env var > default (multi-tenant) |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/real-time-guardrails/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure the Skills button is enabled in your current mode

**LLM-as-judge metrics unavailable:**
1. Confirm a watsonx.ai project with WML is associated
2. Verify the optional `WXG_PROJECT_ID` credential is set

## Related

- [`../bob-modes/`](../bob-modes/) — Real-Time Guardrails Bob Mode
- [`../assets/`](../assets/) — Production SDK and numbered tutorial scripts
- [`../README.md`](../README.md) — Real-Time Guardrails building block overview
