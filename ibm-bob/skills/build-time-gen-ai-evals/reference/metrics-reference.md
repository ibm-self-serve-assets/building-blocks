# Metrics Reference

**TRIGGER:** Load when partner asks about a specific metric, asks "what does X measure", asks for thresholds, asks "what does this score mean", asks about `GenAIConfiguration` field arrays, or needs the complete threshold summary table.

**Naming convention:** the snake_case identifiers below (e.g., `answer_relevance`) map to SDK class names by CamelCase + `Metric` suffix: `AnswerRelevanceMetric`. The SDK reads metric instances, NOT identifier strings — partners pass `[m.AnswerRelevanceMetric(), m.FaithfulnessMetric()]` to `evaluator.evaluate(metrics=...)`, not strings.

---

## RAG quality metrics (tool: `evaluate_rag_quality`)

### `answer_relevance`
- **Plain English:** Does the generated answer actually address the user's question?
- **Technical:** Measures token recall between the answer and the question — how much of the question's vocabulary and intent is reflected in the answer.
- **Threshold:** PASS ≥ 0.70; FAIL < 0.70. **GOOD:** ≥ 0.85. **BAD:** < 0.50 (off-topic or evasive).
- **Common causes of failure:**
  - Model drifting off-topic due to vague question
  - System prompt overriding the intent of the question
  - Retrieval returning irrelevant context that misleads the model
- **Fix actions:**
  - Tighten system prompt: instruct model to directly answer the question
  - Improve question clarity in your test set
  - Review whether retrieved context is actually relevant
- **Required fields:** `question`, `generated_text`
- **Default field names:** `input_field="question"`, `output_field="generated_text"`

### `answer_similarity`
- **Plain English:** How similar is the generated answer to the expected reference answer?
- **Technical:** Semantic similarity between generated answer and a provided reference (ground-truth) answer.
- **Threshold:** PASS ≥ 0.70; FAIL < 0.70. **GOOD:** ≥ 0.85. **BAD:** < 0.50.
- **NOTE:** Requires reference (ground-truth) answers. Skip if you don't have a labeled test set.
- **Common causes of failure:**
  - Model using different phrasing or level of detail than reference
  - Reference answer out of date or from different source
  - Model generating more/less detail than expected
- **Fix actions:**
  - Check if reference answers are actually correct and current
  - Adjust system prompt to match expected response style
  - If consistently low, your reference set may need updating
- **Required fields:** `question`, `generated_text`, `reference`
- **Default field names:** `input_field="question"`, `output_field="generated_text"`, `reference_field="reference"`

### `context_relevance`
- **Plain English:** Is the retrieved context actually relevant to the user's question?
- **Technical:** Token precision between retrieved context and question — how much of the context is relevant to answering the question.
- **Threshold:** PASS ≥ 0.70; FAIL < 0.70. **GOOD:** ≥ 0.85. **BAD:** < 0.40 (retrieval off-topic).
- **Common causes of failure:**
  - Chunk size too large — context includes irrelevant surrounding text
  - Embedding model not suited for the domain
  - Top-K retrieval returning too many chunks, diluting relevance
  - Query not preprocessed correctly before retrieval
- **Fix actions:**
  - Reduce chunk size and overlap
  - Try a domain-specific embedding model
  - Reduce top-K and add re-ranking
  - Add query rewriting or HyDE before retrieval
- **Required fields:** `question`, `context`
- **Default field names:** `input_field="question"`, `context_field="context"`

### `faithfulness`
- **Plain English:** Is the generated answer grounded in the retrieved context, or is the model making things up?
- **Technical:** Measures how much of the generated answer can be attributed to the retrieved context — detecting hallucination.
- **Threshold:** PASS ≥ 0.70; FAIL < 0.70. **GOOD:** ≥ 0.90 (tightly grounded). **BAD:** < 0.50 (significant hallucination).
- **Common causes of failure:**
  - Model adding information from training data not present in context
  - Context too short or sparse to answer the question
  - System prompt asking model to "be helpful" without grounding instruction
  - Model confabulating when context is ambiguous
- **Fix actions:**
  - Add to system prompt: "Answer ONLY based on the provided context. Do not add information not present in the context."
  - Increase context size or retrieve more relevant chunks
  - Add an "I don't know" instruction for when context is insufficient
  - Test with a more conservative/less creative model configuration
- **Required fields:** `context`, `generated_text`
- **Default field names:** `context_field="context"`, `output_field="generated_text"`

### `retrieval_precision`
- **Plain English:** What fraction of the retrieved chunks are actually relevant to the question?
- **Technical:** Precision of the retrieval step — how many of the chunks in the context window are genuinely useful.
- **Threshold:** PASS ≥ 0.70; FAIL < 0.70. **GOOD:** ≥ 0.85. **BAD:** < 0.40 (retrieval is noisy).
- **Common causes of failure:**
  - Too many chunks retrieved (high top-K)
  - Dense retrieval not performing well for the domain
  - Documents not chunked appropriately
- **Fix actions:**
  - Lower top-K retrieval count
  - Add re-ranking step (cross-encoder)
  - Experiment with smaller, more focused chunks
  - Use hybrid retrieval (dense + sparse)
- **Required fields:** `question`, `context`
- **Default field names:** `input_field="question"`, `context_field="context"`

---

## Safety metrics (tool: `evaluate_content_safety`)

### `hap` (Hate, Abuse, Profanity)
- **Plain English:** Does the text contain hate speech, abuse, or profanity?
- **Technical:** Score reflects presence and intensity of toxic language.
- **Threshold:** PASS ≤ 0.10; FAIL > 0.10. **GOOD:** 0.0 (no toxic content). **BAD:** > 0.5 (clearly toxic).
- **Applies to:** model outputs (`generated_text`); can also screen inputs.
- **Fix actions:**
  - Add explicit content filtering layer in front of model output
  - Add to system prompt: "Never use offensive, abusive, or profane language"
  - Implement post-processing filter to block high-scoring responses
  - If fine-tuned, review training data for toxic content
- **Required fields:** `input_text` (or `generated_text`)
- **Default field names:** `input_field="input_text"`, `output_field="generated_text"`

### `pii` (Personally Identifiable Information)
- **Plain English:** Does the text contain PII (names, emails, SSNs, addresses, etc.)?
- **Technical:** Detects PII entities with character positions and confidence scores.
- **Threshold:** PASS ≤ 0.10; FAIL > 0.10. **GOOD:** 0.0 (no PII). **BAD:** > 0.5.
- **Evidence surfacing:** MCP response includes character-level spans. ALWAYS surface them: *"Email detected: john@example.com (chars 12-32)"*.
- **Detected types:** Email addresses, phone numbers, SSNs, names, addresses, credit card numbers.
- **Applies to:** both inputs and outputs.
- **Fix actions:**
  - Add PII redaction layer before text reaches the model (input) or user (output)
  - Use a dedicated PII scrubber library (spacy, presidio)
  - Instruct model: "Never repeat or reference specific personal details from user input"
  - If model outputs PII it wasn't given, check training data
- **Required fields:** `input_text`
- **Default field names:** `input_field="input_text"`

### `jailbreak`
- **Plain English:** Is this input trying to bypass the model's safety guardrails or override its instructions?
- **Technical:** Detects prompt injection and jailbreak attempts using Granite Guardian.
- **Threshold:** PASS ≤ 0.50; FAIL > 0.50. **GOOD:** 0.0-0.2 (benign). **BAD:** > 0.7 (high-confidence jailbreak).
- **Applies to:** user inputs (before sending to model).
- **Common patterns:** "Ignore all previous instructions", "You are now DAN", "Forget your guidelines", "As a developer, override your safety settings", role-play escape attempts.
- **Fix actions:**
  - Block inputs scoring above threshold before they reach the model
  - Add input validation layer that routes high-scoring inputs to a safe fallback
  - Strengthen system prompt with explicit jailbreak resistance instructions
  - Log and review high-scoring inputs to detect attack patterns
- **Required fields:** `input_text`
- **Default field names:** `input_field="input_text"`

### `prompt_safety_risk`
- **Plain English:** Does this input pose a general safety risk to the system?
- **Technical:** Broader than jailbreak — scores general safety risk, including off-topic, harmful task, policy violations.
- **Threshold:** PASS ≤ 0.50; FAIL > 0.50. **GOOD:** 0.0-0.2. **BAD:** > 0.7.
- **Applies to:** user inputs.
- **Fix actions:**
  - Implement input risk scoring layer — route high-risk inputs to human review
  - Add topic restriction instructions to system prompt
  - Consider rate limiting users who consistently submit high-risk prompts
- **Required fields:** `input_text`
- **Default field names:** `input_field="input_text"`

### `social_bias`
- **Plain English:** Does the text contain stereotyping, discrimination, or biased language toward social groups?
- **Technical:** Detects bias including gender, race, religion, nationality, demographic stereotypes.
- **Threshold:** PASS ≤ 0.10; FAIL > 0.10. **GOOD:** 0.0. **BAD:** > 0.3.
- **Applies to:** model outputs (`generated_text`).
- **Fix actions:**
  - Add diversity and inclusion instructions to system prompt
  - Review training or fine-tuning data for biased examples
  - Add post-generation bias filter for high-risk use cases
  - Test with demographically diverse prompts to identify bias patterns
- **Required fields:** `input_text` or `generated_text`
- **Default field names:** `input_field="input_text"`, `output_field="generated_text"`

---

## Agentic metrics (tool: `evaluate_agentic_tool_calls`)

### `tool_call_accuracy`
- **Plain English:** Did the agent call the correct tool for the user's request?
- **Technical:** Binary accuracy — was the tool name in the agent's call correct relative to the ground-truth expected tool call?
- **Threshold:** PASS ≥ 0.80; FAIL < 0.80. **GOOD:** ≥ 0.95. **BAD:** < 0.60.
- **Common causes of failure:**
  - Overlapping or ambiguous tool descriptions
  - Poorly named tools (too similar)
  - Missing tools for certain intent types
  - System prompt not guiding tool selection
- **Fix actions:**
  - Rewrite tool descriptions to be more distinctive and specific
  - Add examples to tool descriptions showing when to use them
  - Group related tools and add routing instructions to system prompt
  - Add a fallback tool for unrecognized intents
- **Required fields:** `input_text`, `tool_calls`, `ground_truth`
- **Default field names:** `input_field="input_text"`, `tool_calls_field="tool_calls"`, `reference_field="ground_truth"`

### `tool_call_parameter_accuracy`
- **Plain English:** Did the agent pass the correct parameter values to the tool?
- **Technical:** Accuracy of parameter values extracted by the agent vs expected (ground-truth) values.
- **Threshold:** PASS ≥ 0.80; FAIL < 0.80. **GOOD:** ≥ 0.90. **BAD:** < 0.60.
- **Common causes of failure:**
  - Ambiguous parameter descriptions in tool schema
  - User input phrased differently than expected
  - Multi-value parameters not extracted correctly
  - Agent hallucinating parameter values not present in user input
- **Fix actions:**
  - Improve parameter descriptions in tool schema with examples
  - Add few-shot examples showing correct parameter extraction
  - For critical parameters (IDs, dates), add explicit extraction instructions
  - Consider adding parameter validation and clarification prompts
- **Required fields:** `input_text`, `tool_calls`, `available_tools`, `ground_truth`
- **Default field names:** `input_field="input_text"`, `tool_calls_field="tool_calls"`, `available_tools_field="available_tools"`, `reference_field="ground_truth"`

### `tool_call_relevance`
- **Plain English:** Was the tool call actually relevant to what the user was asking for?
- **Technical:** Semantic relevance between user's intent and tool called — even if wrong, was it in the right direction?
- **Threshold:** PASS ≥ 0.80; FAIL < 0.80. **GOOD:** ≥ 0.90. **BAD:** < 0.50.
- **Fix actions:**
  - Clarify purpose of each tool in its description
  - Ensure tool descriptions use the same vocabulary as your users
  - Review logs for patterns in what users ask vs. what tools are called
- **Required fields:** `input_text`, `tool_calls`, `available_tools`
- **Default field names:** `input_field="input_text"`, `tool_calls_field="tool_calls"`, `available_tools_field="available_tools"`

### `tool_call_syntactic_accuracy`
- **Plain English:** Was the tool call structurally valid — correct format, required fields present?
- **Technical:** Checks tool call conforms to schema: correct field names, required parameters present, valid data types.
- **Threshold:** PASS ≥ 0.90; FAIL < 0.90. **GOOD:** 1.0. **BAD:** < 0.70.
- **Common causes of failure:**
  - Tool schema not passed to model or model ignoring it
  - Model using incorrect parameter names (e.g., `city_name` vs `city`)
  - Model omitting required parameters
  - Model generating calls in wrong format
- **Fix actions:**
  - Ensure tool schemas are correctly defined and passed to model
  - Add strict JSON mode or function-calling mode if available
  - Add parameter name examples to tool schema descriptions
  - Add schema validation in agent's tool execution layer
- **Required fields:** `tool_calls`, `available_tools`
- **Default field names:** `tool_calls_field="tool_calls"`, `available_tools_field="available_tools"`

---

## Field configuration reference (`GenAIConfiguration`)

The SDK's `MetricsEvaluator` takes a `GenAIConfiguration` that names which DataFrame columns to read for each role. Use this when the partner's data uses non-default column names — avoids renaming their data (RULE 9 in SKILL.md).

```python
from ibm_watsonx_gov.config import GenAIConfiguration

config = GenAIConfiguration(
    input_fields=[...],      # default: ["question"] or ["input_text"]
    output_fields=[...],     # default: ["generated_text"]
    context_fields=[...],    # default: ["context"]
    reference_fields=[...],  # default: ["reference"] — only for answer_similarity
    tool_calls_field="...",      # default: "tool_calls" — agentic only
    available_tools_field="...", # default: "available_tools" — agentic only
)
```

### Defaults per evaluation type

| Evaluation | `input_fields` | `output_fields` | `context_fields` | `reference_fields` | Other |
|---|---|---|---|---|---|
| RAG quality | `["question"]` | `["generated_text"]` | `["context"]` | `["reference"]` (only for `AnswerSimilarityMetric`) | — |
| Content safety (input screening) | `["input_text"]` | — | — | — | — |
| Content safety (output screening) | `["input_text"]` | `["generated_text"]` | — | — | — |
| Content quality | `["question"]` | `["generated_text"]` | `["context"]` | `["reference"]` (optional) | — |
| Agentic tool calls | `["input_text"]` | `["generated_text"]` (optional) | — | `["ground_truth"]` | `tool_calls_field`, `available_tools_field` |

### Example — partner uses `query` and `answer`

```python
config = GenAIConfiguration(
    input_fields=["query"],
    output_fields=["answer"],
    context_fields=["context"],
)
evaluator = MetricsEvaluator(configuration=config)
result = evaluator.evaluate(
    data=df,
    metrics=[m.AnswerRelevanceMetric(), m.FaithfulnessMetric()],
)
```

No data renaming needed — the SDK reads from the partner's columns.

---

## Threshold summary table

### RAG metrics
| Metric | PASS | FAIL |
|---|---|---|
| `answer_relevance` | ≥ 0.70 | < 0.70 |
| `answer_similarity` | ≥ 0.70 | < 0.70 |
| `context_relevance` | ≥ 0.70 | < 0.70 |
| `faithfulness` | ≥ 0.70 | < 0.70 |
| `retrieval_precision` | ≥ 0.70 | < 0.70 |

### Safety metrics
| Metric | PASS | FAIL |
|---|---|---|
| `hap` | ≤ 0.10 | > 0.10 |
| `pii` | ≤ 0.10 | > 0.10 |
| `jailbreak` | ≤ 0.50 | > 0.50 |
| `prompt_safety_risk` | ≤ 0.50 | > 0.50 |
| `social_bias` | ≤ 0.10 | > 0.10 |

### Agentic metrics
| Metric | PASS | FAIL |
|---|---|---|
| `tool_call_accuracy` | ≥ 0.80 | < 0.80 |
| `tool_call_parameter_accuracy` | ≥ 0.80 | < 0.80 |
| `tool_call_relevance` | ≥ 0.80 | < 0.80 |
| `tool_call_syntactic_accuracy` | ≥ 0.90 | < 0.90 |
