# Custom Metric Authoring

**TRIGGER:** Load when partner says "I need a guardrail for X and it's not in the catalog", asks about custom LLM-as-judge metrics, the `prompt_template` vs `criteria + Option` styles, replacing built-in LLM-judge metrics (Answer Completeness, Conciseness, Tool Call Relevance), or registry registration patterns.

---

## Decision — when to author custom

### Use existing if:
- Concern is already covered by one of the 28 catalog metrics. Tuning the threshold is usually enough.
- Judgment is binary "safe vs unsafe" → Granite Guardian's safety metrics handle this better than a custom judge.
- Criterion can be expressed as a regex or keyword list → use `KeywordDetection` / `RegexDetection` instead.

### Author custom if:
- Judgment is domain-specific: "does this answer correctly cite our internal policy?" "does this response use the partner's brand voice?"
- Criterion is a multi-level rubric: High/Medium/Low or complete/partial/incomplete.
- Partner has tried tuning catalog metrics and they're still missing the target behavior.

---

## Two authoring styles

### Style A — `prompt_template` (full control)
**When:** you need to inject custom context, multi-turn examples, or carefully crafted instructions. Comfortable maintaining a prompt template.

```python
from ibm_watsonx_gov.metrics import LLMAsJudgeMetric

my_metric = LLMAsJudgeMetric(
    name="contract_clause_correctness",
    llm_judge=judge,
    prompt_template="""
        You are evaluating whether an AI response correctly cites the
        relevant contract clause.

        Question: {input_text}
        AI Response: {generated_text}
        Reference Contract: {context}

        Return: correct / partially_correct / incorrect
    """,
    input_fields=["input_text", "generated_text", "context"],
    options={"correct": 1, "partially_correct": 0.5, "incorrect": 0},
)
```

**Existing examples in SDK:** `build_answer_completeness`, `build_conciseness` (in `core/custom_metrics.py`).

### Style B — `criteria_description + Option` (SDK auto-generates prompt)
**When:** judgment is a short Y/N or 3-tier rubric. You don't want to maintain a full prompt.

```python
from ibm_watsonx_gov.entities.criteria import Option
from real_time_guardrails.core.custom_metrics import build_criteria_judge

my_metric = build_criteria_judge(
    name="brand_voice",
    display_name="Brand Voice",
    criteria_description="Does the {generated_text} match our brand voice (professional, concise, warm)?",
    options=[
        Option(name="Yes", description="On-brand: professional, concise, warm.", value=1.0),
        Option(name="No", description="Off-brand.", value=0.0),
    ],
    judge=judge,
)
```

**Helper:** `build_criteria_judge()` in `core/custom_metrics.py` — wraps `LLMAsJudgeMetric` for the criteria style.

### Side-by-side

| Aspect | prompt_template | criteria + Option |
|---|---|---|
| Prompt authoring | You write it | SDK generates it |
| Best for | Complex judgments needing examples or context shaping | Short rubrics: Yes/No, High/Medium/Low |
| Lines of code | ~15-25 | ~8-12 |
| Latency | Same (1 LLM call) | Same (1 LLM call) |
| Maintenance burden | Higher (prompt is a long string) | Lower (just Options + 1-line criteria) |
| **RECOMMENDED starting point** | If criteria-style doesn't fit | **Default — try this first** |

---

## Registration in the registry

For a custom metric to be callable via `ev.evaluate(metrics=["My Custom Metric"])`, it must be in the MetricRegistry. The registry is built once at evaluator init from `build_registry(config)` in `core/metrics.py`.

### Option A — post-init registration (RECOMMENDED for partners)
Simplest. Append to `ev.registry` after construction. No need to fork the package.

```python
from real_time_guardrails import GuardrailsEvaluator
from real_time_guardrails.core.registry import MetricEntry
from real_time_guardrails.core.thresholds import ThresholdSpec, Direction

ev = GuardrailsEvaluator()

my_metric_entry = MetricEntry(
    name="Brand Voice",
    metric=my_metric,                # built via build_criteria_judge() above
    category="quality",
    column_name="brand_voice.llm_as_judge",
    threshold_spec=ThresholdSpec(value=0.5, direction=Direction.LOW_IS_RISK, flag_value=0.7),
    required_fields=frozenset({"generated_text"}),
    description="Custom rubric: on-brand vs off-brand response check.",
)
ev.registry._by_name[my_metric_entry.name] = my_metric_entry
# Re-attach known_metrics so threshold resolver sees the new metric:
ev._threshold_resolver.attach_known_metrics(set(ev.registry.names))

bundle = ev.evaluate(generated_text="...", metrics=["Brand Voice"])
```

### Option B — patch `build_registry` (for forks)
For partners who fork the SDK: add the entry directly to `build_registry()` in `core/metrics.py` alongside the 28 catalog metrics.

---

## Caveats

**Judge model selection:**
- Default: `llama-3-3-70b-instruct` on watsonx.ai
- Override via env var `WXG_JUDGE_MODEL_ID`, OR build the `LLMJudge` directly with a different `WxAIFoundationModel(model_id=...)`
- For simple Yes/No rubrics, smaller models (`granite-3-8b-instruct`) work and cost less. For nuanced multi-tier judgments, stick with 70B+.

**Latency cost:** every LLM-judge invocation is a synchronous watsonx.ai call — 1-3 seconds + token cost. For high-volume traffic, sample (e.g. evaluate every 10th request).

**Token cost:** Llama-3.3-70B uses ~200-500 input + ~10 output tokens per call. At watsonx.ai per-token pricing, sustained traffic adds up quickly. Monitor via `WXG_PROJECT_ID`'s usage dashboard.

**Determinism:** LLM judges are NOT perfectly deterministic. Same input may produce slightly different scores across calls. For high-stakes decisions, use binary Yes/No rubric (less score variance) and set thresholds conservatively.

**Prompt injection in inputs:** the LLM judge sees `input_text` + `generated_text` etc. as part of its prompt. Adversarial inputs can attempt to manipulate the judge. **Mitigation:** run safety guardrails (Jailbreak Detection) BEFORE the custom judge fires.

---

## Replacing built-in LLM-judge metrics

The SDK ships 3 LLM-as-judge metrics with OPINIONATED PROMPTS:
- Answer Completeness (LLM Judge) — our prompt in `core/custom_metrics.py`
- Conciseness (LLM Judge) — our prompt in `core/custom_metrics.py`
- Tool Call Relevance — gov SDK's built-in prompt

Partners may want different rubrics (brand voice, stricter compliance, multi-language). Same authoring pattern works for REPLACEMENT as for new metrics: build a new `LLMAsJudgeMetric` (either style) and register it under the SAME NAME so it overrides the catalog entry.

```python
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
from ibm_watsonx_gov.entities.llm_judge import LLMJudge

ev = GuardrailsEvaluator()

# 1. Build replacement metric — same display name as the built-in.
judge = LLMJudge(model=WxAIFoundationModel(
    model_id="llama-3-3-70b-instruct",
    project_id=ev._config.project_id,
))
partner_completeness = build_criteria_judge(
    name="answer_completeness",
    display_name="Answer Completeness (LLM Judge)",  # SAME display name
    criteria_description=(
        "Does the {generated_text} cite a specific section "
        "of our compliance policy (e.g., 'per Section 4.2')?"
    ),
    options=[
        Option(name="Yes", description="Cites a section.", value=1.0),
        Option(name="No", description="Generic answer without citation.", value=0.0),
    ],
    judge=judge,
)

# 2. Override the catalog entry by same display name.
ev.registry._by_name["Answer Completeness (LLM Judge)"] = MetricEntry(
    name="Answer Completeness (LLM Judge)",
    metric=partner_completeness,
    category="quality",
    column_name="answer_completeness.llm_as_judge",  # same column
    threshold_spec=ThresholdSpec(value=0.5, direction=Direction.LOW_IS_RISK),
    required_fields=frozenset({"input_text", "generated_text"}),
    description="(partner override) Compliance citation check.",
)

# 3. Now ev.evaluate(metrics=["Answer Completeness (LLM Judge)"]) uses partner's prompt.
```

### Skip built-in judges entirely
**How:** don't set `WXG_PROJECT_ID`. The registry omits all 3 LLM-judge metrics. Partner gets 25 of 28 metrics.

**When:** partner doesn't want token cost or non-determinism. Common for high-volume / low-margin deployments.

---

## When to advise AGAINST custom authoring

- Partner wants a custom safety check that overlaps with existing safety metrics (HAP / Harm / SocialBias) → recommend tuning thresholds on existing metrics instead.
- Partner wants determinism / 100% reproducibility → LLM judges can't deliver this. Recommend rule-based or regex-based custom checks via the Pattern category.
- Partner needs to enforce schema or structured output → that's a JSON validation problem, not a guardrails problem. Recommend pydantic / json-schema validation before calling our SDK.

---

## Reference

`examples/custom_metric_example.py` — working example with both styles + post-init registration.
