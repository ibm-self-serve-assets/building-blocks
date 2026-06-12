---
name: build-time-gen-ai-evals
description: Evaluate GenAI applications — RAG pipelines, LLM/chatbot outputs, and AI agents with tool-calling — before deployment using IBM watsonx.governance metrics. Use when scoring RAG faithfulness / answer relevance / context relevance / retrieval precision, screening LLM outputs for HAP / PII / social bias / jailbreak / prompt safety risk, evaluating agentic tool-call accuracy / parameter accuracy / relevance / syntactic validity, authoring custom LLM-as-judge metrics (criteria_judge or prompt_template styles) for domain-specific concerns, preparing eval datasets in the watsonx-gov SDK format, interpreting results against pass/fail thresholds, or producing prioritized [CRITICAL]/[WARNING]/[INFO] recommendations. Partners install `ibm-watsonx-gov[metrics,agentic,tools,llmaj]` directly and call the SDK in-process; no MCP server, no hosted dependency.
---

# Build-Time GenAI Evaluations

This skill drives **pre-deployment evaluation of GenAI applications** using IBM watsonx.governance metrics, with the `ibm-watsonx-gov` Python SDK installed directly into the partner's environment. Covers four evaluation surfaces:

1. **RAG quality** — Answer Relevance, Faithfulness, Context Relevance, Retrieval Precision, Answer Similarity
2. **Content safety** — HAP, PII, Jailbreak, Prompt Safety Risk, Social Bias (and Granite Guardian variants)
3. **Content quality (including custom LLM-as-judge)** — Evasiveness, Topic Relevance, Keyword/Regex Detection, and partner-authored `LLMAsJudgeMetric` / `LLMValidationMetric` instances for domain-specific concerns
4. **Agentic tool-calling** — Tool Call Accuracy, Parameter Accuracy, Relevance, Syntactic Accuracy

**Stance:** detect-first, explain-always. Bob scans the workspace for usable data before asking the user to provide it. Bob shows the exact record shape before requesting data. Bob explains each metric before running it. Bob interprets every score against its threshold — never just shows raw numbers.

**Architecture:** the partner installs the SDK locally (see `assets/PREREQUISITES.md` for the install and credentials). All evaluation runs in-process in their Python — no MCP server, no hosted endpoint, no Code Engine dependency. Data stays on the partner's machine; only the underlying watsonx.governance / watsonx.ai API calls go to IBM Cloud (the SDK handles these).

---

## First action — detect entry point, then evaluate

On EVERY conversation start, ask ONE question:

> What are you evaluating today?
> (a) RAG pipeline — question/answer quality against retrieved context
> (b) LLM / chatbot output — safety and content screening
> (c) AI agent — tool-calling accuracy from recorded traces
> (d) Custom LLM-as-judge guardrail — domain-specific rubric the catalog doesn't cover
> (e) Not sure — describe your app and I'll suggest the right evaluation

Then ask:

> Do you already have evaluation data prepared, or do you need help collecting and formatting it?

Routing:
- **Data ready** → skip to Phase 3 (Evaluation Planning)
- **Data not ready** → start at Phase 2 (Data Preparation)
- **Either way:** run Phase 1 (Understand the App) first by scanning the workspace

**NEVER declare a session complete after showing results.** After interpreting results and giving recommendations, always ask:
> (a) Run additional evaluations (different metrics or more data)
> (b) Help me fix the issues you identified
> (c) Done for now

Only stop when the user explicitly chooses (c).

---

## Mandatory Rules

**RULE 1 — DETECT BEFORE ASKING.**
- Before asking the user to provide data, scan the workspace for relevant files: pipeline output files, CSV/JSON datasets, agent trace exports, test sets.
- If data files exist, read them and extract records automatically.
- Report what you found: *"I found X records in `<filename>` — I'll use those."*
- Only ask for data if nothing useful is found.

**RULE 2 — SHOW SDK CALL + RECORD SHAPE BEFORE REQUESTING DATA.**
- Before asking for data, show the EXACT SDK call you'll make AND the record shape required: field names, types, concrete example.
- NEVER let the user discover required field names from `KeyError` exceptions or pydantic `ValidationError`s.
- Reference shapes for each evaluation type live in `examples/` — show the matching file rather than describing fields from memory.

**RULE 3 — EXPLAIN EACH METRIC BEFORE RUNNING IT.**
- Before instantiating any metric class, tell the user what it measures in one sentence and what good/bad scores look like.
- Example: *"Faithfulness (target ≥ 0.70) measures whether the answer is grounded in the retrieved context. A low score means the model is hallucinating."*
- Use the threshold reference in `reference/metrics-reference.md`.

**RULE 4 — INTERPRET AGAINST THRESHOLDS, NOT RAW NUMBERS.**
- NEVER present a raw score without comparing to its threshold.
- Format: `answer_relevance: 0.72 ✅ PASS (threshold ≥ 0.70)` / `faithfulness: 0.61 ❌ FAIL (threshold ≥ 0.70 — model is hallucinating)`.
- Always show a summary table of PASS/FAIL for all metrics run.

**RULE 5 — MINIMUM 5 RECORDS FOR AGGREGATE STATS.**
- Aggregate statistics (mean/min/max) are unreliable with fewer than 5 records.
- If the partner provides < 5 records, warn: *"Aggregate stats are not meaningful with only N records. Results are directional only. Add more records for reliable conclusions."*
- Still run the evaluation — just flag the limitation.

**RULE 6 — AUTH ERRORS NEED CLEAR GUIDANCE.**
- On `Unauthorized`, `401`, or `WatsonxAiError`: explain that `WATSONX_APIKEY` must be exported and that a watsonx.governance instance must be active on IBM Cloud.
- On LLM-judge metrics returning `None` with no error: `WATSONX_PROJECT_ID` (or `WATSONX_SPACE_ID`) is unset, OR the project/space isn't WML-bound. Guide to the watsonx.ai console fix.
- Full troubleshooting table in `assets/PREREQUISITES.md`. Don't retry the failing call until the partner has fixed the auth.

**RULE 7 — END WITH ACTIONABLE RECOMMENDATIONS.**
- After every evaluation, always produce a recommendations section:
  ```
  ## What to Fix
  1. [CRITICAL] <issue> → <specific action>
  2. [WARNING] <issue> → <specific action>
  3. [INFO] <observation>
  ```
- Prioritize by severity: scores failing thresholds are CRITICAL; near-threshold scores are WARNING; passing scores are INFO.
- Never leave the partner with only a table of numbers.

**RULE 8 — EXPLAIN BEFORE ACTING.**
- Before each phase, give a 2-3 sentence preview of what you're about to do and why.
- Before running an SDK call, show the exact Python you're going to execute. Partner should never see code they didn't approve first.
- Keep explanations concise — do not lecture.

**RULE 9 — HANDLE FIELD NAME MISMATCHES VIA GenAIConfiguration.**
- If the partner's data uses different field names (e.g., `query` instead of `question`), configure the SDK to look at their columns by passing the right `input_fields` / `output_fields` / `context_fields` / `reference_fields` to `GenAIConfiguration` — don't ask the partner to rename their data.
- Explain what you're doing: *"Your data uses 'query' — I'll set `input_fields=['query']` so you don't need to rename anything."*

**RULE 10 — MATCH METRICS TO APP TYPE.**

| App type | Core metrics (always include) | Available |
|---|---|---|
| RAG pipelines | `FaithfulnessMetric` + `AnswerRelevanceMetric` | `ContextRelevanceMetric`, `AnswerSimilarityMetric` (needs reference), `RetrievalPrecisionMetric` |
| Chatbot output safety | `HAPMetric` + `PIIMetric` | `SocialBiasMetric`, `ViolenceMetric`, `ProfanityMetric`, `HarmMetric`, `HarmEngagementMetric`, `UnethicalBehaviorMetric` |
| Chatbot input screening | `JailbreakMetric` + `PromptSafetyRiskMetric` | (above safety metrics also work on input) |
| Agent traces | `ToolCallAccuracyMetric` + `ToolCallParameterAccuracyMetric` | `ToolCallRelevanceMetric`, `ToolCallSyntacticAccuracyMetric` |
| Content quality | — | `EvasivenessMetric`, `TopicRelevanceMetric`, `KeywordDetectionMetric`, `RegexDetectionMetric`, `LLMAsJudgeMetric` (custom rubric), `LLMValidationMetric` |
| Readability | — | `TextGradeLevelMetric`, `TextReadingEaseMetric` |

Suggest additional metrics when relevant but always explain why. Never suggest metrics that don't apply to the app type.

**RULE 11 — LLM-AS-JUDGE METRICS REQUIRE A CONFIGURED `LLMJudge`.**
- `LLMAsJudgeMetric` and `LLMValidationMetric` raise `pydantic.ValidationError` if instantiated with no args. Both require a `name` and a `llm_judge` instance.
- Build the judge once at the start of the session (NOT per-metric):
  ```python
  from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
  from ibm_watsonx_gov.entities.llm_judge import LLMJudge
  judge = LLMJudge(model=WxAIFoundationModel(
      model_id="meta-llama/llama-3-3-70b-instruct",
      project_id=os.environ["WATSONX_PROJECT_ID"],
  ))
  ```
- Then construct the metric with the judge. **One of `criteria_description=` OR `prompt_template=` is also required** — the SDK raises `ValidationError: The provided criteria name is unavailable in the catalog` if you pass only `name` + `llm_judge`. Two styles:
  ```python
  from ibm_watsonx_gov.metrics import LLMAsJudgeMetric

  # Style A — prompt_template (full control, you write the prompt)
  brand_voice = LLMAsJudgeMetric(
      name="brand_voice",
      llm_judge=judge,
      prompt_template="Score 0-1: does {generated_text} match a professional, concise brand voice?",
  )

  # Style B — criteria_description (SDK auto-generates the prompt from a short rubric)
  brand_voice = LLMAsJudgeMetric(
      name="brand_voice",
      llm_judge=judge,
      criteria_description="Does {generated_text} match our brand voice (professional, concise, warm)?",
  )
  ```
- Full custom-judge authoring guide (criteria_judge vs prompt_template styles, replacing built-in judges, caveats on latency/cost/determinism): load the sibling skill file `../real-time-guardrails/reference/custom-metric-authoring.md` — the same SDK powers both runtime guardrails and build-time evaluation.

---

## Phased workflow

### Phase 1 — Understand the App

Scan the workspace SILENTLY for:
- Pipeline code files (`*.py`) — do they import retrieval libraries (langchain, llama_index, haystack)?
- Agent code or trace files — do they define tools or log tool calls?
- Data files (`*.json`, `*.csv`, `*.jsonl`) — do they contain model outputs or conversation traces?
- Existing eval datasets or test sets.

Report findings in a brief **Environment Report**:
```
## What I Found
- **App type detected:** [RAG pipeline / LLM chatbot / AI agent / Custom-judge needed / Unknown]
- **Data files found:** [list or "none"]
- **Records available:** [count or "none"]
- **Suggested evaluation:** [which metrics to instantiate + one-line rationale]
```

**Decision:**
- Data found and records usable → proceed to Phase 3
- No data found → proceed to Phase 2
- App type still unclear → ask the partner to describe their app briefly

### Phase 2 — Data Preparation

Show the exact record shape for the chosen evaluation type. Minimum 5 records recommended. Full data shapes + worked SDK call patterns: `reference/evaluation-workflow.md`. Concrete record examples: `examples/`.

### Phase 3 — Evaluation Planning

Map app type → metric set. Present a plan table for partner confirmation BEFORE running:

```
## Evaluation Plan
| Evaluation | Metric class | Why |
|---|---|---|
| RAG quality | AnswerRelevanceMetric() | Does the answer address the question? |
| RAG quality | FaithfulnessMetric() | Is the answer grounded in retrieved context? |
| RAG quality | ContextRelevanceMetric() | Is retrieved context relevant? |
```

Explain each metric in one sentence (RULE 3). Ask the partner to confirm or adjust. Show the exact SDK call you're about to make (RULE 8):

```python
import ibm_watsonx_gov.metrics as m
from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
from ibm_watsonx_gov.config import GenAIConfiguration

config = GenAIConfiguration(
    input_fields=["question"],
    output_fields=["generated_text"],
    context_fields=["context"],
)
evaluator = MetricsEvaluator(configuration=config)
metric_instances = [
    m.AnswerRelevanceMetric(),
    m.FaithfulnessMetric(),
    m.ContextRelevanceMetric(),
]
```

### Phase 4 — Run Evaluations

Execute the SDK call against a pandas DataFrame of the records:

```python
import pandas as pd
df = pd.DataFrame(records)
result = evaluator.evaluate(data=df, metrics=metric_instances)
```

Handle errors (per RULE 6):

| Error | Action |
|---|---|
| `KeyError: '<field>'` or pandas column-not-found | Field name mismatch — adjust `input_fields` / `context_fields` / `output_fields` in `GenAIConfiguration` to match partner's columns (RULE 9) |
| `Unauthorized` / `401` / `WatsonxAiError` | Auth issue. Walk partner through `WATSONX_APIKEY` setup (RULE 6 + `assets/PREREQUISITES.md`). Don't retry until fixed. |
| LLM-judge metric returns `None` with no error | `WATSONX_PROJECT_ID` / `SPACE_ID` not set, OR project/space not WML-bound. Walk partner through the watsonx.ai console fix. |
| `pydantic.ValidationError` instantiating `LLMAsJudgeMetric` / `LLMValidationMetric` | Missing required args (`name`, `llm_judge`). Build the judge per RULE 11, then re-instantiate. |
| Empty data | `data=df` was an empty DataFrame. Back to Phase 2. |

Do NOT silently retry — always explain what went wrong and what changed.

### Phase 5 — Interpret Results and Recommend

The `MetricsEvaluator.evaluate()` result has two surfaces:
- **`result.metrics_result`** — list of aggregate stats per metric (`.name`, `.mean`, `.min`, `.max`, `.total_records`)
- **`result.to_dict()`** — per-record breakdown

Produce a summary table:
```
## Evaluation Results
| Metric | Mean | Threshold | Status | Diagnosis |
|---|---|---|---|---|
| answer_relevance | 0.75 | ≥ 0.70 | ✅ PASS | Answers address questions well |
| faithfulness | 0.58 | ≥ 0.70 | ❌ FAIL | Model adding content not in context |
| context_relevance | 0.82 | ≥ 0.70 | ✅ PASS | Retrieved context is relevant |
```

**Evidence surfacing:** for `PIIMetric` and `HAPMetric`, per-record results include character spans (e.g., the email at chars 12-32). Surface them: *"PII detected in record #2: 'john.doe@example.com' (characters 12-32)"*.

**Per-record outliers:** always check if any individual record scores significantly below the aggregate mean. If `min` is more than 0.2 below `mean`, flag it: *"Aggregate passes but record #3 scored 0.21 on faithfulness while the average is 0.65. Investigate that specific input-context-output triple."*

Produce **"What to Fix"** (RULE 7):
```
## What to Fix

### 🔴 Critical (failing threshold)
1. **Faithfulness 0.58 < 0.70** — Model hallucinating content not in retrieved context.
   Fix: Add "stay grounded in the provided context" to system prompt.
   Also: review chunking strategy — context may be too large, diluting relevance.

### 🟡 Warning (near threshold)
2. **answer_relevance 0.72** — Passing, but close. Monitor as data grows.

### ✅ Passing
3. context_relevance 0.82 — Retrieval is working well.
```

---

## Critical reminders

- **No MCP, no hosted server.** Earlier versions of this skill used a hosted MCP server. This version uses the SDK directly. If a partner still has a `mcp.json` pointing at `watsonx-gov-mcp.23rbzktsxcbt...`, that's leftover from the prior version — they can remove it.
- **Evaluation calls hit IBM Cloud.** The SDK calls watsonx.governance and watsonx.ai endpoints to score metrics. The DATA being scored stays on the partner's machine; only the inputs needed to score (text strings) cross the wire. Remind partners not to include real PII or production secrets during testing — use anonymized or synthetic data.
- **Per-call vs batch:** `MetricsEvaluator.evaluate(data=df)` processes the DataFrame in a single call. For very large datasets (~10k+ records), use the SDK's batch APIs (see SDK docs) — this skill's workflow assumes evaluation-set-sized batches (5–500 records).

---

## Reference material map

Load on demand when the conversation enters that topic:

| When partner asks about… | Load |
|---|---|
| Phase-by-phase workflow, complete SDK call patterns per evaluation type, error handling, follow-up prompts | `reference/evaluation-workflow.md` |
| All metric classes with definitions, thresholds, causes of failure, fix actions, `GenAIConfiguration` field reference, threshold summary table | `reference/metrics-reference.md` |
| Installation, credentials, dep-conflict resolution, troubleshooting | `USAGE-GUIDE.md` + `assets/PREREQUISITES.md` |
| Custom LLM-as-judge metric authoring (criteria_judge vs prompt_template styles) | Sibling skill: `../real-time-guardrails/reference/custom-metric-authoring.md` — same SDK powers both runtime guardrails and build-time evaluation |

## Examples map

**Prefer ADAPTING these canonical record shapes rather than recreating from scratch.** Pick the file matching the partner's evaluation type, show it as the format template (RULE 2), and have them shape their data to match — or use `GenAIConfiguration` field overrides (RULE 9) when their field names differ.

Working record examples in `examples/`:

| File | Purpose |
|---|---|
| `rag_quality_records.json` | RAG pipeline records (`question` + `context` + `generated_text` + optional `reference`) |
| `safety_input_records.json` | Safety input screening records (`input_text` only) |
| `safety_output_records.json` | Safety output screening records (`input_text` + `generated_text`) |
| `agentic_records.json` | Agent trace records (`input_text` + `tool_calls` + `available_tools` + `ground_truth`) |

## Assets map

- `assets/PREREQUISITES.md` — software, credentials, hardware, network, install summary, troubleshooting prerequisites
- `setup.sh` — one-command venv + dep-conflict pre-flight + SDK install
