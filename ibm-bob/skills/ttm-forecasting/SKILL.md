---
name: ttm-forecasting
description: IBM Granite TTM time-series forecasting — predicts future values for cold-chain temperatures, demand, energy, stock prices, IoT sensors, or any numeric time series. Routes to the correct inference path (watsonx.ai API, local HuggingFace, or mock), generates service code, scaffolds a forecast dashboard, and supports concurrent fleet forecasting.
---

# TTM Time-Series Forecasting — Master Skill

## Overview

This skill provides 96-step-ahead time-series forecasting using IBM Granite TTM (Tiny Time Mixer). It is split into focused sub-skills — load only the one relevant to your task.

| Sub-skill | File | When to use |
|---|---|---|
| **TTM Inference** | `ttm-inference/SKILL.md` | Generating forecast service code, selecting inference path, `.env` setup, credentials, troubleshooting |
| **TTM Dashboard** | `ttm-dashboard/SKILL.md` | Scaffolding `dashboard.html`, wiring to live API, visualising forecast output |
| **TTM Fleet** | `ttm-fleet/SKILL.md` | Concurrent multi-truck forecasting, cargo normalisation, OpenScale governance logging |

---

## Routing Instructions

When the user's request matches one of the following, **read the corresponding sub-skill file before responding**:

- Inference / service code / `.env` / credentials / API path / troubleshooting errors → read `ttm-inference/SKILL.md`
- Dashboard / visualise / chart / plot / forecast UI / `dashboard.html` → read `ttm-dashboard/SKILL.md`
- Fleet / multi-truck / concurrent / cargo / governance / OpenScale → read `ttm-fleet/SKILL.md`

If the request spans multiple areas, read all relevant sub-skill files.

---

## Project Folder Convention

**Always create a named project subfolder** before writing any files. Never drop files into the workspace root.

```
<project_name>/
├── ttm_model.py
├── forecasting_service.py
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

Use a descriptive name derived from the use case (e.g. `stock_forecast`, `cold_chain`, `energy_monitor`). If adding TTM to an **existing** project, place files in the most logical existing subfolder.

---

## Input / Output Summary

**Minimum input:** 512 historical data points as `[{"timestamp": "...", "value": ...}]`

**Output:**
```json
{
  "predictions": [{"timestamp": "...", "value": 2.5}, "...96 steps"],
  "model": "ibm/granite-ttm-512-96-r2",
  "inference_path": "native_api | local_pipeline | mock",
  "risk_assessment": {"risk_score": 45, "action": "MONITOR"},
  "metadata": {"inference_time_ms": 1450}
}
```

---

## Inference Paths (quick reference)

| Path | Trigger | Best for |
|---|---|---|
| **1 — watsonx.ai Native API** | `TTM_MODEL_ID` set in `.env` | Production — no model download |
| **2 — Local HuggingFace** | `USE_TTM_MODEL=True`, `TTM_MODEL_ID` empty | macOS dev / air-gapped |
| **3 — Mock / Statistical** | Neither of the above | Local dev / CI only |

→ Full path details, code templates, and troubleshooting in `ttm-inference/SKILL.md`

---

## Known Issues & Corrections (validated in production)

These were discovered during real watsonx.ai API usage — always apply them:

| # | Issue | Correct behaviour |
|---|---|---|
| 1 | **Wrong endpoint** — skill originally referenced `/ml/v1/text/chat` | TTM uses `/ml/v1/time_series/forecast?version=2025-02-10` |
| 2 | **`space_id` only** — skill assumed only `space_id` is valid | IBM API accepts either `space_id` (deployment space) or `project_id` (Watson Studio project) — never both |
| 3 | **`FREQUENCY` casing** — skill said always lowercase | IBM API is format-specific: daily=`1D`, hourly=`1h`, 5-minute=`5min`. Match IBM docs exactly |
| 4 | **Stub scenario files** — 4 of 5 scenario JSONs had only 20 data points | All scenarios now contain real 512-point datasets. The TTM API enforces minimum 512 points |
| 5 | **No deployment asset needed** — skill implied deployment space requires promoting a model | Granite TTM is IBM-hosted serverless. Pass `space_id` or `project_id` directly — no asset promotion needed |

---

## Sample Scenarios

Ready-to-use test data is in `sample_data/scenarios/`:

| File | Use case |
|---|---|
| `stock_price_scenario.json` | Financial forecasting — 512 hourly prices |
| `website_traffic_scenario.json` | Capacity planning — 512 hourly visitors |
| `sales_scenario.json` | Inventory management — 512 daily sales |
| `iot_sensor_scenario.json` | Predictive maintenance — 512 sensor readings |
| `custom_template.json` | Your own data — extend to 512+ points |
