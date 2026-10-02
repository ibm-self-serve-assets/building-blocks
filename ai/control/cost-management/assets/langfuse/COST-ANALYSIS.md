# Five-layer cost analysis (Langfuse)

A customer-ready way to turn Langfuse token and cost data into decisions. The **data** (tokens, cost, latency per generation) is Langfuse's; the **report shape** below is curated from engagements — adapt the sections to what the customer cares about. Bob follows this guide when asked for a cost analysis.

## Prerequisites

1. watsonx Orchestrate exports traces to a Langfuse project you can read (`README.md`, step 1).
2. The agent's models are priced in Langfuse (step 2); otherwise cost is 0 and only tokens and latency are available.
3. Sessions map to something meaningful: an evaluation run produces one Langfuse session per test case; applications should set a session id per conversation and tags per use case or agent version.

## Pull the data

Use the SDK or `langfuse_cost_report.py`; never ask the user to read the dashboard aloud. For an evaluation run, map sessions to cases with the `<case>.metadata.json` files in the run folder (they carry the thread id) and bring `is_success` from `summary_metrics.csv`.

## Layer 1 — per scenario (or per session)

| Scenario | Turns | Input tokens | Output tokens | Total | Cost | Result |
|---|---|---|---|---|---|---|

Sorted by total tokens, descending. Totals and the average per scenario at the bottom.

## Layer 2 — per turn (multi-turn scenarios)

Each turn re-sends the conversation so far; input tokens grow with every exchange. Show the sequence per multi-turn scenario:

```
tc04 (4 turns):  turn 1  2,296 in /   228 out
                 turn 2  5,607 in /   628 out   (+3,311 context)
                 turn 3 10,401 in /   803 out   (+4,794)
                 turn 4 16,297 in / 1,035 out   (+5,896)
```

## Layer 3 — patterns (computed from the data, never assumed)

- **Base cost** — input tokens of single-turn scenarios ≈ system prompt + tool definitions; the fixed overhead every turn pays.
- **Context growth rate** — average input-token increase per turn across multi-turn scenarios.
- **Input/output ratio** — input usually dominates (10:1 or more); a high output share means a verbose agent.
- **Wasted spend** — cost of failed scenarios, in dollars and as a share of the total.
- **Concentration** — share of total cost in the top three scenarios.

## Layer 4 — recommendations (only what the data supports)

| Pattern | Recommendation |
|---|---|
| Base cost high (> ~3,000 input tokens on single-turn cases) | tighten instructions and tool docstrings; drop unused tools from the agent |
| Steep context growth (> ~3,000 tokens per turn) | succeed in fewer turns: ask for all facts at once, avoid clarification loops |
| Failed scenarios carry a large share of spend | fixing functional failures *is* cost optimization (see Agent Ops) |
| Extreme input/output ratio (> 15:1) | work on input only; output savings are negligible |
| One scenario dominates | look for retry loops, redundant tool calls, over-long tool outputs |
| Multi-turn cost ≫ single-turn | split long workflows into focused interactions; summarize state between steps |
| Expensive model on simple steps | route easy steps to a smaller model and re-run the evaluation suite to confirm quality holds |

## Layer 5 — projection

`average cost per conversation × conversations per day × 30` → monthly estimate; ask for the expected volume if unknown, and flag that production conversations are usually longer than evaluation cases. Suggest an alert threshold (for example, conversations above twice the average).

## Report template

```
## Cost & latency — <agent> (<window or run>)
Summary: <n> conversations · <tokens> tokens · $<cost> · $<avg>/conversation · model(s) <...> at $<in>/$<out> per 1M

Per scenario            (Layer 1 table)
Context growth          (Layer 2, multi-turn only)
Patterns                base ≈ <t> tokens · growth ≈ <t>/turn · in:out <r>:1 · wasted $<w> (<p>%) · top-3 share <s>%
Recommendations         (Layer 4, data-backed only)
Projection              <n>/day → ≈ $<m>/month · alert above <t> tokens/conversation
```

## Cost and quality together

Run the cost report on the same run you evaluated with Agent Ops. A change that halves cost but drops journey success from 5/5 to 3/5 is not an optimization; present both numbers side by side.
