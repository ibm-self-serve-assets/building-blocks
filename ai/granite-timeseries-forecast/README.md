# TTM Forecasting — Bob Skill

Bob skill for **IBM Granite TTM (Tiny Time Mixer) time-series forecasting** — cold-chain temperature prediction, demand forecasting, energy consumption, IoT sensor monitoring, and any 96-step ahead prediction scenario — using the IBM watsonx.ai native serverless API or a local HuggingFace pipeline.

## Overview

The `ttm-forecasting` skill turns Bob into a forecasting assistant. When activated, it:

1. **Guides you to the right inference path** — watsonx.ai native API (production, no model download) or local HuggingFace pipeline (dev / air-gapped)
2. **Generates service code** — `TTMModelWrapper`, `forecasting_service.py`, FastAPI endpoints, Dockerfile
3. **Handles governance** — OpenScale payload logging wired in as a fire-and-forget daemon thread
4. **Scaffolds `dashboard.html`** — self-contained ECharts visualisation of forecast output, on request

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `ttm-forecasting` | [`ttm-forecasting.zip`](ttm-forecasting.zip) | Building or extending any time-series forecasting service with IBM Granite TTM |

---

### `ttm-forecasting`

Three inference paths, one skill:

| Path | Trigger | What it does |
|---|---|---|
| **Path 1 — watsonx.ai native API** | `TTM_MODEL_ID` set in `.env` | Calls `ibm/granite-ttm-512-96-r2` serverless endpoint — no model download, single-stage Docker, ~1-2 s latency |
| **Path 2 — Local HuggingFace** | `USE_TTM_MODEL=True`, `TTM_MODEL_ID` unset | Downloads `ibm-granite/granite-timeseries-ttm-r2` (~2-3 GB), 2-stage Docker build for OpenShift AMD64 |
| **Path 3 — Mock fallback** | neither set | Sine-wave simulation — local dev / CI only |

The skill asks two questions to pick the right path before writing any code, then generates `.env` setup, service code, and deployment config accordingly.

---

## Installation

### Step 1 — Install the skill

The zip is pre-structured with `.bob/skills/ttm-forecasting/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip ttm-forecasting.zip
```

This creates:

```
.bob/skills/ttm-forecasting/SKILL.md
.bob/skills/ttm-forecasting/sample_data/scenarios/
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Settings → Skills → enable `ttm-forecasting`.

Then ask Bob: *"I need to add TTM temperature forecasting to my service"* — the skill activates automatically.

### Step 3 — Set credentials (Path 1 only)

```bash
# Copy and fill in your values
cp forecast-backend/.env.example forecast-backend/.env

# Minimum for watsonx.ai native path:
TTM_MODEL_ID=ibm/granite-ttm-512-96-r2
WML_API_KEY=<your-ibm-cloud-api-key>
WML_SPACE_ID=<your-wml-deployment-space-guid>
IBM_CLOUD_REGION=us-south
FREQUENCY=1min          # must be lowercase
```

---

## Usage Examples

Once activated, you can ask Bob:

- *"Add TTM temperature forecasting to my FastAPI service"*
- *"I have an IBM Cloud account — set up the watsonx.ai native API path"*
- *"I'm working offline — use the local HuggingFace model instead"*
- *"Build a dashboard.html to visualise the forecast output"*
- *"Why is my FREQUENCY env var breaking the TTM model?"*
- *"Add OpenScale payload logging for governance"*
- *"Run all 10 truck forecasts concurrently in the fleet endpoint"*

---

## What Bob Can Help You Build

1. **Temperature breach forecasting** — 96-min ahead prediction with cargo-type normalisation and threshold risk scoring
2. **Fleet-wide concurrent forecasting** — all trucks in parallel via `ThreadPoolExecutor`, ~1-2 s total
3. **Demand / IoT / energy forecasting** — same model, any numeric time series at `1min` / `5min` / `1h` / `1d`
4. **Governance-wired inference** — OpenScale payload logging on every native API call (fire-and-forget, never blocks the forecast)
5. **Forecast visualisation** — self-contained `dashboard.html` with ECharts line chart, risk cards, and threshold line

---

## Prerequisites

Before using this skill, ensure you have:

- **Python 3.11+**
- **IBM Cloud** account with WML enabled *(Path 1 only)*
- `WML_API_KEY` — IBM Cloud → Manage → Access (IAM) → API keys → Create
- `WML_SPACE_ID` — Watson Studio → Deployments → Spaces → copy GUID from URL
- `IBM_CLOUD_REGION` — region of your WML instance (`us-south`, `eu-gb`, `eu-de`, `jp-tok`, `au-syd`)
- Outbound HTTPS to `<region>.ml.cloud.ibm.com` and `iam.cloud.ibm.com`

For **Path 2 (local pipeline)** instead:
- `granite-tsfm>=0.2.0`, `torch>=2.4.0`, `transformers>=4.41.0`
- ~4 GB RAM, ~3 GB disk for model cache

---

## Directory Structure

```
bob-modes-skills/ttm-forecast/
├── README.md                                     ← this file
├── ttm-forecasting.zip                           ← install this
└── skills/
    └── ttm-forecasting/
        ├── SKILL.md                              ← full skill spec (v2.0.0)
        └── sample_data/
            └── scenarios/
                ├── README.md                     ← scenario guide + accuracy benchmarks
                ├── stock_price_scenario.json     ← 512 pts · 1h · financial
                ├── website_traffic_scenario.json ← 512 pts · 1h · capacity planning
                ├── sales_scenario.json           ← 512 pts · 1d · retail
                ├── iot_sensor_scenario.json      ← 512 pts · 5min · predictive maintenance
                └── custom_template.json          ← template for your own data
```

---

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **Inference path selection** | Guided decision tree — watsonx.ai native API vs local HuggingFace vs mock |
| **Native API integration** | `score_via_native_api()` with IAM token refresh, correct payload shape, response parsing |
| **Local pipeline** | TSFM-first load sequence, output normalisation for all TSFM output shapes |
| **Cargo normalisation** | `_CARGO_BASE` map prevents garbage context windows during simulation incidents |
| **Fleet concurrency** | `ThreadPoolExecutor` pattern — 10 trucks in parallel, per-truck timeout + fallback |
| **OpenScale logging** | Fire-and-forget daemon thread; reads IDs from `governance/artifacts/deployment.json` |
| **Dashboard scaffold** | Self-contained `dashboard.html` — ECharts, risk cards, threshold line, live API wiring |
| **Risk scoring** | 50% temp risk + 30% weather + 20% cargo value; CRITICAL / WARNING / NORMAL levels |

---

## Troubleshooting

**Skill doesn't activate:**
1. Verify `.bob/skills/ttm-forecasting/SKILL.md` exists after unzipping
2. Restart Bob to refresh the skills list

**`FREQUENCY` env var breaks the TTM model:**
Must be lowercase — `1min`, not `1MIN`. Uppercase is silently accepted by dotenv but rejected by the native API schema validator.

**`401 Unauthorized` from watsonx.ai:**
IAM token expired or `WML_SPACE_ID` doesn't match `IBM_CLOUD_REGION`. Re-check both values.

**Granite TTM loads inconsistently (Path 2 / local):**
Use the TSFM-first path — `TinyTimeMixerForPrediction.from_pretrained()` + `TimeSeriesForecastingPipeline`. Do not use `AutoModel.from_pretrained()` on Apple Silicon.

**OpenScale payload logging silently skipped:**
`governance/artifacts/deployment.json` has no `payload_data_set_id` yet. Run `python governance/setup/provision.py` to populate it.

**Fleet endpoint slow (>15 s):**
`ThreadPoolExecutor` must be active with `FLEET_WORKERS = min(10, len(trucks))`. Check that per-truck calls aren't serialised.

---

## Related

- [`skills/ttm-forecasting/SKILL.md`](skills/ttm-forecasting/SKILL.md) — complete technical specification
- [`skills/ttm-forecasting/sample_data/scenarios/README.md`](skills/ttm-forecasting/sample_data/scenarios/README.md) — scenario guide and accuracy benchmarks
- [`../../forecast-backend/`](../../forecast-backend/) — production implementation this skill is based on
- [`../../governance/`](../../governance/) — OpenScale governance module

# Made with Bob
