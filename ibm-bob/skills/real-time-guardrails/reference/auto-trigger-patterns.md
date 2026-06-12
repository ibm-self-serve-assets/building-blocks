# Auto-Trigger Patterns

**TRIGGER:** Load when partner says "I want to add guardrails without modifying every endpoint", asks about HTTP middleware vs Python decorator vs framework callback, asks about pre-hook vs post-hook semantics, fail-open vs fail-closed, or about why stock LangChain callbacks can't block outputs.

---

## Three patterns

1. **HTTP middleware** — for polyglot agents behind HTTP
2. **Python decorator** — for monolithic Python agents
3. **Framework callback** — for LangChain / LangGraph / similar

None require changes to the SDK. All are consumer patterns built on the existing `evaluate()` API.

---

## DECISION tree

**Q:** What language is the agent's request handler in?

- **Not Python (Node, Go, Java, etc.)** → middleware
- **Python, monolithic function** → decorator
- **Python, built on LangChain / LangGraph** → framework callback
- **Python, plain Flask/FastAPI with N endpoints** → middleware
- **Mix of services in a mesh** → middleware (at the gateway)

---

## Pre-hook vs post-hook (CRITICAL)

Every pattern has TWO attach points. Partners get confused about how output-blocking works with auto-trigger — address head-on.

### Pre-hook
- **When:** fires BEFORE the agent runs
- **On Block:** skip agent entirely. Return fallback message directly.
- **Cost:** cheap — 1 guardrail call, no LLM cost incurred

### Post-hook
- **When:** fires AFTER the agent has generated output
- **On Block:** replace agent's output with fallback before returning
- **Cost:** expensive — 1+ guardrail calls PLUS one full LLM call you can't refund. LLM cost is sunk regardless of post-check outcome.

**IMPLICATION:** catch what you can at the input stage. Reserve output-stage checks for things ONLY the output can reveal — PII leaks from the LLM, hallucinations vs context, profanity in generated text, RAG faithfulness. Don't duplicate input-side safety on output unless there's a specific reason.

---

## Pattern 1 — HTTP middleware

**Suitability:** most universal. Works for any language with HTTP middleware. Drop-in — agent code is unchanged.

**Pre/post mechanics:** both pre and post live in the SAME middleware function.
- **Pre** = inspect request body BEFORE `call_next(request)`
- **Post** = read response body AFTER `call_next(request)`, evaluate, optionally replace with `JSONResponse(fallback)` on Block.

### FastAPI skeleton
```python
@app.middleware("http")
async def guardrail(request, call_next):
    body = await request.body()
    payload = json.loads(body) if body else {}
    query = payload.get("query", "")

    # === PRE: input check ===
    if query:
        in_bundle = ev.evaluate(input_text=query, categories=["safety"])
        if in_bundle.failed():
            msg = in_bundle.failed()[0].fallback_message
            return JSONResponse({"action": "Block", "text": msg})

    # === Agent runs here ===
    response = await call_next(request)

    # === POST: output check ===
    resp_chunks = [c async for c in response.body_iterator]
    resp_body = b"".join(resp_chunks)
    try:
        resp_json = json.loads(resp_body)
        out_bundle = ev.evaluate(
            input_text=query,
            generated_text=resp_json.get("text", ""),
            metrics=["Output PII Detection", "Output HAP Detection", "Harm", "Profanity"],
        )
        if out_bundle.failed():
            msg = out_bundle.failed()[0].fallback_message
            return JSONResponse({"action": "Block", "text": msg})
    except json.JSONDecodeError:
        pass  # non-JSON response (streaming) — let it through

    return Response(
        content=resp_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )
```

### Flask skeleton
```python
@app.before_request
def _input_check():
    if request.method != "POST":
        return None
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "")
    if not query:
        return None
    bundle = ev.evaluate(input_text=query, categories=["safety"])
    if bundle.failed():
        msg = bundle.failed()[0].fallback_message
        return jsonify({"action": "Block", "text": msg})

@app.after_request
def _output_check(response):
    if response.mimetype != "application/json":
        return response
    data = response.get_json(silent=True) or {}
    output_text = data.get("text") or data.get("response", "")
    if not output_text:
        return response
    bundle = ev.evaluate(
        generated_text=output_text,
        metrics=["Output PII Detection", "Output HAP Detection", "Harm", "Profanity"],
    )
    if bundle.failed():
        msg = bundle.failed()[0].fallback_message
        response.set_data(json.dumps({"action": "Block", "text": msg}))
    return response
```

**Reference:** `examples/middleware_fastapi.py`, `examples/middleware_flask.py`.

---

## Pattern 2 — Python decorator

**Suitability:** cleanest retrofit for monolithic Python agents. Wraps a single function — agent code is unchanged except for the `@guard` line.

**Pre/post mechanics:** decorator wraps the function.
- **Pre** = run BEFORE wrapped function call. On Block, return fallback WITHOUT invoking function.
- **Post** = run AFTER wrapped function returns. On Block, substitute fallback for returned value.

**Signature:**
```python
@guard(evaluator=ev,
       input_categories=["safety"],
       output_metrics=["Output PII Detection", "Output HAP Detection", "Harm", "Profanity"])
def handle_user_query(query: str) -> str:
    return llm.generate(query)
```

**Reference:** `examples/decorator_example.py` — self-contained ~100 lines partners copy into their codebase.

**Note:** The decorator is intentionally a skill reference, NOT an SDK feature. Partners copy + adapt. Revisit shipping in the SDK if 2+ partners request it.

---

## Pattern 3 — Framework callback (LangChain / LangGraph)

**Suitability:** for agents built on LangChain / LangGraph / similar frameworks. Hooks into the framework's existing callback system.

### CRITICAL ASYMMETRY
- **Pre:** `on_chain_start` callback fires with chain inputs. Raising an exception aborts the chain — partner catches and converts to a Block response. **Clean pattern.**
- **Post:** STOCK LANGCHAIN CALLBACKS ARE OBSERVATIONAL — they can't replace outputs. **Workaround:** wrap the chain in a `RunnableLambda` post-processor that re-evaluates the result and substitutes the fallback. This is the canonical LangChain pattern for output guardrails. Document the asymmetry so partners aren't surprised.

### Example
```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import RunnableLambda

class GuardrailsInputCallback(BaseCallbackHandler):
    def __init__(self, evaluator, categories):
        self.ev = evaluator; self.cats = categories
    def on_chain_start(self, serialized, inputs, **kwargs):
        query = inputs.get("query") or inputs.get("input", "")
        bundle = self.ev.evaluate(input_text=query, categories=self.cats)
        if bundle.failed():
            raise RuntimeError(
                f"Guardrails blocked: {bundle.failed()[0].fallback_message}"
            )

def output_guard(evaluator, metrics):
    def _check(result):
        text = result["output"] if isinstance(result, dict) else str(result)
        bundle = evaluator.evaluate(generated_text=text, metrics=metrics)
        if bundle.failed():
            return {"output": bundle.failed()[0].fallback_message, "guardrail_blocked": True}
        return result
    return RunnableLambda(_check)

# Usage:
guarded_chain = my_chain | output_guard(ev, ["Output PII Detection", "Output HAP Detection"])
result = guarded_chain.invoke(
    {"query": user_q},
    config={"callbacks": [GuardrailsInputCallback(ev, ["safety"])]},
)
```

**Reference:** `examples/langchain_callback.py`.

---

## 4 choke points → pre/post mapping

| Choke point | Hook | Fits in |
|---|---|---|
| 1 — Input safety | pre | all 3 patterns |
| 2 — Retrieval quality | between retrieve and LLM-call | LangChain framework callback (`on_retriever_end`); middleware can't insert here without code structure cooperation |
| 3 — Generation faithfulness | post | all 3 patterns |
| 4 — Output safety | post | all 3 patterns |

**Note:** auto-trigger can't automatically insert choke point 2 unless the agent's code is split into retrieval + generation phases. LangChain handles this naturally because it has separate Runnables for retrieval and LLM call. Monolithic Python agents need explicit wiring for retrieval-stage checks.

---

## Stateless requirement (CRITICAL — RULE 16)

**RULE:** Build `GuardrailsEvaluator` ONCE at app/worker startup. Share across requests. NEVER instantiate per-request.

**Reason:** registry build does ~28 SDK object constructions plus an LLMJudge build (network-y on first use). Per-request instantiation adds ~1-3 s overhead per request — defeats the purpose of auto-trigger.

---

## Failure mode policy

What happens when guardrails service is degraded (timeout, 5xx)?

| Policy | Semantics | Use when |
|---|---|---|
| **fail_open** | Allow request to pass when guardrails fails. Log the failure for ops review. | Availability > safety enforcement (internal tooling, low-stakes use cases) |
| **fail_closed** | Refuse request when guardrails fails. Return generic "service unavailable" message. | Compliance/safety non-negotiable (regulated industries, customer-facing high-stakes content) |

**Implementation:** wrap `ev.evaluate()` in try/except. On exception, apply partner's chosen policy. Consistent across all three trigger patterns.

---

## Anti-patterns

- Building an evaluator per request (cold-start cost is several seconds)
- Running LLM-judge metrics on every request without sampling (token cost blows up)
- Putting output-stage RAG metrics in input-stage middleware (impossible — output doesn't exist yet)
- Trying to block output via stock LangChain callbacks (won't work — use `RunnableLambda` wrapping)
- Mixing trigger patterns in the same agent (RULE 17 — pick ONE)
