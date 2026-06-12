# Metrics Catalog and Thresholds

**TRIGGER:** Load when user is in Phase 2 (Design) or Phase 4 (Tuning), asks about a specific metric, asks "what metrics will run with my data?", asks about threshold mechanics, the 5-layer override model, per-partner policy, or sees `MissingFieldError`.

---

## Categories at a glance

| Category | Count | Direction | Default Block | Default Flag |
|---|---|---|---|---|
| safety | 12 | HIGH_IS_RISK | 0.65 | 0.4 |
| rag_generation | 3 | LOW_IS_RISK | 0.1 | 0.3 |
| rag_retrieval | 3 | LOW_IS_RISK | 0.1 | 0.3 |
| quality | 5 | LOW_IS_RISK | 0.1 | 0.3 |
| topic | 1 | LOW_IS_RISK | 0.1 | 0.3 |
| pattern | 2 | HIGH_IS_RISK | 0.5 | None (binary) |
| tool_call | 2 | LOW_IS_RISK | 0.1 | 0.3 |

**Total: 28 metrics** (25 if `WXG_PROJECT_ID` is unset — 3 LLM-judge dropped).

---

## Category: `safety` (14 metrics)

**Score:** model confidence that content IS risky — higher = more risky.

| Name | Column | Fields scanned |
|---|---|---|
| HAP (Hate, Abuse, Profanity) | hap | `input_text` ONLY |
| **Output HAP Detection** | output_hap | **`generated_text` ONLY** |
| PII Detection | pii | `input_text` ONLY |
| **Output PII Detection** | output_pii | **`generated_text` ONLY** |
| Harm | harm.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Social Bias | social_bias.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Jailbreak Detection | jailbreak.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Violence | violence.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Profanity | profanity.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Unethical Behavior | unethical_behavior.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Sexual Content | sexual_content.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Evasiveness | evasiveness.granite_guardian | `input_text` OR `generated_text` (auto-routed) |
| Harm Engagement | harm_engagement.granite_guardian | `input_text` ONLY |
| Prompt Safety Risk | prompt_safety_risk.granite_guardian | `input_text` + `system_prompt` |

### Field routing for single-field safety metrics

**PII Detection and HAP — explicit input vs output names.** The underlying SDK ships separate classes for input-side (`PIIMetric`, `HAPMetric`) and output-side (`OutputPIIMetric`, `OutputHAPMetric`) scanning. The wrapper registers each pair under explicit names. To scan PII or HAP in output text, use `Output PII Detection` / `Output HAP Detection` — the un-prefixed names route exclusively to the input-scanning SDK classes.

**The other 8 single-field safety metrics — same name, auto-routed.** For Harm, Social Bias, Jailbreak Detection, Violence, Profanity, Unethical Behavior, Sexual Content, and Evasiveness, the wrapper detects which field the partner populated and points the metric at it. The same metric name works at any choke point:

```python
# Input scanning (Choke Point 1)
ev.evaluate(input_text=user_query, metrics=["Harm", "Jailbreak Detection"])
# → bundle.results["Harm"], bundle.results["Jailbreak Detection"]

# Output scanning (Choke Point 4) — SAME name, no prefix needed
ev.evaluate(generated_text=model_answer, metrics=["Harm", "Profanity"])
# → bundle.results["Harm"], bundle.results["Profanity"]
```

**Both fields populated → results have suffixed keys.** When the partner passes BOTH `input_text` and `generated_text` and requests one of these 8 metrics, the wrapper scans both fields and returns two results — `"<metric> (input)"` and `"<metric> (output)"`:

```python
ev.evaluate(input_text=user_query, generated_text=model_answer, metrics=["Harm"])
# → bundle.results = {
#       "Harm (input)":  GuardrailResult(...),
#       "Harm (output)": GuardrailResult(...),
#   }
```

This is intentional: the wrapper does NOT impose a "worst of both" or "scan input only" assumption. Partners see both scores and decide what to do (block on either, take the higher, treat them independently — all valid). Each suffixed result has its own Pass/Flag/Block action via the existing threshold logic, and the audit log records both as separate decisions.

## Category: `rag_generation` (3 metrics)

**Score:** LLM's generated answer against query + context. Low score = risky (hallucination or off-topic).

| Name | Column | Fields |
|---|---|---|
| Answer Relevance | answer_relevance.granite_guardian | `input_text` + `generated_text` + `context` |
| Context Relevance | context_relevance.granite_guardian | `input_text` + `generated_text` + `context` |
| Faithfulness | faithfulness.granite_guardian | `input_text` + `generated_text` + `context` |

## Category: `rag_retrieval` (3 metrics)

**Score:** retriever's output. Built on Context Relevance per doc, aggregated via IR formulas.

| Name | Column | Fields |
|---|---|---|
| Retrieval Precision | retrieval_precision | `input_text` + `context: list[str]` |
| Hit Rate | hit_rate | `input_text` + `context: list[str]` |
| Reciprocal Rank | reciprocal_rank | `input_text` + `context: list[str]` |

**CRITICAL:** `context` MUST be `list[str]`, one entry per retrieved document. Single-string context gives degenerate scores.

## Category: `quality` (5 metrics — 2 LLM-judge, 3 deterministic)

| Name | Column | Fields | LLM-judge? | Requires `WXG_PROJECT_ID`? |
|---|---|---|---|---|
| Answer Completeness (LLM Judge) | answer_completeness.llm_as_judge | `input_text` + `generated_text` | Yes | Yes |
| Conciseness (LLM Judge) | conciseness.llm_as_judge | `generated_text` | Yes | Yes |
| Text Grade Level | text_grade_level.flesch_kincaid_grade | `generated_text` | No | No |
| Text Reading Ease | text_reading_ease.flesch_reading_ease | `generated_text` | No | No |
| Unsuccessful Requests | unsuccessful_requests | `generated_text` | No | No (non-actionable) |

## Category: `topic` (1 metric)

| Name | Column | Fields |
|---|---|---|
| Topic Relevance | topic_relevance | `input_text` + `system_prompt` |

## Category: `pattern` (2 metrics — pure Python, binary scoring)

Score is 1.0 on match, 0.0 on no match. No flag state.

| Name | Column | Fields |
|---|---|---|
| Keyword Detection | keyword | `input_text` + `params={"keywords": [...], "case_sensitive": bool}` |
| Regex Detection | regex | `input_text` + `params={"pattern": "..."}` OR `{"patterns": [...]}` |

## Category: `tool_call` (2 metrics)

| Name | Column | Fields | LLM-judge? |
|---|---|---|---|
| Tool Call Accuracy | tool_call_accuracy.syntactic | `input_text` + `tool_calls` + `available_tools` | No |
| Tool Call Relevance | tool_call_relevance.llm_as_judge | `input_text` + `tool_calls` + `available_tools` | Yes (requires `WXG_PROJECT_ID`) |

**Note:** Tool Call Accuracy returns `None` when there are no syntactic issues. This is treated as Pass.

---

## Threshold override layers (highest precedence wins — RULE 8)

| Level | Name | Code |
|---|---|---|
| 1 | per-call argument | `ev.evaluate(..., thresholds={"PII Detection": 0.7}, flag_thresholds={"PII Detection": 0.5})` |
| 2 | constructor argument | `GuardrailsEvaluator(threshold_overrides={"PII Detection": 0.7})` |
| 3 | YAML config | `GuardrailsEvaluator(config_path="thresholds.yaml")` (auto-discover: `GUARDRAILS_CONFIG_PATH` env var or `./real-time-guardrails.yaml`) |
| 4 | env vars | `GUARDRAILS_THRESHOLD_<METRIC_SLUG>=<float>` or category shortcuts |
| 5 | package defaults | Safety: block=0.65 flag=0.4. RAG: block=0.1 flag=0.3. Pattern: block=0.5 (no flag). Quality: block=0.1 flag=0.3. |

**YAML shape:**
```yaml
defaults:
  safety: 0.6
  rag: 0.15
  quality: 0.1
metrics:
  "PII Detection": 0.7
  "Faithfulness": 0.15
```

## Flag/Block invariants

- **HIGH_IS_RISK:** `flag_value` must be strictly LESS THAN `block` value. Example: flag=0.4, block=0.65.
- **LOW_IS_RISK:** `flag_value` must be strictly GREATER THAN `block` value. Example: block=0.1, flag=0.3.
- **Auto-drop:** when `with_value()` is called with a new block that invalidates the existing flag, the flag auto-drops (set to None). To keep a Flag state at the new block level, also pass `flag_thresholds={metric: new_flag}`.

---

## Selection modes

| Mode | Code | Semantics | When |
|---|---|---|---|
| **explicit_metrics** | `ev.evaluate(..., metrics=["PII Detection", "Faithfulness"])` | Strict — every named metric runs; missing required fields raise `MissingFieldError`. | Production: tight, deliberate metric set per choke point. |
| **categories** | `ev.evaluate(..., categories=["safety", "pattern"])` | Lenient — runs every metric in those categories whose required_fields are satisfied; silently skips others. | Exploratory: "give me everything safety-related I can run with the data I have." |
| **auto_select** | `ev.evaluate(input_text="...")` | Runs every metric in the registry whose required_fields are satisfied. | Quick sanity check. NOT recommended for production (unpredictable cost as catalog grows). |

---

## Field availability matrix (RULE 18)

Most partners don't have all 7 input fields. Tell them up-front exactly which metrics will run given their data shape. This matrix maps common shapes to the metric subset. Use during Phase 2 (Design) BEFORE any code is written.

**Key:** `WXG_PROJECT_ID` status also matters: without it, ALL 3 LLM-judge metrics (Answer Completeness, Conciseness, Tool Call Relevance) are omitted regardless of fields. Counts below assume `WXG_PROJECT_ID` IS set.

| Shape | Fields | Runs | Typical use |
|---|---|---|---|
| **input-text-only** | `input_text` | 11 (10 generic safety + Harm Engagement) | Input-safety-only deployments (chat moderation, prompt filtering) |
| **input + system-prompt** | `input_text` + `system_prompt` | 13 (11 + Prompt Safety Risk + Topic Relevance) | System-prompt-aware input safety (catch off-topic, prompt-injection) |
| **input + output** | `input_text` + `generated_text` | ~13-16 (generics + Answer Completeness + 3 output-only quality) | Non-RAG agent (single-shot LLM call without retrieval) |
| **input + output + context (str)** | `input_text` + `generated_text` + `context` (str) | 16 (above + 3 RAG generation) | RAG agent caring about generation quality, not retrieval |
| **input + context (list)** | `input_text` + `context` (list[str]) | 14 (11 input-safety + 3 RAG retrieval) | Pre-LLM retrieval guardrail — skip LLM if HitRate=0 |
| **full RAG + system prompt** | `input_text` + `generated_text` + `context` (str) + `system_prompt` | 18 | Full-featured chat-style RAG agent with defined persona |
| **tool-using agent** | `input_text` + `tool_calls` + `available_tools` | 13 (11 input-safety + Tool Call Accuracy + Tool Call Relevance) | Function-calling agent — validate the LLM picked the right tool |
| **compliance blocklist** | `input_text` + `params={"keywords": [...]}` | 12 (11 input-safety + Keyword Detection) | Partners with custom keyword blocklists (competitors, internal codenames, regulated terms) |

**How to inspect at runtime:**
```python
ev = GuardrailsEvaluator()
sample = {"input_text": "...", "generated_text": "...", "context": "..."}
bundle = ev.evaluate(**sample)
print("Will run:", bundle.metrics_evaluated)
# Or:
for entry in ev.registry:
    satisfied = entry.required_fields.issubset(sample.keys())
    print(f"{entry.name}: {'will run' if satisfied else 'SKIPPED — needs ' + str(entry.required_fields)}")
```

---

## Per-partner policy patterns

**Approach 1 — YAML per partner:** keep one YAML per partner (`thresholds.partner-acme.yaml`, `thresholds.partner-globex.yaml`). Switch via `GUARDRAILS_CONFIG_PATH` at deploy time.

**Approach 2 — per-call at runtime:** look up policy in your database; pass `thresholds=` per request:
```python
partner_policy = db.get_policy(partner_id)
bundle = ev.evaluate(
    input_text=query,
    thresholds=partner_policy["block"],
    flag_thresholds=partner_policy["flag"],
    fallback_messages=partner_policy["fallback"],
)
```

**Approach 3 — multiple evaluators:** build N `GuardrailsEvaluator` instances at startup (one per partner) with different `threshold_overrides=`. Look up the right one per request. Trade-off: higher memory; same SDK cost.
