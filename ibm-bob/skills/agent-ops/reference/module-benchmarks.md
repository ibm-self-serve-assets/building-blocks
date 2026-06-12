# Module: Benchmarks

**TRIGGER:** Load when user wants to author benchmark JSONs, run `record` or `generate`, asks about the benchmark JSON schema, DAG patterns, `arg_matching` strategies, the `kb_tool_call` vs `conversational_search` confusion, or the minimum coverage floor.

---

## Three authoring paths (preferred order)

1. **`record`** — capture real chat-UI sessions, save as benchmark JSON. **Fastest path.** Dev Edition only.
2. **`generate`** — expand a CSV of user stories into benchmark JSON via the active env's LLM. Tool-aware (Python `@tool` only).
3. **manual** — write JSON by hand, using `examples/` as templates. Fallback.

**CRITICAL:** Before any authoring path, **READ the agent's tool code, embedded data files, and KB YAMLs.** Every tool name, arg key, and strict arg value in a benchmark must come from real code — never guess.

**Authoritative docs:**
- `record` + `generate`: https://developer.watson-orchestrate.ibm.com/evaluate/create_data.md
- Overview / arg matching: https://developer.watson-orchestrate.ibm.com/evaluate/overview.md

---

## Inputs

- **Required:** target env from Q1.
- **Required:** agent's tool code path (typically `agent/tools/`).
- **Optional:** for `record`: server running on `:4321` (DevEd only).
- **Optional:** for `generate`: a `stories.csv` (see `examples/stories_sample.csv`).

## Read-only diagnostics

- **Tools are Python `@tool`-decorated:** read 1-3 files in user's `tools/` directory; confirm they import `@tool` from `ibm_watsonx_orchestrate.agent_builder.tools` and have type hints.
- **Agent name in `agent_config.yaml`:** read `agent_config.yaml` (or multi-agent variant). This name becomes the `agent` field in every benchmark JSON.
- **KB YAMLs (if RAG benchmarks needed):** read `knowledge_bases/*.yaml` for collection names and source docs.

---

## Authoring path 1 — `record` (DevEd only)

**WHEN:** user has an existing agent and wants to capture real conversations as benchmarks. Especially useful when user isn't sure what to test or wants to convert reported bugs into regression scenarios.

```bash
# Then open http://localhost:4321 in your browser and chat with the agent.
# Each conversation saved as <thread_id>_annotated_data.json in the output dir.
source "$VENV_ACTIVATE" && \
orchestrate evaluations record \
  --output-dir recordings/$(date +%Y%m%d-%H%M%S)
```

**Follow-up:** after user pastes output path, read the recorded JSON(s) with Read tool, then write benchmark JSON to `benchmarks/` using the schema below. Refine `story` and `starting_sentence` to match the recorded conversation.

---

## Authoring path 2 — `generate`

**WHEN:** user wants benchmarks for many scenarios at once and has rough story descriptions in a CSV. Active env's LLM expands each row into a full benchmark JSON.

**Prereq:** a CSV with two columns: `story` and `agent`. See `examples/stories_sample.csv` for the exact format.

```bash
# The active env's LLM expands each CSV row into a full benchmark JSON.
# Tools must be Python @tool-decorated; framework introspects signatures to fill in expected tool_call entries.
source "$VENV_ACTIVATE" && \
orchestrate evaluations generate \
  --stories-path stories.csv \
  --tools-path agent/tools \
  --output-dir generated_benchmarks/$(date +%Y%m%d-%H%M%S)
```

After it finishes, review generated JSONs and flag any that need manual cleanup (the LLM sometimes guesses wrong arg values).

---

## Authoring path 3 — manual

**WHEN:** `record` and `generate` aren't available, OR user needs precise control over a complex scenario (multi-turn, strict DAG, specific adversarial framing).

**Process:** Bob writes the JSON file directly (Bob owns the `edit` group; this is NOT a "command emission" case). Use one of the `examples/` templates as starting point, then customize. After writing, run dry-run via `quick-eval` to validate (see `reference/module-eval.md`).

---

## Benchmark JSON schema

### Required top-level fields

| Field | Type | Notes |
|---|---|---|
| `agent` | string | Must match `name:` in `agent_config.yaml` |
| `story` | string | Second-person instructions for the LLM-simulated user. **MUST include explicit end-of-conversation criteria** — simulator will end early without them. |
| `starting_sentence` | string | First message the simulated user sends. Natural, specific, aligned with story. |
| `goals` | object | DAG: keys are goal names (matching `goal_details.name`), values are arrays of dependent goal names that can be evaluated once key completes. `[]` = leaf. |
| `goal_details` | array | Per-goal expected actions. Every key in `goals` must have matching entry. |
| `text_checks` | object (optional) | Expected keywords in agent text responses. |

### `goal_details` types

**`tool_call`** — expects the agent to call a specific tool with specific arguments.
- Fields: `name` (matches goals key), `type: "tool_call"`, `tool_name`, `args` (dict), `arg_matching` (per-arg strategy).

**`tool_response`** — expects a specific tool response value. Same shape as `tool_call`; validates the tool's RETURN, not just the call.

**`conversational_search`** — expects agent to perform a knowledge-base lookup (RAG).
- Fields: `name`, `type: "conversational_search"`, `keywords` (list of must-include terms in final answer).
- NO `args` / `arg_matching` — framework does NOT validate the search query; it validates that a KB was consulted AND that the answer contains the keywords.

**`text`** — expects a specific text response. Used with `text_checks`.
- Fields: `name`, `type: "text"`, `response` (template), `keywords` (must-include list).

### Valid `type` values (CRITICAL)

The eval-framework's `ReferencelessTestCase` schema (used by `quick-eval` + `evaluate`) accepts EXACTLY these `type` values: `text`, `tool_call`, `tool_response`, `conversational_search`.

**Earlier drafts referenced `kb_tool_call` — that is NOT a valid type in ADK 2.9.0 / eval-fw 1.4.x.** KB / RAG scenarios use `conversational_search`.

### `arg_matching` strategies

| Strategy | Semantics |
|---|---|
| `strict` | Exact equality required. Use for IDs, enums, fixed strings (account IDs, tier names, communication types). |
| `fuzzy` | LLM judges semantic equivalence. Use for free-text descriptive args (`custom_content`, `notes`). |
| `optional` | Field may or may not be present; if absent, no penalty. |
| `<IGNORE>` | String literal as the arg value; tells framework to skip validation for this arg entirely. |

### Naming convention

Goal names follow `<tool_name>-<N>`, e.g., `get_account_holder_by_id-1`, `calculate_portfolio_metrics-2`. The `-N` suffix disambiguates when the same tool is expected to be called multiple times.

---

## DAG patterns

| Pattern | Shape |
|---|---|
| `linear_chain` | A → B → C. Three goals, each depends on prior. |
| `parallel` | A and B independent; both must complete before C. |
| `fan_out` | A → B, A → C, A → D. After A, three parallel goals. |
| `single_tool` | One goal, `[]` deps. Simplest valid benchmark. |
| `conversational_search_only` | A single `conversational_search` goal for KB/RAG-only scenarios. |
| `kb_then_tool` | KB lookup (`conversational_search`) → tool call using KB result. |

---

## Coverage recommendations (RULE 11)

**SOURCE NOTE (RULE 9):** curated guidance, NOT a WXO-published coverage standard. The 5-12 scenario floor and category list are starting points from real engagement experience — adjust based on agent complexity, blast radius, and customer risk tolerance.

| Category | Description |
|---|---|
| Tool calls | At least one `strict` and one `fuzzy` arg_matching. |
| Filtered queries | Scenarios with arg constraints (e.g., "only Gold tier"). |
| Multi-turn | Scenarios where user provides info across multiple messages. |
| Error handling | Scenarios where user gives bad input and agent must recover. |
| RAG / KB | Scenarios with `conversational_search` goals if agent has a KB. |
| Text validation | Scenarios with `text_checks` for tone / format / required keywords. |

**Minimum:** 5-12 scenarios per agent for meaningful metrics. Single-scenario eval has too much variance.

---

## Reference templates

| Path | Description |
|---|---|
| `examples/portfolio_advisor/` | 8 working scenarios on a real agent. Copy-modify pattern. |
| `examples/minimal_single_tool/` | Smallest valid benchmark. Use for `generate` few-shot priming. |
| `examples/multi_agent_routing/` | Facilitator + 2 collaborators; tests Agent Routing F1. |
| `examples/rag_only/` | KB-bound scenarios; tests RAG metrics in isolation. |
| `examples/stories_sample.csv` | CSV input format for `generate`. |

---

## Done-when criteria

- One or more benchmark JSON files exist under user's `benchmarks/` directory.
- Each JSON validates against the schema (Bob has read back and confirmed).
- Dry-run via `quick-eval` (see `reference/module-eval.md`) has succeeded against at least one.
- User has explicitly chosen next action: write more scenarios, run full `evaluate`, or stop.
