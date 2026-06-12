# Real-Time Guardrails Skill — Usage Guide

This guide is for the **person installing and invoking the skill** (partner, developer, or platform owner). For internal mechanics and reference materials, see `SKILL.md` and `reference/`.

## Quick start

### 1. Install the skill into your Bob workspace

```bash
# from the bob-skills/ directory containing real-time-guardrails/
cp -r real-time-guardrails ~/your-repo/.bob/skills/
```

Bob auto-discovers any skill in `.bob/skills/`. No additional registration needed.

### 2. Verify Bob loads the skill

Open your project in Bob and ask:

> *"Do you have a real-time-guardrails skill?"*

Bob should confirm and offer to walk you through the workflow.

### 3. Install the underlying Python package

The skill drives the integration, but the runtime enforcement is done by the `real-time-guardrails` Python package.

**Important:** the package is NOT on PyPI as of today. Partners install it from source in the building-blocks repo. We'll publish to PyPI once it's GA — this step gets simpler then. For now:

**Fastest path — run the bundled setup script:**

```bash
bash .bob/skills/real-time-guardrails/setup.sh
```

This script:
- Verifies Python 3.11+ is available
- Clones the building-blocks repo (or uses an existing clone via `BB_REPO_DIR=...`)
- Creates a dedicated venv at `~/guardrails-venv` (override with `VENV_DIR=...`)
- **Pre-flights the dependency resolution with `pip install --dry-run`** — catches conflicts before committing the install (see Known Dependency Conflicts below)
- Installs `real-time-guardrails[all]` from source in editable mode
- Prints next-step guidance for credentials and a sanity test

**Manual path** (if you want to control the install yourself):

```bash
# Python 3.11-3.13 (3.14+ not yet supported by the SDK's wheel surface)
python3.11 --version

# Clone building-blocks if you haven't already
git clone https://github.com/ibm-self-serve-assets/building-blocks ~/src/building-blocks

# Create a DEDICATED venv (do NOT install into your existing project venv —
# see Known Dependency Conflicts below for why)
python3.11 -m venv ~/guardrails-venv
source ~/guardrails-venv/bin/activate

# Install with all extras from source (editable).
# IMPORTANT: the quotes around the path+extras are required on zsh (macOS default shell).
# Without them, zsh interprets [all] as an array subscript, the path resolves to empty,
# and pip errors with `is not a valid editable requirement`.
pip install -e "$HOME/src/building-blocks/ai-trust/real-time-guardrails/assets/sdk[all]"
```

The `[all]` extra adds REST server + MCP server interfaces. The required `[metrics,llmaj]` extras are part of the base install (always pulled in) — without them, registry build fails with `ModuleNotFoundError: No module named 'unitxt'`.

### Known Dependency Conflicts

The SDK sits on top of `ibm-watsonx-gov[metrics,llmaj]`, which transitively pulls a large slice of the LLM ecosystem: `langchain-openai`, `langchain-google-genai`, `google-genai`, `litellm`, `openai`, `langchain-ibm`. These packages push minimum versions of the HTTP and data layers underneath (`httpx`, `pydantic`).

**If you install into an existing project venv that has stricter pins** (e.g., `pydantic==2.9.2` or `httpx==0.27.2` from an older app), pip raises `ResolutionImpossible`. The `setup.sh` script's pre-flight catches this before the install commits — but if you hit it manually, here are today's known floors:

| Layer package | Pinned by | Resolution range to use |
|---|---|---|
| `pydantic` | `ibm-watsonx-gov 1.4.x` requires `>=2.10.3,<3.0.0` | `pydantic>=2.10.3,<3.0.0` |
| `httpx` | `google-genai 1.52+` requires `>=0.28.1`; `ibm-watsonx-ai` requires `<0.29` | `httpx>=0.28.1,<0.29` |

**The right technique, not just the floors.** These floors WILL rise again as the LLM ecosystem evolves — re-check quarterly. The diagnostic pattern that catches whatever the next conflict turns out to be:

```bash
# Run pip's full SAT solve, no packages installed, full conflict report in ~30s-2min.
python3.11 -m venv /tmp/resolve-check
source /tmp/resolve-check/bin/activate
pip install --upgrade pip
pip install --dry-run -e "$HOME/src/building-blocks/ai-trust/real-time-guardrails/assets/sdk[all]"
```

If output ends with `Would install <long list>`, you're clean. If it ends with `ResolutionImpossible`, the report above it names the exact packages and versions colliding. Match the Python version pip uses to your target deployment (we test with 3.11).

**Recommended posture:** always use a dedicated venv for guardrails. The `setup.sh` script does this by default. It eliminates the entire class of "my existing project's pins broke the guardrails install" failures.

### 4. Provision IBM Cloud services

Always required:
- **watsonx.governance** — IBM Cloud console → Catalog → search "watsonx.governance" → Create. Choose a region close to your compute.

Optional (unlocks 3 LLM-as-judge metrics):
- **watsonx.ai project** — https://dataplatform.cloud.ibm.com → Projects → New project
- **Watson Machine Learning** — from inside the project: Manage → Services and Integrations → Associate Service → Watson Machine Learning (free tier OK for testing)

### 5. Set credentials

```bash
cd <your-project-root>
cp .bob/skills/real-time-guardrails/assets/env.example .env
chmod 600 .env

# Edit .env, paste your IDs. Use read -s for the API key to avoid shell history:
read -s -p "API key: " key && printf 'WATSONX_APIKEY=%s\n' "$key" >> .env && unset key
```

Required: `WATSONX_APIKEY`, `WXG_SERVICE_INSTANCE_ID`.
Optional: `WXG_PROJECT_ID` (unlocks LLM-judge metrics), `WATSONX_URL` (region override), `WXG_JUDGE_MODEL_ID` (LLM-judge model override).

### 6. Smoke-test the package

```python
from real_time_guardrails import GuardrailsEvaluator
ev = GuardrailsEvaluator()
print("metrics:", ev.list_metrics()["total"])   # 28 (or 25 without WXG_PROJECT_ID)

result = ev.evaluate(input_text="My SSN is 123-45-6789", metrics=["PII Detection"])
print(result["PII Detection"].score, result["PII Detection"].action)
# Expect: score ~0.6-0.9, action="Block"
```

### 7. Invoke the skill in Bob

Open your repo in Bob and describe your agent. Examples that activate this skill:

- *"I need to add safety guardrails to my RAG chatbot before going to production"*
- *"Add PII detection and HAP screening to my LangChain agent's outputs"*
- *"How do I wire guardrails into a watsonx Orchestrate agent with three tools?"*
- *"My chat widget calls the LLM directly from the browser — how do I add guardrails without leaking the API key?"*
- *"I need to author a custom LLM-as-judge metric for compliance citation accuracy"*

Bob will drive the 5-phase workflow (Setup → Design → Implement → Test & tune → Deploy).

---

## Prerequisites checklist

| Requirement | Why | Check |
|---|---|---|
| Python 3.11–3.13 | IBM SDK chain doesn't support 3.14 (as of SDK 1.4.2) | `python3 --version` |
| IBM Cloud account | watsonx.governance is required | https://cloud.ibm.com |
| watsonx.governance subscription | Source of metric scoring | IBM Cloud → Resource list |
| (Optional) watsonx.ai project + WML | Unlocks 3 LLM-judge metrics | https://dataplatform.cloud.ibm.com |
| Outbound HTTPS to `*.ml.cloud.ibm.com` + governance regional endpoint | SDK calls IBM Cloud APIs (air-gap not supported) | network policy review |
| Repo `.env` with `chmod 600` | Credential hygiene | `ls -la .env` |
| `.env` in `.gitignore` | Prevent commit leaks | `grep -E '^\.env' .gitignore` |

---

## First-time tips

1. **Don't paste credentials into Bob's chat.** Bob will guide you to set them in `.env`. If you accidentally paste a key, rotate it at IBM Cloud → Manage → Access (IAM) → API keys.
2. **Start with the 25-metric subset.** If you don't have `WXG_PROJECT_ID`, you still get 25 of 28 metrics. The 3 LLM-judge metrics (Answer Completeness, Conciseness, Tool Call Relevance) are opinionated and you may want to author replacements anyway.
3. **Build the evaluator ONCE at app startup.** Per-request instantiation costs seconds. The reference examples all show the startup-build pattern.
4. **Pick ONE auto-trigger pattern per agent.** Don't mix middleware + decorator + callback in the same service — gaps appear at the seams.
5. **Order metrics cheap-first.** Pattern matching (~1 ms) before Granite Guardian (200-800 ms) before LLM-judge (1-3 s). The skill walks you through this in Phase 2.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ResolutionImpossible` during `pip install` | Existing venv has stricter pin on `pydantic` (<2.10.3) or `httpx` (<0.28.1) than the SDK needs | Use a dedicated venv (the `setup.sh` script does this), OR relax those pins in your `requirements.txt`. See "Known Dependency Conflicts" above. |
| `ConfigError: Missing required environment variable(s): WATSONX_APIKEY` | env vars not exported in this shell | `set -a; source .env; set +a` |
| `ModuleNotFoundError: No module named 'unitxt'` | Installed without `[all]` extra (or `[metrics]` extra) | Re-install with `pip install -e "<sdk-path>[all]"` — quotes are required on zsh |
| `is not a valid editable requirement` from pip | zsh ate the `[all]` as an array subscript (no quotes) | Use `pip install -e "<sdk-path>[all]"` (with quotes); or use bash; or use the `setup.sh` script which handles this. |
| `EvaluatorInitError: Failed to initialize ibm_watsonx_gov MetricsEvaluator` | Wrong API key, missing permissions, or wrong service instance ID | Re-check IDs in IBM Cloud → Resource list → Instance → GUID |
| `project_id ... is not associated with a WML instance` | watsonx.ai project missing WML association | Project → Manage → Services and Integrations → Associate Watson Machine Learning |
| `UnknownMetricError: 'Conciseness (LLM Judge)'` (or Answer Completeness / Tool Call Relevance) | `WXG_PROJECT_ID` not set; those 3 metrics dropped from registry | Set `WXG_PROJECT_ID` + associate WML, OR don't request those metrics |
| Network/DNS timeout to `*.ml.cloud.ibm.com` | Wrong region in `WATSONX_URL` | Set to: `us-south`, `eu-de`, `eu-gb`, `jp-tok`, or `au-syd` |

For deeper troubleshooting (per-error guidance, IBM Cloud UI navigation), Bob loads `reference/setup-and-credentials.md`.

---

## What "complete" looks like

After running the full skill workflow, you should have:

- [ ] `GuardrailsEvaluator` instantiated once at app startup
- [ ] All 4 choke points wired (or documented if you skip one)
- [ ] One auto-trigger pattern chosen and consistently applied (or explicit wiring)
- [ ] `AuditLogger` writing to a JSONL file or sink (Splunk/ELK/CloudWatch)
- [ ] Thresholds tuned against representative sample workload
- [ ] Block-action responses return `result.fallback_message` (no metric details leaked)
- [ ] Production dashboards: block/flag rate, latency per choke point, LLM-judge cost (if used)
- [ ] Network egress allowlist updated for IBM Cloud endpoints
- [ ] Credential rotation runbook documented

---

## Updating the skill

To pick up a newer version of the skill:

```bash
cd <bob-skills-source>
git pull
cp -r real-time-guardrails ~/your-repo/.bob/skills/   # overwrite
```

Bob picks up the updated skill on next invocation. No restart needed.
