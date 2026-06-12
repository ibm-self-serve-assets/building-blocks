# Integration Patterns — The 4 Choke Points

**TRIGGER:** Load when designing where to attach guardrails in the agent (Phase 2), picking which metrics + fields to use per choke point, or when user asks about the Python library / REST / MCP interfaces, parallelization, or the OpenAI tool-call payload format.

---

## Cross-reference

If the partner's agent runs on **watsonx Orchestrate (WXO)**, the 4 choke points still apply conceptually, but WHERE you attach them is constrained by WXO's managed-platform boundaries. Don't try to wrap the WXO runtime or insert middleware on WXO's HTTP entry. Load `reference/watsonx-orchestrate-integration.md` for the 3-approach decision tree.

---

## Choke Point 1 — Input (before retrieval / LLM)

**Purpose:** catch malicious or out-of-policy inputs before any expensive work.

**Recommended metrics:**
- Category: `safety`
- Category: `pattern` (with `params={"keywords": [...]}` or `{"pattern": "..."}`)
- Metric: `Prompt Safety Risk` (if `system_prompt` available)
- Metric: `Topic Relevance` (if `system_prompt` available)

**Required fields:** `input_text` + optionally `system_prompt` + optionally `params`

**On Block:** refuse with `fallback_message`. Do NOT call retriever or LLM.

**On Flag:** allow through; audit log records borderline state.

**Example:**
```python
bundle = ev.evaluate(
    input_text=user_query,
    categories=["safety", "pattern"],
    params={"keywords": partner_block_list},
)
if bundle.failed():
    return bundle.failed()[0].fallback_message
```

---

## Choke Point 2 — Retrieval (after retrieve, before LLM)

**Purpose:** catch retrieval failures cheaply before paying for an LLM call on bad context.

**Recommended metrics:** category `rag_retrieval` (Retrieval Precision, Hit Rate, Reciprocal Rank)

**Required fields:** `input_text` + `context` (MUST be `list[str]`, one entry per retrieved doc — RULE 6)

**On Block:** skip the LLM. Return "no relevant info."

**On Flag:** allow LLM call but log low-confidence retrieval for analysis.

**Example:**
```python
docs = vector_store.retrieve(user_query, k=5)   # list[str]
bundle = ev.evaluate(
    input_text=user_query,
    context=docs,
    categories=["rag_retrieval"],
)
if bundle.failed():
    return "I don't have enough relevant information to answer that."
```

**GOTCHA:** `context` MUST be `list[str]` here, NOT a single string. Single-string context makes HitRate trivially 0 or 1.

---

## Choke Point 3 — Generation (after LLM)

**Purpose:** catch hallucinations and off-topic answers.

**Recommended metrics:** category `rag_generation` (Answer Relevance, Context Relevance, Faithfulness)

**Required fields:** `input_text` + `generated_text` + `context` (single **string** here — the chunks the LLM saw)

**On Block:** regenerate once with a stricter prompt; if it blocks again, fall back to refusal.

**Example:**
```python
best_context = "\n\n".join(docs[:3])
answer = llm.generate(user_query, context=best_context)
bundle = ev.evaluate(
    input_text=user_query,
    generated_text=answer,
    context=best_context,
    categories=["rag_generation"],
)
```

---

## Choke Point 4 — Output (before serving)

**Purpose:** final safety + quality gate on what the user actually sees.

**Recommended metrics:**
- Output PII Detection (catches LLM-generated PII leaks)
- Output HAP Detection (toxic output)
- Harm, Profanity, Social Bias, Violence, Unethical Behavior (same names as Choke Point 1 — wrapper auto-routes to `generated_text`)
- Conciseness, Text Grade Level, Text Reading Ease (optional quality)

**Required fields:** `generated_text` (safety metrics run output-side).

**About metric naming:** two patterns at Choke Point 4 — see `reference/metrics-catalog.md` "Field routing for single-field safety metrics" for the full rules.
- **PII and HAP** ship as input/output pairs in the underlying SDK. Use the explicit `Output PII Detection` / `Output HAP Detection` names for output-side scanning. The un-prefixed names route to input-only SDK classes.
- **The other 8 safety metrics** (Harm, Social Bias, Jailbreak, Violence, Profanity, Unethical Behavior, Sexual Content, Evasiveness) auto-route based on which field you populate. Use the same metric name regardless of choke point.

**On Block:** scrub the offending span or regenerate.

**Example:**
```python
bundle = ev.evaluate(
    generated_text=answer,
    metrics=["Output PII Detection", "Output HAP Detection",
             "Harm", "Profanity", "Social Bias",
             "Conciseness (LLM Judge)"],
)
if bundle.failed():
    return bundle.failed()[0].fallback_message
```

---

## Integration Reference — Python library

**When:** agent is a Python service and can pip-install into the same process.

**Full example:** `examples/full_pipeline.py`

**One-class summary:**
```python
from real_time_guardrails import GuardrailsEvaluator, AuditLogger
from examples.full_pipeline import GuardrailedAgent

ev = GuardrailsEvaluator()
audit = AuditLogger(path="audit.jsonl")
agent = GuardrailedAgent(ev, audit=audit,
                        retrieve_callback=my_retriever,
                        model_callback=my_llm)
result = agent.process_request(user_query, request_id="req-42")
return result.final_response
```

---

## Integration Reference — REST API

**When:** agent is in another language (Node, Go, Java) or another service.

**Deploy:** `real-time-guardrails serve --port 8090` next to the agent. Co-locate in same VPC for latency.

**Example client call:**
```javascript
const GUARD = "http://your-guardrails-host:8090";
async function check(payload, stage) {
  const r = await fetch(`${GUARD}/api/evaluate`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  const data = await r.json();
  if (data.overall_action === "Block") {
    throw new GuardrailBlock(stage, data);
  }
  return data;
}
```

**Request shape:**
```
POST /api/evaluate
{
  "input_text": "...",
  "generated_text": "...",                       // optional
  "context": "..." or [...],                     // string for RAG-gen, list for RAG-retr
  "system_prompt": "...",                        // optional
  "tool_calls": [{...}],                         // optional, OpenAI format (RULE 5)
  "available_tools": [{...}],                    // optional
  "params": {...},                               // optional, for Pattern metrics
  "metrics": ["..."],                            // OR
  "categories": ["..."],                         // OR omit both for auto-select
  "thresholds": {"metric": 0.5},                 // optional block override
  "flag_thresholds": {"metric": 0.3},            // optional flag override
  "fallback_messages": {"metric": "..."},        // optional override
  "interaction_id": "req-42"
}
```

**Response shape:**
```
{
  "status": "success",
  "interaction_id": "req-42",
  "overall_action": "Block" | "Flag" | "Pass",
  "metrics_evaluated": [...],
  "results": {
    "PII Detection": {
      "score": 0.87, "passed": false, "action": "Block",
      "threshold": 0.65, "flag_threshold": 0.4,
      "fallback_message": "Your request couldn't be processed...",
      "column": "pii", "category": "safety"
    }
  },
  "input": { /* echoed input */ },
  "timestamp": "2026-05-18T..."
}
```

**Sample payloads per choke point:** see `examples/input_safety.json`, `examples/rag_generation.json`, `examples/rag_retrieval.json`, `examples/pattern_keywords.json`, `examples/tool_call.json`.

---

## Integration Reference — MCP tool

**When:** agent is built on MCP and consumes guardrails as a tool.

**Deploy:** add to MCP client config (format varies per client — chat tools, IDE extensions, agent frameworks). The block to add:

```json
{
  "mcpServers": {
    "real-time-guardrails": {
      "command": "real-time-guardrails",
      "args": ["mcp"],
      "env": {
        "WATSONX_APIKEY": "...",
        "WXG_SERVICE_INSTANCE_ID": "...",
        "WXG_PROJECT_ID": "..."
      }
    }
  }
}
```

**Available MCP tools:**
- `evaluate(...)` — generic, accepts any field
- `evaluate_safety(text, role="input")`
- `evaluate_prompt_safety(input_text, system_prompt)`
- `evaluate_rag_generation(input_text, generated_text, context)`
- `evaluate_rag_retrieval(input_text, contexts)`
- `evaluate_quality(input_text, generated_text)`
- `evaluate_pattern(input_text, keywords=None, pattern=None)`
- `evaluate_tool_call(input_text, tool_calls, available_tools=None)`
- `list_metrics()`

---

## Parallelization

**When:** latency optimization for Python library users.

Stages 1 (input safety) and 2 (retrieval) are independent — fire retrieval while the input check is in-flight, await both before the LLM call:

```python
import asyncio
input_task = asyncio.create_task(asyncio.to_thread(
    ev.evaluate, input_text=query, categories=["safety"]))
docs = await my_async_retriever(query)
input_bundle = await input_task
if input_bundle.failed():
    return input_bundle.failed()[0].fallback_message
```

---

## Tool-call payload format (CRITICAL — RULE 5)

**RULE:** OpenAI function-calling format ONLY. Flat dicts are rejected by ToolSpec validation.

**CORRECT:**
```python
tool_calls = [
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": '{"city": "Tokyo"}'  # JSON string
    }
  }
]
available_tools = [
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get weather for a city",
      "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
      }
    }
  }
]
```

**WRONG (rejected):**
```python
tool_calls = [{"name": "get_weather", "arguments": {"city": "Tokyo"}}]
```
