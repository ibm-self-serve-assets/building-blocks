# Setup and Credentials

**TRIGGER:** Load when user is in Phase 1 — env-var setup, IBM Cloud provisioning, credential errors (`ConfigError`, `EvaluatorInitError`, `project_id ... is not associated with a WML instance`, `Network/DNS timeout to *.ml.cloud.ibm.com`, `UnknownMetricError`), or when user asks "how do I get my watsonx.governance instance ID" or similar.

---

## Required env vars

**`WATSONX_APIKEY`**
- IBM Cloud API key with permissions on watsonx.governance (and watsonx.ai if using LLM-judge metrics).
- **Find:** IBM Cloud console → Manage → Access (IAM) → API keys → Create.
- **Format:** ~44 chars, mixed case, may contain underscores and hyphens.

**`WXG_SERVICE_INSTANCE_ID`**
- watsonx.governance service instance ID.
- **Find:** IBM Cloud console → Resource list → click the watsonx.governance instance → copy the **GUID** field.
- **Format:** UUID, 36 chars (8-4-4-4-12 hex).

## Optional env vars

**`WXG_PROJECT_ID`**
- watsonx project ID. ONLY required for the 3 LLM-as-judge metrics (Answer Completeness, Conciseness, Tool Call Relevance).
- **Find:** https://dataplatform.cloud.ibm.com → your project → Manage tab → General → copy Project ID.
- **Required setup:** the watsonx.ai project MUST have a Watson Machine Learning (WML) service associated. Verify: project → Manage → Services and Integrations. If missing: Associate Service → Watson Machine Learning → New service (free tier OK).

**`WATSONX_URL`**
- Override the regional endpoint. Default: `https://us-south.ml.cloud.ibm.com`
- **Valid values:** `us-south` | `eu-de` | `eu-gb` | `jp-tok` | `au-syd`
- Set to the region of your watsonx instances.

**`WXG_JUDGE_MODEL_ID`**
- Override the LLM-as-judge model. Default: `llama-3-3-70b-instruct`
- **Find:** dataplatform.cloud.ibm.com → project → Models → use any available model ID.

## Per-metric threshold env vars

**Pattern:** `GUARDRAILS_THRESHOLD_<METRIC_SLUG>=<float>`

**Slug rule:** metric name uppercased, non-alphanumerics replaced with underscores.

**Examples:**
- `"PII Detection"` → `GUARDRAILS_THRESHOLD_PII_DETECTION`
- `"HAP (Hate, Abuse, Profanity)"` → `GUARDRAILS_THRESHOLD_HAP_HATE_ABUSE_PROFANITY`
- `"Faithfulness"` → `GUARDRAILS_THRESHOLD_FAITHFULNESS`

**Category shortcuts:**
- `GUARDRAILS_THRESHOLD_DEFAULT_SAFETY`
- `GUARDRAILS_THRESHOLD_DEFAULT_RAG` (applies to both rag_generation and rag_retrieval)
- `GUARDRAILS_THRESHOLD_DEFAULT_QUALITY`
- `GUARDRAILS_THRESHOLD_DEFAULT_TOPIC`
- `GUARDRAILS_THRESHOLD_DEFAULT_PATTERN`
- `GUARDRAILS_THRESHOLD_DEFAULT_TOOL_CALL`

## `.env` file security RULES

- **RULE:** Always `chmod 600` the `.env` file. Never world-readable.
- **RULE:** Always add `.env` to `.gitignore` (verify in partner's repo).
- **RULE:** Use `read -s` to enter the API key without it appearing in shell history.
- **RULE:** If a partner pastes their API key into chat or a public PR, rotate immediately at IBM Cloud → Manage → Access (IAM) → API keys → Delete the leaked key.

**Pattern:**
```bash
read -s -p "WATSONX_APIKEY: " key
cat >> .env <<EOF
WATSONX_APIKEY=$key
EOF
unset key
chmod 600 .env
```

## IBM Cloud provisioning

| Service | Required | How |
|---|---|---|
| **watsonx.governance** | Always | IBM Cloud console → Catalog → search "watsonx.governance" → choose region → Create. Subscription/seat-based; Granite Guardian calls included. |
| **watsonx.ai project** | Only for LLM-judge metrics | https://dataplatform.cloud.ibm.com → Projects → New project → name + storage. Then Manage → Services and Integrations → Associate Service → Watson Machine Learning. Cost: pay-per-token foundation model inference, ~200-500 input + ~10 output tokens per LLM-judge call. For high-volume, sample (10% of traffic is a common default). |
| **WML (Watson Machine Learning)** | Only if `WXG_PROJECT_ID` is set | Must be associated with the watsonx.ai project. From inside the project: Manage → Services and Integrations → Associate Service → Watson Machine Learning → New service (free tier OK for testing). Without this, LLM-judge metrics fail with `project_id ... is not associated with a WML instance`. |

## Common errors

**`ResolutionImpossible` during `pip install`**
- **Cause:** The partner's existing venv has stricter version pins than `ibm-watsonx-gov[metrics,llmaj]` can accept. Most common: `pydantic==2.9.2` (gov SDK requires `>=2.10.3`) or `httpx==0.27.2` (transitively pulled `google-genai` requires `>=0.28.1`).
- **Today's known floors** (re-check quarterly — these rise as the LLM ecosystem moves):
  - `pydantic>=2.10.3,<3.0.0`
  - `httpx>=0.28.1,<0.29` (must stay <0.29 due to `ibm-watsonx-ai`'s ceiling)
- **Fix:** EITHER use a dedicated venv (the bundled `setup.sh` does this by default — eliminates the entire conflict class), OR relax the stricter pins in the partner's existing `requirements.txt`.
- **Diagnostic recipe** for the next conflict pattern (when the ecosystem moves again):
  ```bash
  python3.11 -m venv /tmp/resolve-check && source /tmp/resolve-check/bin/activate
  pip install --upgrade pip
  pip install --dry-run -e "<building-blocks>/ai-trust/real-time-guardrails/assets/sdk[all]"
  # Note: quotes around the path+extras are required on zsh — without them
  # zsh interprets [all] as an array subscript and pip sees an empty path.
  # If output ends with "Would install <list>", clean. If "ResolutionImpossible",
  # the report names the exact packages and version ranges colliding.
  ```

**`ConfigError: Missing required environment variable(s): WATSONX_APIKEY`**
- **Cause:** The shell where the SDK is being invoked doesn't have the env var exported.
- **Fix:** `set -a; source .env; set +a; python ...` or `bash -c 'set -a && source .env && set +a && python ...'`.

**`ModuleNotFoundError: No module named 'unitxt'`**
- **Cause:** SDK installed without the `[metrics]` extra (always part of `[all]` and the base install). The gov SDK declares unitxt as an optional dep inside `[metrics]`.
- **Fix:** Re-install with `pip install -e "<sdk-path>[all]"` from the building-blocks clone. **Quote the path+extras** — required on zsh (macOS default), where unquoted `[all]` is interpreted as an array subscript and silently produces an empty path.

**`EvaluatorInitError: Failed to initialize ibm_watsonx_gov MetricsEvaluator`**
- **Cause:** API key invalid, lacks permissions, or service instance ID wrong.
- **Fix:** (1) Re-check IDs in IBM Cloud → Resource list → Instance → GUID field. (2) Confirm the API key has IAM access on the governance service.

**`project_id ... is not associated with a WML instance`**
- **Cause:** watsonx.ai project missing WML association.
- **Fix:** Project → Manage → Services and Integrations → Associate Service → Watson Machine Learning.

**Network/DNS timeout to `*.ml.cloud.ibm.com`**
- **Cause:** `WATSONX_URL` is set to the wrong region for your watsonx instance.
- **Fix:** Set `WATSONX_URL` to match instance region: `us-south`, `eu-de`, `eu-gb`, `jp-tok`, or `au-syd`.

**`UnknownMetricError: 'Conciseness (LLM Judge)'`** (or `'Answer Completeness'` or `'Tool Call Relevance'`)
- **Cause:** `WXG_PROJECT_ID` is not set — those 3 metrics are dropped from the registry.
- **Fix:** Either (a) set `WXG_PROJECT_ID` + associate WML, or (b) don't request those metrics.

## See also

- `reference/metrics-catalog.md` — full 28-metric catalog + threshold mechanics + field availability matrix
- `assets/env.example` — annotated env var template
