# Under the Hood — `real-time-guardrails` vs `ibm-watsonx-gov`

`real-time-guardrails` is a thin, opinionated wrapper over IBM's
[`ibm-watsonx-gov`](https://pypi.org/project/ibm-watsonx-gov/) SDK. It adds
production patterns (3-state action model, audit log, threshold layers,
multi-interface) but the underlying API calls go through the gov SDK
unchanged.

This doc shows side-by-side comparisons so you understand what our wrapper
is doing on your behalf. Useful when:

- You're debugging why a metric scored a certain way and want to see the raw
  SDK call.
- You need a metric or capability we don't expose (e.g. batch evaluation,
  some non-reference-free metrics).
- You're migrating an existing `ibm-watsonx-gov` integration to our SDK.

> **Heads up**: you can mix both SDKs in the same process. Our wrapper
> exposes the underlying gov SDK objects via `evaluator._sdk_evaluator` and
> `evaluator.registry` if you ever need to drop down without leaving our
> framework.

---

## 1. Initializing the evaluator

```python
# Our SDK
from real_time_guardrails import GuardrailsEvaluator
ev = GuardrailsEvaluator()   # reads WATSONX_APIKEY, WXG_SERVICE_INSTANCE_ID,
                              # WXG_PROJECT_ID from env; builds the 28-metric
                              # registry and an LLMJudge automatically

# ibm-watsonx-gov direct equivalent
import os
from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
from ibm_watsonx_gov.entities.llm_judge import LLMJudge

os.environ["WATSONX_APIKEY"] = "..."
os.environ["WXG_SERVICE_INSTANCE_ID"] = "..."
sdk_evaluator = MetricsEvaluator()
judge = LLMJudge(model=WxAIFoundationModel(
    model_id="llama-3-3-70b-instruct",
    project_id="...",
))
# You then have to instantiate each metric class individually and
# pass them per evaluate() call — there's no registry.
```

**What our SDK adds**: env-var loading with clear errors, the 28-metric
registry built once at init, the LLMJudge built once and shared.

---

## 2. Running a safety check on input

```python
# Our SDK
bundle = ev.evaluate(input_text="My SSN is 123-45-6789",
                     metrics=["PII Detection", "Jailbreak Detection"])
r = bundle["PII Detection"]
print(r.score, r.action, r.threshold)
```

```python
# ibm-watsonx-gov direct equivalent
import pandas as pd
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.metrics import PIIMetric, JailbreakMetric

config = GenAIConfiguration(input_fields=["input_text"],
                            output_fields=["generated_text"])
df = pd.DataFrame([{"input_text": "My SSN is 123-45-6789",
                    "generated_text": ""}])
evaluator = MetricsEvaluator(configuration=config)
result = evaluator.evaluate(data=df, metrics=[PIIMetric(value=0.5),
                                              JailbreakMetric()])
# Find the score in result.metrics_result by metric.name; apply your own
# threshold logic (e.g. score >= 0.65 → block); pick a fallback message.
```

**What our SDK adds**: list-wrapping normalization (every field consistently
wrapped), automatic threshold lookup from the registry, 3-state Pass / Flag /
Block action via `r.action`, default fallback message via `r.fallback_message`.

---

## 3. RAG retrieval ranking (multi-doc context)

```python
# Our SDK
bundle = ev.evaluate(input_text="What is RAG?",
                     context=["doc 1", "doc 2", "doc 3"],   # LIST
                     categories=["rag_retrieval"])
```

```python
# ibm-watsonx-gov direct equivalent
from ibm_watsonx_gov.metrics import (
    HitRateMetric, RetrievalPrecisionMetric, ReciprocalRankMetric,
)
df = pd.DataFrame([{"input_text": "What is RAG?",
                    "context": [["doc 1", "doc 2", "doc 3"]]}])
# Note the nested list — context column is a list[str] per row,
# wrapped in another list for the DataFrame column.
result = evaluator.evaluate(data=df, metrics=[
    HitRateMetric(), RetrievalPrecisionMetric(), ReciprocalRankMetric(),
])
```

**What our SDK adds**: handles the list-wrapping quirk for you (the gov SDK
expects nested lists for `context` but not for `input_text`, which is easy
to get wrong).

---

## 4. Custom LLM-as-judge metric (criteria style)

```python
# Our SDK
from real_time_guardrails.core.custom_metrics import build_criteria_judge
from ibm_watsonx_gov.entities.criteria import Option

brand_voice = build_criteria_judge(
    name="brand_voice", display_name="Brand Voice",
    criteria_description="Does the {generated_text} match our brand voice?",
    options=[
        Option(name="Yes", description="On-brand.", value=1.0),
        Option(name="No", description="Off-brand.", value=0.0),
    ],
    judge=ev._llm_judge,   # access the shared judge
)
# Then register in the evaluator's registry — see 03_custom_guardrails.py
```

```python
# ibm-watsonx-gov direct equivalent
from ibm_watsonx_gov.metrics import LLMAsJudgeMetric
from ibm_watsonx_gov.entities.criteria import Option

brand_voice = LLMAsJudgeMetric(
    name="brand_voice", display_name="Brand Voice",
    criteria_description="Does the {generated_text} match our brand voice?",
    options=[
        Option(name="Yes", description="On-brand.", value=1.0),
        Option(name="No", description="Off-brand.", value=0.0),
    ],
    output_field="generated_text",
    llm_judge=judge,
)
# Then pass directly to evaluator.evaluate(data=df, metrics=[brand_voice, ...])
# (no registry to register into).
```

**What our SDK adds**: minimal wrapper (`build_criteria_judge`) so the call
site is shorter; standard registration pattern so the metric works with
`ev.evaluate(metrics=["Brand Voice"])` by name.

---

## 5. Threshold overrides — the 5 layers

This is the biggest delta. Our SDK has a **5-layer override system**
(per-call → constructor → YAML config file → env var → default). The raw
gov SDK has none of this — partners hand-roll per-deployment logic.

```python
# Our SDK — 5 ways to express "PII Detection should block at 0.7":

# Layer 1 — per-call
ev.evaluate(..., thresholds={"PII Detection": 0.7})

# Layer 2 — constructor
ev = GuardrailsEvaluator(threshold_overrides={"PII Detection": 0.7})

# Layer 3 — YAML config file
# (config_path="thresholds.yaml" with `metrics: {"PII Detection": 0.7}`)

# Layer 4 — env var
# GUARDRAILS_THRESHOLD_PII_DETECTION=0.7

# Layer 5 — package default (0.65)
```

```python
# ibm-watsonx-gov direct — there's no built-in override layer.
# Partners typically write their own policy dict:

GUARDRAIL_POLICY = {"pii": {"block": 0.7, "flag": 0.5}, ...}
# Then iterate over result.metrics_result, look up policy, apply manually.
```

**What our SDK adds**: declarative threshold management with clear precedence,
which matters for multi-tenant deployments where per-partner policies differ.

---

## 6. Audit logging

```python
# Our SDK
from real_time_guardrails import AuditLogger
audit = AuditLogger(path="/var/log/guardrails/audit.jsonl")
audit.record(bundle, input_payload={"query": q}, request_id="req-42")
```

```python
# ibm-watsonx-gov direct — no built-in audit; partners roll their own.
# Typical pattern:
import json, datetime
def write_audit(result, input_payload, request_id):
    record = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "request_id": request_id,
        "input": input_payload,
        "metrics": {m.name: {"score": m.mean} for m in result.metrics_result},
    }
    with open("/var/log/guardrails/audit.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
```

**What our SDK adds**: structured records with per-metric scores + actions +
thresholds, stable input hashes for join keys, pluggable sinks (file/Splunk/ELK),
optional `include_inputs=False` for PII-sensitive deployments.

---

## When to drop down to raw `ibm-watsonx-gov` directly

You don't need to drop down for the common case. But there are legitimate
reasons:

- **You need a metric we don't expose**: ground-truth-requiring metrics
  (AnswerSimilarity, ToolCallParameterAccuracy, LLMValidation), batch-only
  ranking metrics (AveragePrecision, NDCG), observability metrics (Cost,
  Duration, TokenCount, Status, UserId), or any newer metric IBM ships in a
  gov SDK release we haven't synced yet.
- **You need batch evaluation**: our SDK is request-scoped. For evaluating
  large historical datasets in one call, use `MetricsEvaluator.evaluate()`
  with a multi-row DataFrame directly.
- **You're integrating with IBM's own dashboards / OpenScale UI**, which
  expects the canonical SDK's data shape.
- **You're debugging a scoring quirk** and want to bypass our wrapper to
  confirm the score comes from the gov SDK and not our processing.

You can mix freely — `ev._sdk_evaluator` is the underlying `MetricsEvaluator`
instance if you ever want to call it directly without leaving our SDK's
context.

## The version contract

We pin `ibm-watsonx-gov>=1.4.0,<1.5.0`. When IBM ships 1.5, our SDK is
intentionally one version behind for a short window while we verify the
upgrade. If you need 1.5 features immediately, pin both SDKs in your project
and use the raw gov SDK for the new functionality alongside our wrapper for
the rest.
