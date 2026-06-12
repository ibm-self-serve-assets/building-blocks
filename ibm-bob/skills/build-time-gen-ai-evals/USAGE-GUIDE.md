# Build-Time GenAI Evaluations Skill — Usage Guide

This guide is for the **person installing and invoking the skill**. For internal mechanics and detailed reference materials, see `SKILL.md` and `reference/`. For the full prerequisites checklist (software, credentials, hardware, network, troubleshooting), see `assets/PREREQUISITES.md`.

## Quick start

### 1. Install the skill into your Bob workspace

```bash
cp -r build-time-gen-ai-evals ~/your-repo/.bob/skills/
```

Bob auto-discovers skills in `.bob/skills/`. No additional registration needed.

### 2. Install the watsonx.governance SDK

The skill drives the workflow; the actual evaluation is run by the `ibm-watsonx-gov` Python SDK installed directly into your environment.

**Fastest path — run the bundled setup script:**

```bash
bash .bob/skills/build-time-gen-ai-evals/setup.sh
```

This script:
- Verifies Python 3.11+ is available
- Creates a dedicated venv at `~/gen-ai-evals-venv` (override with `VENV_DIR=...`)
- **Pre-flights the dependency resolution with `pip install --dry-run`** — catches conflicts before committing the install (see Known Dependency Conflicts below)
- Installs `ibm-watsonx-gov[metrics,agentic,tools,llmaj]` with the bound fixes
- Prints next-step guidance for credentials and a sanity test

**Manual path** (if you want to control the install yourself):

```bash
# Python 3.11–3.13 (3.14+ not yet supported by the SDK's wheel surface)
python3.11 --version

# Create a DEDICATED venv (do NOT install into your existing project venv —
# see Known Dependency Conflicts below for why)
python3.11 -m venv ~/gen-ai-evals-venv
source ~/gen-ai-evals-venv/bin/activate

# Install with the full extras for partner-side flexibility
pip install \
  "ibm-watsonx-gov[metrics,agentic,tools,llmaj]>=1.4.0,<2.0.0" \
  "ibm_watsonx_ai>=1.3.13,<2.0.0" \
  "pydantic>=2.10.3,<3.0.0" \
  "httpx>=0.28.1,<0.29" \
  "pandas>=2.2,<3.0"
```

The `[metrics,agentic,tools,llmaj]` extras give you:
- **`metrics`** — deterministic RAG metrics (faithfulness, answer relevance, context relevance, retrieval precision)
- **`agentic`** — tool-call accuracy / parameter accuracy / relevance / syntactic validity
- **`tools`** — the SDK's tool catalog functionality
- **`llmaj`** — LLM-as-judge metrics PLUS the ability to author custom LLM-judge metrics for domain-specific guardrails

### Known Dependency Conflicts

The SDK pulls a large slice of the LLM ecosystem (`langchain-openai`, `langchain-google-genai`, `google-genai`, `litellm`, `openai`, `langchain-ibm`) via the `[llmaj]` extra. These packages push minimum versions of the HTTP and data layers underneath (`httpx`, `pydantic`).

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
pip install --dry-run \
  "ibm-watsonx-gov[metrics,agentic,tools,llmaj]>=1.4.0,<2.0.0" \
  "ibm_watsonx_ai>=1.3.13,<2.0.0"
```

If output ends with `Would install <long list>`, you're clean. If it ends with `ResolutionImpossible`, the report above it names the exact packages and versions colliding. Match the Python version pip uses to your target deployment (we test with 3.11).

**Recommended posture:** always use a dedicated venv for this skill. The `setup.sh` script does this by default. It eliminates the entire class of "my existing project's pins broke the install" failures.

### 3. Set up credentials

For all evaluations (always required):
```bash
export WATSONX_APIKEY=<from IBM Cloud → Manage → Access (IAM) → API keys>
```

For LLM-as-judge metrics (`LLMAsJudgeMetric`, `LLMValidationMetric`, `AnswerCompletenessMetric`, etc.) — one of:
```bash
export WATSONX_PROJECT_ID=<from watsonx.ai console → project → Manage tab>
# OR
export WATSONX_SPACE_ID=<from watsonx.ai console → deployments → your space>
```

The project/space must be **associated with a Watson Machine Learning instance**. Verify in the watsonx.ai console under Manage → Services and Integrations.

For non-US regions:
```bash
export WATSONX_URL=https://eu-de.ml.cloud.ibm.com  # or eu-gb, jp-tok, au-syd
```

Full credential matrix and IBM Cloud UI navigation: `assets/PREREQUISITES.md`.

### 4. Sanity test

```bash
python3 -c "
import ibm_watsonx_gov.metrics as m
print('OK -', sum(1 for n in dir(m) if n.endswith('Metric')), 'metric classes available')
"
```

Expected output: `OK - 20+ metric classes available`. If you get `ModuleNotFoundError`, the install didn't pull all extras — re-run `setup.sh`.

### 5. Invoke the skill

Open your project in Bob and describe what you want to evaluate:

- *"Evaluate my RAG pipeline against the records in `eval_data.json`"*
- *"Screen these 20 chatbot responses for HAP, PII, and social bias"*
- *"I exported agent traces to `traces.jsonl` — run tool-call accuracy evaluation"*
- *"I need a custom LLM-as-judge metric that scores whether answers correctly cite our compliance policy — help me author it"*
- *"Not sure what to evaluate — here's my app, what do you recommend?"*

Bob will:
1. Run a 1-question detect (what are you evaluating?) + 1-question data-check (data ready?)
2. Scan the workspace for usable files (Phase 1)
3. Show the exact record shape if your data isn't ready (Phase 2)
4. Present an evaluation plan table with per-metric rationale (Phase 3)
5. Call the SDK from your venv, handling errors with clear guidance (Phase 4)
6. Interpret every score against its threshold and produce prioritized fix recommendations (Phase 5)

---

## Prerequisites checklist

| Requirement | Why | Check |
|---|---|---|
| Python 3.11–3.13 | SDK's wheel surface (3.14+ not yet supported) | `python3.11 --version` |
| IBM Cloud account | watsonx.governance is hosted there | https://cloud.ibm.com |
| watsonx.governance subscription | Source of metric scoring | IBM Cloud → Resource list |
| `WATSONX_APIKEY` | Auths every SDK call | IBM Cloud → IAM → API keys |
| `WATSONX_PROJECT_ID` (or `SPACE_ID`) | LLM-as-judge metrics need watsonx.ai access | watsonx.ai console |
| WML association on the project/space | LLM-as-judge metrics call WML-deployed models | watsonx.ai console → Manage → Services and Integrations |
| Outbound HTTPS to `*.ml.cloud.ibm.com` + `iam.cloud.ibm.com` | SDK calls IBM Cloud APIs | Network policy review |

---

## First-time gotchas

1. **Don't install into your existing project venv.** The SDK's `[llmaj]` extra pulls a large dependency footprint that's likely to conflict with stricter pins in your app. Use a dedicated venv (the `setup.sh` default).
2. **Real PII in eval records.** SDK calls hit IBM-hosted watsonx.governance / watsonx.ai. Use anonymized or synthetic data during testing.
3. **Minimum 5 records.** Aggregate stats (mean/min/max) are noisy with fewer; Bob will run the eval anyway and warn.
4. **Field name mismatches.** If your data uses `query` instead of `question`, configure the SDK to look at your columns via `GenAIConfiguration(input_fields=["query"], ...)` — don't rename your data.
5. **LLM-as-judge metrics need configuration.** `LLMAsJudgeMetric()` with no args raises `pydantic.ValidationError`. You must provide a `name` and an `llm_judge` instance — Bob will walk you through this in Phase 3.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ResolutionImpossible` during `pip install` | Existing venv has stricter pin on `pydantic` (<2.10.3) or `httpx` (<0.28.1) than the SDK needs | Use a dedicated venv (the `setup.sh` does this), OR relax those pins in your `requirements.txt`. See Known Dependency Conflicts above. |
| `Unauthorized` / `401` / `WatsonxAiError` | `WATSONX_APIKEY` missing or doesn't have watsonx.governance access | Rotate at IBM Cloud → IAM → API keys; confirm watsonx.governance instance is active |
| LLM-judge metric returns `None` with no error | `WATSONX_PROJECT_ID`/`SPACE_ID` unset, OR project/space not WML-bound | Set the env var; verify WML association in watsonx.ai console |
| `space_id ... is not associated with a WML instance` | Watsonx space exists but isn't bound to WML | Either bind it in IBM Cloud → Resource list → WML service → Manage → Add to space, OR use `WATSONX_PROJECT_ID` instead (projects are usually pre-bound) |
| `ModuleNotFoundError: 'unitxt'` | Installed without `[metrics]` extra | Re-run `setup.sh` (it installs the full extras) |
| `pydantic.ValidationError` for `LLMAsJudgeMetric()` | Instantiated with no args; needs `name` and `llm_judge` | Build the judge per SKILL.md RULE 11, then construct the metric with `name=` and `llm_judge=` |
| `Network/DNS timeout to *.ml.cloud.ibm.com` | Wrong region in `WATSONX_URL` | Set to: `us-south`, `eu-de`, `eu-gb`, `jp-tok`, or `au-syd` |
| Aggregate stats look noisy | < 5 records (high variance) | Add more records |

For deeper troubleshooting, Bob loads `assets/PREREQUISITES.md`.

---

## What "complete" looks like

After running a full evaluation session, you should have:

- [ ] Dedicated venv with `ibm-watsonx-gov[metrics,agentic,tools,llmaj]` installed
- [ ] `WATSONX_APIKEY` exported (and `WATSONX_PROJECT_ID`/`SPACE_ID` if using LLM-judge)
- [ ] Evaluation records in the right shape (5+ for meaningful aggregates)
- [ ] An evaluation plan table approved by you (metrics + rationale per metric)
- [ ] A PASS/FAIL results table for every metric run
- [ ] Evidence surfaced for any PII / HAP / social_bias hits (with character spans)
- [ ] A "What to Fix" section with prioritized [CRITICAL] / [WARNING] / [INFO] items
- [ ] An explicit "done for now" from you (Bob will keep offering follow-up evaluations otherwise)

---

## Updating the skill

```bash
cd <bob-skills-source>
git pull
cp -r build-time-gen-ai-evals ~/your-repo/.bob/skills/   # overwrite
```

Bob picks up the updated skill on next invocation. No restart needed.

## Related skills

- **`real-time-guardrails`** — for runtime per-request enforcement (block/flag answers at request time using the same SDK). If you want to MOVE a build-time eval finding into production runtime, that's the skill. Cross-reference its `reference/custom-metric-authoring.md` for the canonical custom LLM-as-judge authoring guide — applies equally here.
- **`agent-ops`** — for watsonx Orchestrate agent-specific evaluation (benchmarks, red-teaming, traces). Different lifecycle stage focus (WXO agents), different metric surface.
