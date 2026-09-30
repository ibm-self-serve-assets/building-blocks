# Real-Time Guardrails

Your RAG agent passes functional tests — but will it refuse a prompt injection? Will it catch a hallucinated answer that drifts from the retrieved context? Will it leak PII in the response? Will a borderline-toxic input slip through because nobody tuned the threshold?

**Real-Time Guardrails answers these questions in production.** This [Bob](https://bob.ibm.com) custom mode (IBM's AI code assistant) helps you wire IBM watsonx.governance-backed guardrails into your AI/RAG agent across **4 choke points** — input safety, retrieval quality, generation faithfulness, output compliance — with a **3-state Pass/Flag/Block** action model, audit logging, and threshold policy as code. Bob picks metrics from a **28-metric catalog**, tunes thresholds against your sample workload, and wires the auto-trigger (middleware / decorator / framework callback) that fits your agent topology.


## What You Need

**Required:**
- [Bob](https://bob.ibm.com) (IBM's AI code assistant)
- Python 3.11, 3.12, or 3.13 (**not** 3.14 — IBM SDK chain doesn't support it yet)
- IBM Cloud account with a **watsonx.governance** subscription
- The `real-time-guardrails` package with the `[all]` extra:
  ```bash
  pip install "real-time-guardrails[all]"
  ```
- A `.env` file (chmod 600) with:
  ```
  WATSONX_APIKEY=<your-api-key>
  WXG_SERVICE_INSTANCE_ID=<watsonx.governance instance GUID>
  ```
- An AI/RAG agent (or AI pipeline) you want to guard

**Optional:**
- `WXG_PROJECT_ID` (a watsonx.ai project ID) — unlocks the 3 LLM-as-judge metrics (Answer Completeness, Conciseness, Tool Call Relevance). Without it you still get 25 of the 28 catalog metrics.

## Installation

**Option A: Project-level mode (recommended)**

1. Download `real-time-guardrails.zip` from this repo
2. Unzip it into your agent project root:
   ```bash
   unzip real-time-guardrails.zip -d /path/to/your/agent/project
   ```
   This places the `.bob/` folder in your project, next to your agent. Bob will detect the mode automatically.

**Option B: Global mode**

1. Download and unzip `real-time-guardrails.zip`
2. Append the contents of `.bob/custom_modes.yaml` to Bob's global config:
   ```
   ~/Library/Application Support/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml
   ```
3. Copy the `.bob/` folder from the unzipped folder to your project root.

Then switch to the **🛡️ Real-Time Guardrails** mode in Bob's mode selector.

## How It Works

When you start a conversation, Bob asks where you are in the integration:

| Choice | What Bob does |
|--------|-------------|
| **(a) First-time setup** | Provisions IBM Cloud services, sets credentials safely (no chat paste, no shell history), runs the sanity check (PII Detection on a synthetic input). |
| **(b) Mid-integration** | Maps the 4 choke points to your agent, picks metrics per choke point, wires `GuardrailedAgent` or REST calls into your request flow. |
| **(c) Threshold tuning** | Runs your sample workload through guardrails, analyzes the JSONL audit trail, tunes Block/Flag thresholds per metric. |
| **(d) Deployment** | Dockerizes the guardrails layer, wires audit logs to Splunk/ELK, builds the partner-facing compliance dashboard, applies per-tenant policy. |
| **(e) Something else** | Describe what you need and Bob tailors the workflow — including watsonx Orchestrate (WXO) integration via tool wrapping, service-layer middleware, or frontend BFF. |

Bob checks what already exists (credentials set? package installed with `[all]`? `GuardrailsEvaluator` builds? choke points mapped? audit logger wired?) and **only does what's needed** — it won't repeat steps you've already completed.

## Integration Workflow

```
Phase 1: Setup & Verify → Phase 2: Design Integration → Phase 3: Implement → Phase 4: Test & Tune → Phase 5: Deploy & Observe
```

1. **Setup & Verify** (~15 min) — Provisions watsonx.governance, sets credentials via `.env` (chmod 600, `read -s` for the key), installs `real-time-guardrails[all]`, runs a PII Detection sanity check
2. **Design Integration** (~30 min) — Maps the 4 choke points (input → retrieval → generation → output) to your agent, picks metric sets per choke point, **enumerates which of the 28 metrics WILL RUN vs WILL BE SKIPPED given your data shape** (RULE 18)
3. **Implement** (~60 min) — Wires `GuardrailedAgent` or REST calls, adds `AuditLogger`, builds the evaluator once at startup (RULE 16), picks ONE auto-trigger pattern (middleware OR decorator OR framework callback — RULE 17)
4. **Test & Tune** (~30 min) — Runs sample workload, analyzes the JSONL audit log, tunes Block/Flag thresholds per metric — never bypasses a Block by raising thresholds (RULE 10)
5. **Deploy & Observe** (~45 min) — Dockerizes, wires audit logs to Splunk/ELK, builds the compliance dashboard, applies per-tenant threshold policy via YAML/env (RULE 8)

## The 4 Choke Points

```
User input ──► [Input safety] ──► Retrieval ──► [Retrieval quality] ──► LLM ──► [Generation faithfulness] ──► [Output safety] ──► User
```

| Choke point | Recommended metrics | Latency budget |
|---|---|---|
| **Input** | `categories=["safety", "pattern"]` + optionally Topic Relevance | ~1–800 ms |
| **Retrieval** | `categories=["rag_retrieval"]` (Hit Rate, Reciprocal Rank, Retrieval Precision) | ~200–800 ms |
| **Generation** | `categories=["rag_generation"]` (Faithfulness, Answer Relevance, Context Relevance) | ~200–800 ms |
| **Output** | PII Detection, HAP, optional Conciseness (LLM Judge) | ~200 ms – 3 s |

Bob orders checks **cheap-first** (RULE 12): local-Python (~1 ms) → Granite Guardian (~200–800 ms) → LLM-as-judge (1–3 s).

## Mode Contents

```
real-time-guardrails/
└── .bob/
    ├── custom_modes.yaml                                    # Mode definition with 19 mandatory rules
    ├── workflow.md                                          # 5-phase walkthrough with commands per phase
    ├── rules-real-time-guardrails/
    │   ├── 1_setup_and_credentials.xml                      # Env vars, IBM Cloud provisioning, common errors
    │   ├── 2_integration_patterns.xml                       # 4 choke points + Python/REST/Node/MCP code
    │   ├── 3_metric_catalog_and_thresholds.xml              # 28-metric catalog + 5-layer threshold mechanics
    │   ├── 4_audit_and_observability.xml                    # AuditLogger usage, JSONL schema, Splunk/ELK sinks
    │   ├── 5_deployment.xml                                 # Dockerfile, REST vs MCP, scaling, multi-tenant
    │   ├── 6_custom_metric_authoring.xml                    # When + how to author custom LLM-judge metrics
    │   ├── 7_frontend_integration.xml                       # Chat widget, backend proxy, Block/Flag/Pass UX
    │   ├── 8_auto_trigger_patterns.xml                      # Middleware / decorator / callback decision tree
    │   └── 9_watsonx_orchestrate_integration.xml            # WXO topology: tool wrap / service middleware / BFF
    └── reference-payloads/
        ├── input_safety.json, rag_generation.json,          # Verified request payloads
        │   rag_retrieval.json, pattern_keywords.json,
        │   tool_call.json
        ├── thresholds.example.yaml                          # Per-tenant threshold policy as code
        ├── env.example                                      # .env template
        ├── audit_log_sample.jsonl                           # JSONL audit trail sample
        ├── full_pipeline.py                                 # End-to-end GuardrailedAgent class
        ├── custom_metric_example.py                         # Both LLM-judge authoring styles side by side
        ├── middleware_fastapi.py, middleware_flask.py       # HTTP middleware auto-trigger
        ├── decorator_example.py                             # @guard Python decorator auto-trigger
        ├── langchain_callback.py                            # LangChain callback + RunnableLambda
        ├── wxo_tool_wrapper.py                              # WXO Approach 1: @tool() body wrapping
        ├── wxo_service_middleware.py                        # WXO Approach 2: FastAPI middleware on partner service
        ├── frontend_chat_integration.jsx                    # Production React chat widget
        ├── backend_guardrails_proxy.py                      # Flask backend proxy + audit-serving endpoint
        └── dashboard_skeleton.jsx                           # MUI compliance dashboard reading audit log
```

## Key Rules

The mode enforces **19 mandatory rules** that Bob never violates. Highlights:

- **RULE 1** — Never paste live credentials into chat. Always use `.env` + `chmod 600` + `read -s`. If a user pastes a key, Bob interrupts the workflow and walks them through rotation.
- **RULE 7** — Three-state action model (Pass / Flag / Block). Never silently drop the Flag state; flagged calls must surface in the audit log for human review.
- **RULE 8** — Threshold precedence: per-call > constructor > YAML config > env vars > package default. Per-partner thresholds belong in YAML or env, never hard-coded.
- **RULE 10** — Never bypass a Block. Don't recommend raising thresholds to make a failing metric pass. Refuse, regenerate, or document an override with justification.
- **RULE 14** — Never expose `WATSONX_APIKEY` or the guardrails REST endpoint to a browser. Always: browser → partner backend → guardrails service.
- **RULE 16** — Build `GuardrailsEvaluator` once at startup. Per-request instantiation costs several seconds and defeats auto-trigger.
- **RULE 17** — One trigger pattern per agent (middleware OR decorator OR framework callback). Mixing creates gaps where guardrails can be skipped.
- **RULE 18** — Always enumerate "WILL RUN" vs "WILL BE SKIPPED" up front. Partners must never discover at deployment time that 6 metrics they assumed were running aren't.
- **RULE 19** — watsonx Orchestrate (WXO) agents: guardrails attach ONLY at partner-owned boundaries (tool wrap / service middleware / frontend BFF). Never modify WXO itself.

Full list in `.bob/custom_modes.yaml`.

## Example Prompts

```
"Help me add real-time guardrails to my RAG chatbot before we ship to a regulated customer."

"My agent uses watsonx Orchestrate — how do I add guardrails when I can't modify the WXO runtime?"

"PII Detection keeps blocking benign questions about employee directories. How do I tune the threshold without weakening other metrics?"

"I want a partner-facing compliance dashboard that reads from the audit log. Build me the skeleton."

"Author a custom LLM-judge metric that checks whether the response cites a policy document by name."
```

## Auto-Trigger Patterns Covered

| Pattern | Best for | Reference |
|---------|----------|-----------|
| HTTP middleware (FastAPI / Flask) | Web-app agents with a single request entry point | `middleware_fastapi.py`, `middleware_flask.py` |
| Python `@guard` decorator | Function-call agents, tool-based pipelines | `decorator_example.py` |
| LangChain callback / RunnableLambda | LangChain chains | `langchain_callback.py` |
| WXO tool wrapping (Approach 1) | watsonx Orchestrate agents with tool composition | `wxo_tool_wrapper.py` |
| WXO service-layer middleware (Approach 2) | watsonx Orchestrate, RAG-heavy, single retrieval API | `wxo_service_middleware.py` |
| WXO frontend BFF (Approach 3) | watsonx Orchestrate with a custom UI | `frontend_chat_integration.jsx` + `backend_guardrails_proxy.py` |

## Troubleshooting

### `ModuleNotFoundError: No module named 'unitxt'`

You installed `real-time-guardrails` without the `[all]` extra. Fix:

```bash
pip install "real-time-guardrails[all]"
```

The `[all]` extra pulls in `metrics`, `llmaj`, `rest`, and `mcp` subpackages. Without it, the registry build fails on first `GuardrailsEvaluator()`.

### `ConfigError: Missing required environment variable(s): WATSONX_APIKEY`

The `.env` file exists but isn't loaded in the current shell. Fix:

```bash
set -a; source .env; set +a
```

If the variable is set and you still see the error, check for a stale ancestor `.env` overriding it:

```bash
python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"
```

If the path is outside your project, move it aside for the session.

### `EvaluatorInitError: Failed to initialize ibm_watsonx_gov MetricsEvaluator`

Either the API key is invalid, lacks permissions, or the `WXG_SERVICE_INSTANCE_ID` is wrong. Find the correct GUID in IBM Cloud → Resource list → click the watsonx.governance instance → GUID field.

### `project_id ... is not associated with a WML instance`

You set `WXG_PROJECT_ID` but the watsonx.ai project has no Watson Machine Learning service. In the project: **Manage** → **Services and Integrations** → **Associate Service** → **Watson Machine Learning**. Or unset `WXG_PROJECT_ID` if you don't need the 3 LLM-judge metrics.

### A Block fires on legitimate input

Don't raise the block threshold to suppress it (RULE 10). Instead:

1. Read the live Granite Guardian / LLM-judge response in the audit log (Bob can show you the JSON)
2. Decide: is the metric correct (input really is borderline) or incorrect (false positive)?
3. If false positive: tune the threshold with documented justification, or author a custom metric (RULE 13) that scores your domain better
4. If correct: serve `result.fallback_message` or regenerate with adjusted prompt

## Learn More

- [Bob — IBM's AI Code Assistant](https://bob.ibm.com)
- [IBM watsonx.governance](https://www.ibm.com/products/watsonx-governance)
- The 28-metric catalog: see `.bob/rules-real-time-guardrails/3_metric_catalog_and_thresholds.xml`
