# Module: Test cases (ground truth)

**TRIGGER:** the user wants to write, generate, or record test cases, asks about the JSON schema, goal DAGs, `arg_matching`, handoff goals for multi-agent systems, `record`, `generate`, or how many cases are enough.

Authoritative docs: https://developer.watson-orchestrate.ibm.com/evaluate/overview.md (schema, arg matching), `evaluate/create_data.md` (`record`, `generate`).

---

## Before anything: read the agent

Every tool name, argument key, strict value, and collaborator name in a test case must come from the real definitions. Bob reads, in this order:

1. the agent YAMLs (`name`, `display_name`, `style`, `collaborators`, `tools`, the instructions — they say which steps are mandatory and in what order);
2. the tool modules (function names, parameter names and types, docstrings, embedded data such as fixtures or IDs);
3. knowledge-base YAMLs, if any (what the KB covers → `conversational_search` cases);
4. `orchestrate agents list` / `tools list` to confirm the imported names match the files.

---

## Four authoring paths

| Path | When | Notes |
|---|---|---|
| **Generator script** (recommended for systems with a decision table) | several cases share one journey and differ in inputs and expected outcome | One function builds every case from a table; the DAG and matching rules live in one place. `../examples/loan_underwriting/make_testcases.py` builds 5 cases × 2 agent versions. |
| **`record`** | you can produce the behaviour by chatting | Activate the environment, run `orchestrate evaluations record -o recordings/`, chat in the UI (SaaS chat URL, or `orchestrate chat start` on DevEd), one chat session per case, `Ctrl+C`. Output `<thread_id>_annotated_data.json`; `story` and `goals` are inferred — review them. `--context-variables '{"k":"v"}'` adds context. |
| **`generate`** | you have one-line stories and Python tools | `stories.csv` with columns `story,agent`; `-t` is the Python **file** that defines the tools (a directory makes it fall back to a "minimal spec" and guess). Output `<agent>_snapshot_llm.json` and `<agent>_test_cases/`. *Observed on 2.18 / 1.5.2:* the command needs a reachable Langfuse project even when `--with-langfuse` is not used — see "generate on 2.18" below. |
| **Hand-written JSON** | one-off or adversarial cases | Start from an example file; never from memory. |

---

## Schema (framework `TestCase`)

```json
{
  "agent": "agentops_d1_loan_orchestrator_v2",
  "starting_sentence": "I'd like to apply for a home loan. My name is Marcus Reyes, I am self-employed, my annual income is $120,000, I'm requesting $300,000 and my existing monthly debt payments are $1,500.",
  "story": "You are Marcus Reyes, applying for a home loan of $300,000. ... Provide these details when asked and wait for the underwriting decision. Once you have received the decision and the letter, the conversation is over: reply END and nothing else.",
  "max_user_turns": 3,
  "goals": {
    "route_intake": ["validate"],
    "validate": ["route_credit"],
    "route_credit": ["bureau"],
    "bureau": ["route_compliance"],
    "route_compliance": ["sanctions", "aml"],
    "sanctions": ["letter"],
    "aml": ["letter"],
    "letter": ["summarize"]
  },
  "goal_details": [
    { "type": "tool_call", "name": "route_intake", "tool_name": "chat_with_collaborator_agentops_d1_intake_agent",
      "args": { "message": "IGNORE" }, "arg_matching": { "message": "ignore" } },
    { "type": "tool_call", "name": "validate", "tool_name": "agentops_d1_validate_application",
      "args": { "annual_income": 120000, "loan_amount": 300000, "employment_type": "self_employed",
                "monthly_debt_payments": 1500, "applicant_name": "Marcus Reyes" },
      "arg_matching": { "applicant_name": "fuzzy" } },
    { "type": "tool_call", "name": "aml", "tool_name": "agentops_d1_aml_screening",
      "args": { "employment_type": "self_employed", "loan_amount": 300000, "applicant_name": "Marcus Reyes" },
      "arg_matching": { "applicant_name": "fuzzy" } },
    { "type": "tool_call", "name": "letter", "tool_name": "agentops_d1_generate_decision_letter",
      "args": { "decision": "CONDITIONAL_APPROVAL", "primary_reasons": [], "applicant_name": "Marcus Reyes" },
      "arg_matching": { "applicant_name": "fuzzy", "primary_reasons": "ignore" } },
    { "type": "text", "name": "summarize", "response": "Decision for Marcus Reyes: CONDITIONAL_APPROVAL.",
      "keywords": ["CONDITIONAL_APPROVAL"] }
  ]
}
```
(abridged; the full file is `../examples/loan_underwriting/testcases_v2/tc02_self_employed_caution.json`)

| Field | Required | Meaning |
|---|---|---|
| `agent` | yes | `name` of the agent the simulated user talks to (the orchestrator in a multi-agent system) |
| `story` | yes | second-person brief for the simulated user: who they are, the facts they know, what they want, **and when to stop** |
| `starting_sentence` | yes | the first user message |
| `goals` | yes | DAG: each key is a goal name; its list holds the goals that become evaluable once it completes; `[]` marks a leaf |
| `goal_details` | yes | one entry per goal key |
| `max_user_turns` | no | per-case cap on simulated user turns (overrides the config) |
| `runtime_context`, `file_upload`, `dataset_name` | no | context variables, file input, display name |

### `goal_details` types

| `type` | Fields | Checks |
|---|---|---|
| `tool_call` | `tool_name`, `args`, `arg_matching` | the tool was called, in DAG order, with matching arguments |
| `tool_response` | same shape | the tool returned the expected value |
| `text` | `response`, `keywords` | the final answer matches (`keyword_match`, `semantic_match`, `text_match` columns) |
| `conversational_search` | `keywords` | a knowledge base was consulted and the answer contains the keywords; scored by the RAG metrics |

### `arg_matching`

| Strategy | Semantics | Use for |
|---|---|---|
| `strict` (default) | exact match after normalization (case, key order, numeric types, list order are normalized by the framework) | ids, enums, amounts, decisions |
| `fuzzy` | semantic similarity (embeddings, `similarity_threshold` 0.8, token-ratio fallback) | names and free text the user may phrase differently |
| `optional` | skipped if absent, must match if present | arguments the agent may or may not pass |
| `ignore` | never checked | runtime-generated values, handoff messages |
| `{"IGNORE": null}` as the whole `args` | only the tool name is checked | tools whose arguments are all runtime-generated |
| `"<IGNORE>"` as a value | legacy per-field skip | prefer `ignore` |
| `"input.field": "strict"` | dot paths into nested objects | Pydantic-model arguments |

---

## Field notes for multi-agent systems (observed on 2.18 / 1.5.2)

1. **Declare handoffs as goals.** A handoff appears as a tool call named `chat_with_collaborator_<collaborator name>`. Add one `tool_call` goal per expected handoff with `"args": {"message": "IGNORE"}, "arg_matching": {"message": "ignore"}`; otherwise every handoff counts as an unexpected call and precision drops (0.56 in the loan example before, 1.0 after).
2. **`display_name` must equal `name`** on every agent, or routing accuracy stays at 0.0.
3. **Strict before fuzzy.** The matcher stops at the first `fuzzy` field; list strict arguments first in `args` (the example puts `applicant_name` last).
4. **End the conversation.** `max_user_turns: 3` and a story that ends with "Once you have received …, reply END and nothing else". One real turn per case keeps a five-case run near a minute.
5. **Goal names are free text** as long as `goals` keys and `goal_details[].name` match; `tool_name-N` is the documented convention when a tool is called more than once.
6. **One journey, many outcomes.** Keep the DAG identical across cases and vary the inputs and the expected `decision` argument; a generator script makes this trivial and keeps the suite reviewable.
7. **The v1 / v2 pattern.** Keep the test cases per agent version in separate folders that differ only in the `agent` field (and collaborator names in handoff goals); the same suite then shows a regression or an improvement side by side.

---

## DAG patterns

| Pattern | Shape |
|---|---|
| linear chain | A → B → C |
| parallel | A → {B, C} → D (B and C both required before D) |
| fan-out | A → B, A → C, A → D |
| single tool | one goal with `[]` |
| RAG only | one `conversational_search` goal |
| RAG then tool | `conversational_search` → `tool_call` |
| orchestrated journey | handoff → tool(s) → handoff → tool(s) → … → final tool → `text` summary (the loan example) |

---

## `generate` on 2.18

```bash
# -s stories CSV with columns story,agent; -t the Python file with the @tool functions (not a directory)
source "$VENV_ACTIVATE" && \
orchestrate evaluations generate \
  -s evaluations/stories.csv \
  -t tools/<module>.py \
  -o evaluations/generated/
```

*Observed on 2.18.0 / 1.5.2:* the command converts the tools, generates starting sentences and tool sequences, and then calls the Langfuse API to finish — without `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` it fails with `'Langfuse' object has no attribute 'api'`, and with keys for an unreachable host it fails with `Connection refused`, in both cases writing no test cases. You need a **reachable Langfuse project** (Developer Edition started with `-l`, or a hosted project) with `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY` exported; otherwise author with a generator script or by hand (both are what the validated example uses). Review every generated case: the LLM guesses strict values, omits handoff goals, and does not add an end-of-conversation signal.

---

## Coverage and validation

**Coverage (RULE 12, curated):** 5–12 cases per agent — happy path, one case per decision branch or policy rule, a multi-turn case where information arrives late, a bad-input case, RAG cases if there is a knowledge base, and a `text` goal on the final answer where wording matters.

**Validate before running** (Bob does this and shows the table):

| Check | Pass when |
|---|---|
| names | `agent` and every `tool_name` exist in `agents list` / `tools list`; collaborator names in handoff goals match |
| arguments | keys match the tool signature; strict values exist in the tool's data; fuzzy only on free text; strict fields listed before fuzzy |
| DAG | every goal key has a `goal_details` entry; no cycles; the leaf is reachable |
| story | states every fact the agent will ask for; names the stop condition; `max_user_turns` set |
| dry run | tracing the conversation in your head from `starting_sentence` reaches every goal in order |

```
## Test case validation
| Case | Names | Arguments | DAG | Story | Dry run | Notes |
|---|---|---|---|---|---|---|
```

Then run one case through `quick-eval` or `evaluate -p <file>` before the whole suite (`reference/module-eval.md`).

---

## Done when

- Test case files exist in a folder, validated with the table above.
- One case has run end to end.
- The user has chosen: write more cases, run the suite, or stop.
