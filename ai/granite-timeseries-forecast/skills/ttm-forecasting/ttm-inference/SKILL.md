---
name: ttm-inference
description: TTM inference path selection and service code generation — covers watsonx.ai native API (Path 1), local HuggingFace pipeline (Path 2), and mock fallback (Path 3). Includes .env setup, IBM Cloud credentials, IAM token refresh, payload structure, output normalisation, Docker build, dependencies, and troubleshooting.
---

# TTM Inference — Path Selection & Service Code

## Step 1 — Choose Your Inference Path

Before writing any code, ask the user (or infer from context) which path applies. The three paths are mutually exclusive:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PATH 1 — IBM watsonx.ai Native API  (RECOMMENDED for production)       │
│  Trigger : TTM_MODEL_ID is set in .env                                  │
│  Needs   : WML_API_KEY, WML_SPACE_ID or WML_PROJECT_ID, IBM_CLOUD_REGION│
│  Model   : ibm/granite-ttm-512-96-r2  (IBM SaaS hosted — no download)  │
│  Latency : ~1-2 s per call                                              │
│  Docker  : Single-stage, no model weights in image                      │
├─────────────────────────────────────────────────────────────────────────┤
│  PATH 2 — Local HuggingFace Pipeline  (macOS dev / air-gapped)          │
│  Trigger : USE_TTM_MODEL=True, TTM_MODEL_ID not set                     │
│  Needs   : granite-tsfm, torch, transformers installed                  │
│  Model   : ibm-granite/granite-timeseries-ttm-r2 (~2-3 GB download)    │
│  Latency : ~2-3 s on CPU after load; ~30-60 s first cold start          │
│  Docker  : 2-stage build (download on ARM, copy to AMD64 image)         │
├─────────────────────────────────────────────────────────────────────────┤
│  PATH 3 — Mock / Statistical Fallback  (development / CI only)          │
│  Trigger : TTM_MODEL_ID not set AND USE_TTM_MODEL=False                 │
│  Needs   : nothing extra                                                 │
│  Output  : Simulated sine-wave forecast — NOT suitable for production   │
└─────────────────────────────────────────────────────────────────────────┘
```

<Steps>
<Step>
Ask these decision questions in order:

1. **Do you have an IBM Cloud account with WML enabled?**
   - Yes → use **Path 1**. Add `TTM_MODEL_ID`, `WML_API_KEY`, `IBM_CLOUD_REGION`, and either `WML_SPACE_ID` (deployment space) or `WML_PROJECT_ID` (Watson Studio project) to `.env`. Use only one — not both.
   - No → go to question 2.

2. **Are you on macOS / Linux and can install ~2-3 GB of model weights?**
   - Yes → use **Path 2**. Set `USE_TTM_MODEL=True` in `.env`, install `granite-tsfm torch transformers`.
   - No → use **Path 3** (mock) for local dev/CI only.
</Step>

<Step>
Set up the `.env` file for the chosen path (see sections below).
</Step>

<Step>
Generate `ttm_model.py` using the routing logic and path-specific code shown below.
</Step>

<Step>
Generate `forecasting_service.py` and `app.py` using the project folder convention from the master skill.
</Step>
</Steps>

---

## Path 1 — watsonx.ai Native API

### `.env` setup

```dotenv
# Activate native API path — takes priority over USE_TTM_MODEL
TTM_MODEL_ID=ibm/granite-ttm-512-96-r2
WML_API_KEY=<your-ibm-cloud-api-key>

# Use EITHER space_id OR project_id — not both
# Deployment space (recommended for production — must have WML runtime associated)
WML_SPACE_ID=<your-wml-deployment-space-guid>
# Watson Studio project (simpler for dev/testing)
# WML_PROJECT_ID=<your-project-guid>

IBM_CLOUD_REGION=us-south   # or eu-gb, eu-de, jp-tok, au-syd, ca-tor

# Correct TTM forecast endpoint — NOT the text/chat endpoint
WML_BASE_URL=https://<IBM_CLOUD_REGION>.ml.cloud.ibm.com
WML_API_VERSION=2025-02-10
WML_FORECAST_PATH=/ml/v1/time_series/forecast

# Must remain False / unset when using the native path
USE_TTM_MODEL=False
CONTEXT_LENGTH=512
PREDICTION_LENGTH=96
FREQUENCY=1D    # daily=1D, hourly=1h, 5-minute=5min — case-sensitive per IBM API docs
```

### How to get credentials

1. **WML_API_KEY** — IBM Cloud console → Manage → Access (IAM) → API keys → Create
2. **WML_SPACE_ID** — Watson Studio → Deployments → Spaces → your space → copy GUID from URL (preferred for production — associate a WML runtime instance to the space first)
3. **WML_PROJECT_ID** — Watson Studio → your project → Manage tab → copy Project ID (simpler for dev/testing)
4. **IBM_CLOUD_REGION** — match the region of your WML instance URL (e.g. `ca-tor.ml.cloud.ibm.com` → `ca-tor`)

### Routing logic (`ttm_model.py`)

```python
def forecast(self, historical_data):
    if self._ttm_model_id:                    # PATH 1 — native API
        return self.score_via_native_api(historical_data)
    if not self.model_loaded or not self.pipeline:
        raise RuntimeError("Model not loaded")
    return self._run_local_pipeline(historical_data)  # PATH 2
```

`is_loaded()` returns `True` immediately when `TTM_MODEL_ID` is set — no model download, no warmup wait.

### IAM token refresh

Tokens expire after ~1 hour. Refresh automatically:

```python
if time.time() >= self._token_expiry - 60:   # refresh 60 s before expiry
    self._refresh_iam_token()
```

Never hardcode a bearer token. Always fetch from `https://iam.cloud.ibm.com/identity/token`.

### Native API payload structure

```python
# Scope: use space_id OR project_id — not both. space_id takes priority if both set.
scope_key = "space_id" if WML_SPACE_ID else "project_id"
scope_val = WML_SPACE_ID or WML_PROJECT_ID

payload = {
    "model_id": "ibm/granite-ttm-512-96-r2",
    scope_key: scope_val,
    "schema": {
        "timestamp_column": "date",          # name must match the key in data dict below
        "target_columns":   ["value"],       # name must match the key in data dict below
        "freq":             "1D",            # 1D=daily, 1h=hourly, 5min=5-minute
    },
    "parameters": {"prediction_length": 96},
    "data": {
        "date":  ["2024-01-01T00:00:00", ...],   # ISO-8601 strings, 512 entries
        "value": [2.5, 2.6, 2.4, ...],           # 512 floats — key must match target_columns
    },
}
```

> ⚠️ The `timestamp_column` name and `target_columns` names **must exactly match** the keys used in the `data` dict. Mismatch causes a silent 400 error.

Endpoint URL:
```
POST https://<IBM_CLOUD_REGION>.ml.cloud.ibm.com/ml/v1/time_series/forecast?version=2025-02-10
```

> ⚠️ Do **NOT** use the `/ml/v1/text/chat` endpoint — that is for LLM text generation, not TTM forecasting.

Response shape: `{"results": [{"value": [...96 floats...], "date": [...96 timestamps...]}]}`

---

## Path 2 — Local HuggingFace Pipeline

### `.env` setup

```dotenv
USE_TTM_MODEL=True
TTM_MODEL_ID=                       # leave empty — triggers local path
TTM_MODEL_PATH=ibm-granite/granite-timeseries-ttm-r2
TTM_MODEL_REVISION=main
CONTEXT_LENGTH=512
PREDICTION_LENGTH=96
FREQUENCY=1min
DEVICE=cpu                          # or cuda
```

### Install dependencies

```bash
pip install "granite-tsfm[notebooks]==0.3.3" torch transformers
```

### Loading sequence — preserve this exactly

```python
from tsfm_public import TinyTimeMixerForPrediction, TimeSeriesForecastingPipeline

model = TinyTimeMixerForPrediction.from_pretrained(
    TTM_MODEL_PATH,
    revision=TTM_MODEL_REVISION
)
pipeline = TimeSeriesForecastingPipeline(
    model=model,
    timestamp_column="timestamp",
    id_columns=["id"],
    target_columns=["value"],
    context_length=CONTEXT_LENGTH,
    prediction_length=PREDICTION_LENGTH,
    freq=FREQUENCY,
    device=DEVICE,
)
```

> ⚠️ Do **not** use `AutoModel.from_pretrained()` — it misses TTM-specific config and fails silently on Apple Silicon.

### Inference output normalisation

TTM pipeline outputs vary by TSFM version. Always normalise defensively:

```python
raw = pipeline(context_data)
# raw may be: dict, DataFrame, Series, ndarray, or nested list

if isinstance(raw, dict):
    raw = raw.get("prediction") or raw.get("forecast") or list(raw.values())[0]

if isinstance(raw, pd.DataFrame):
    col = next((c for c in ["value_prediction","prediction","forecast","value"]
                if c in raw.columns), None)
    raw = raw[col].values if col else raw.iloc[:, 0].values

arr = np.asarray(raw, dtype=float).flatten()
arr = arr[np.isfinite(arr)]          # strip NaN / Inf
arr = arr[:PREDICTION_LENGTH]        # truncate to horizon
```

### Docker 2-stage build (for OpenShift AMD64)

```dockerfile
# Stage 1 — download model on native arch (e.g. ARM Mac)
FROM python:3.11-slim AS model-downloader
RUN pip install "granite-tsfm[notebooks]==0.3.3"
RUN python -c "from tsfm_public import TinyTimeMixerForPrediction; \
    TinyTimeMixerForPrediction.from_pretrained('ibm-granite/granite-timeseries-ttm-r2', \
    cache_dir='/cache')"

# Stage 2 — final AMD64 image
FROM --platform=linux/amd64 python:3.11-slim
COPY --from=model-downloader /cache /app/.cache/huggingface
ENV HF_HOME=/app/.cache/huggingface
```

> ⚠️ First build downloads ~2-3 GB. Use `--cache-from` in CI to avoid re-downloading every build.
> For production, **Path 1 is strongly preferred** — it eliminates the large image entirely.

---

## Path 3 — Mock Fallback

Triggered automatically when neither `TTM_MODEL_ID` nor `USE_TTM_MODEL=True` is set. Returns a sine-wave-based simulated forecast. **Use only in local dev / CI — never in production or demos.**

---

## Dependencies

### Path 1 (native API) — minimal

```txt
requests>=2.31.0
pandas>=2.1.0
numpy>=1.26.0,<2.0.0
python-dotenv>=1.0.0
# Governance (optional)
ibm-cloud-sdk-core>=3.18.0
ibm-watson-openscale>=3.1.8
```

### Path 2 (local pipeline) — full

```txt
torch>=2.4.0
transformers>=4.41.0
granite-tsfm>=0.2.0
requests>=2.31.0
pandas>=2.1.0
numpy>=1.26.0,<2.0.0
```

### System requirements

| Requirement | Path 1 | Path 2 |
|---|---|---|
| RAM | 512 MB | 4–8 GB |
| Disk | minimal | ~2–3 GB model cache |
| GPU | not needed | optional (CUDA) |
| Internet | IBM Cloud endpoint | HuggingFace Hub (first run only) |

---

## Troubleshooting

| Error | Fix |
|---|---|
| `WML_API_KEY is not set` | Add `WML_API_KEY=<key>` to `.env`. On OpenShift use a Secret — never a ConfigMap. |
| `401 Unauthorized` from native API | IAM token expired, or `WML_SPACE_ID`/`WML_PROJECT_ID` wrong. Verify GUID matches `IBM_CLOUD_REGION`. |
| `400 Bad Request` | Check `timestamp_column` and `target_columns` names exactly match the keys in the `data` dict. Also verify `WML_SPACE_ID` region matches `IBM_CLOUD_REGION`. |
| `Need at least 512 data points, got N` | Scenario JSON file is a stub — generate or load a real 512-point dataset before calling the API. |
| Wrong endpoint used | TTM uses `/ml/v1/time_series/forecast` — **not** `/ml/v1/text/chat` (that is for LLMs). |
| `FREQUENCY` format error | IBM API is case-sensitive: daily=`1D`, hourly=`1h`, 5-minute=`5min`. Check exact casing in IBM docs for your interval. |
| `project_id` vs `space_id` confusion | For the TTM serverless API both work — no deployment asset needed. Use `space_id` when you have a WML deployment space with runtime; use `project_id` for simpler dev/testing. Never send both. |
| Granite TTM loads inconsistently (Path 2) | Use `TinyTimeMixerForPrediction.from_pretrained()` + `TimeSeriesForecastingPipeline`. Never `AutoModel.from_pretrained()`. |
| `AutoConfig.from_pretrained()` fails | Add `trust_remote_code=True`: `AutoConfig.from_pretrained(TTM_MODEL_PATH, trust_remote_code=True)` |
| Pipeline returns unexpected shape | Use the normalisation block above — flatten to 1-D float numpy array, strip NaN/Inf. |
| `JSON serialization fails — NaN in response` | Use a `safe_float` helper: `return f if np.isfinite(f) else None` |
