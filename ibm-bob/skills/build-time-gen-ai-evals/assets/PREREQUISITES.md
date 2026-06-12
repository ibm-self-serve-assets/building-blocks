# Build-Time GenAI Evaluations — Prerequisites

Everything a partner needs in place before invoking the skill. Read this once before the first install; the skill will reference back to it on credential errors.

---

## 1. Software

| Component | Version | Purpose |
|---|---|---|
| **Python** | 3.11, 3.12, or 3.13 (3.14+ NOT supported) | Runtime for `ibm-watsonx-gov` SDK; the SDK chain has C-extension wheels for 3.11–3.13 only |
| **`ibm-watsonx-gov`** | `>= 1.4.0, < 2.0.0` (with `[metrics,agentic,tools,llmaj]` extras) | The evaluation SDK — installed by `setup.sh` or manually per `USAGE-GUIDE.md` |
| **`ibm_watsonx_ai`** | `>= 1.3.13, < 2.0.0` | Foundation-model access for LLM-as-judge metrics |

The full install profile is pinned in `setup.sh` with the dependency-conflict bounds from `USAGE-GUIDE.md`'s Known Dependency Conflicts section.

---

## 2. Credentials

### 2a. IBM Cloud + watsonx.governance (always required)

| Variable | How to get it |
|---|---|
| `WATSONX_APIKEY` | IBM Cloud → Manage → Access (IAM) → API keys → **Create**. Save the key — it's shown only once. |
| watsonx.governance subscription | IBM Cloud → Catalog → search "watsonx.governance" → choose region → Create. |

### 2b. watsonx.ai project or space (required for LLM-as-judge metrics)

The LLM-as-judge metrics (`llm_as_judge`, `llm_validation`, `answer_completeness`, `conciseness`, `tool_call_relevance`) call watsonx.ai's foundation models. You need ONE of:

| Variable | How to get it |
|---|---|
| `WATSONX_PROJECT_ID` | watsonx.ai console → your project → **Manage** tab → General → copy Project ID |
| `WATSONX_SPACE_ID` | watsonx.ai console → **Deployments** → your space → space ID |

**Critical:** the project/space must be **associated with a Watson Machine Learning (WML) instance**. Verify: project → Manage → Services and Integrations. If missing: Associate Service → Watson Machine Learning → New service (free tier is fine for testing).

**Without this:** the deterministic metrics still work (HAP, PII, RAG-retrieval precision, keyword/regex detection, etc.), but `evaluate(...)` will return `None` for any LLM-judge metric and emit a `WatsonxAiError`.

### 2c. Region override (optional)

| Variable | Default | When to set |
|---|---|---|
| `WATSONX_URL` | `https://us-south.ml.cloud.ibm.com` | Set if your watsonx instance is in `eu-de`, `eu-gb`, `jp-tok`, or `au-syd`. Match instance region. |

---

## 3. Recommended shell setup

Add to `~/.zshrc` or `~/.bashrc` for persistent access:

```bash
export WATSONX_APIKEY=<your-key>
export WATSONX_PROJECT_ID=<your-project-id>   # OR WATSONX_SPACE_ID=...
# Optional:
# export WATSONX_URL=https://eu-de.ml.cloud.ibm.com
```

For project-scoped credentials, use a `.env` file in the project root:

```bash
cd <your-project>
cat > .env <<'EOF'
WATSONX_APIKEY=
WATSONX_PROJECT_ID=
EOF
chmod 600 .env

# Use `read -s` so the key never appears in shell history:
read -s -p "WATSONX_APIKEY: " key && printf 'WATSONX_APIKEY=%s\n' "$key" >> .env && unset key
```

Then in Python:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 4. Hardware & network

| Requirement | Notes |
|---|---|
| **RAM** | ~2 GB free for the Python process (the SDK loads several ML libraries) |
| **Disk** | ~1.5 GB for the installed venv (large because of langchain + google-genai + torch transitive deps) |
| **First install time** | ~3–5 minutes for the full extras install |
| **Outbound HTTPS** | `*.ml.cloud.ibm.com` (watsonx.ai), `iam.cloud.ibm.com` (IAM token exchange), `pypi.org` (during install) |
| **Air-gap** | Partially supported via internal PyPI mirror; ask your IBM contact for the mirror URL. Air-gap setup is out of scope for this guide. |

---

## 5. The data you want to evaluate

| Evaluation type | Records you need |
|---|---|
| **RAG quality** | List of `{question, context, generated_text}` records (5+ for meaningful aggregates). Optionally `reference` if you use `answer_similarity`. |
| **Content safety (input screening)** | List of `{input_text}` records — actual user prompts including potentially adversarial examples |
| **Content safety (output screening)** | List of `{input_text, generated_text}` records — model responses to a representative prompt set |
| **Content quality (LLM-as-judge)** | Same shape as RAG quality. Plus a configured `LLMJudge` if using `llm_as_judge` or `llm_validation`. |
| **Agentic tool-call accuracy** | List of `{input_text, tool_calls, available_tools, ground_truth}` records exported from your agent's traces (LangChain, LangGraph, etc. all support trace logging) |

Reference data shapes in [`examples/`](../examples/) — partners should ADAPT the closest match rather than recreate from scratch.

---

## 6. Quick install summary

If everything above lines up, this is the one-time setup:

```bash
# Run the bundled setup script (recommended):
bash .bob/skills/build-time-gen-ai-evals/setup.sh

# OR manual install with the dep-bound fixes from USAGE-GUIDE.md:
python3.11 -m venv ~/gen-ai-evals-venv
source ~/gen-ai-evals-venv/bin/activate
pip install \
  "ibm-watsonx-gov[metrics,agentic,tools,llmaj]>=1.4.0,<2.0.0" \
  "ibm_watsonx_ai>=1.3.13,<2.0.0" \
  "pydantic>=2.10.3,<3.0.0" \
  "httpx>=0.28.1,<0.29" \
  "pandas>=2.2,<3.0"
```

---

## 7. Troubleshooting prerequisites

| Symptom | Cause | Fix |
|---|---|---|
| `ResolutionImpossible` during `pip install` | Existing venv has stricter pin on `pydantic` or `httpx` than the SDK requires | Use the dedicated venv from `setup.sh`, OR relax pins in your project's `requirements.txt`. See `USAGE-GUIDE.md` → Known Dependency Conflicts. |
| `Unauthorized` / `401` from watsonx | `WATSONX_APIKEY` missing, expired, or no access to watsonx.governance | Rotate at IBM Cloud → IAM → API keys; confirm watsonx.governance instance is active |
| `space_id ... is not associated with a WML instance` | Watsonx space exists but isn't bound to WML | Either bind in IBM Cloud → Resource list → WML service → Manage → Add to space, OR use `WATSONX_PROJECT_ID` instead (projects are usually pre-bound) |
| `LLM-judge metric returns None` | `WATSONX_PROJECT_ID` / `SPACE_ID` not exported, OR project/space not WML-bound | Set the env var; verify WML association |
| `Network/DNS timeout to *.ml.cloud.ibm.com` | Wrong region in `WATSONX_URL` | Set to: `us-south`, `eu-de`, `eu-gb`, `jp-tok`, or `au-syd` |
| `ModuleNotFoundError: unitxt` | Installed without `[metrics]` extra | Re-run `setup.sh`, OR re-install manually with the full `[metrics,agentic,tools,llmaj]` extras |

---

## 8. What you do NOT need

- **No MCP server.** Earlier versions of this skill used a hosted MCP. The skill now uses the SDK directly — no separate server process, no Code Engine deployment dependency.
- **No internet-facing service.** Evaluations run locally in your Python process. Only outbound HTTPS to `*.ml.cloud.ibm.com` (for the underlying watsonx.governance / watsonx.ai calls) is required.
- **No fixed regions.** US-South is the default but EU-DE / EU-GB / JP-TOK / AU-SYD all work with `WATSONX_URL` override.
