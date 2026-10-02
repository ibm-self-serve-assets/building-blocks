# Module: Report (five layers, cost next to quality)

**TRIGGER:** the user wants a cost report for a run, a window, or a use case, asks "where does the cost come from", wants a projection, or needs a customer-ready summary.

The **data** comes from `module-sources.md` (platform traces, `trace_cost.py`) or `module-langfuse.md` (`langfuse_cost_report.py`). The **report shape** below is curated from engagements; adapt the sections to the audience.

---

## Inputs

- Per-conversation rows: tokens in/out, dollars (with price source), model(s), agent(s), turns, session id.
- When the conversations are an Agent Ops run: `summary_metrics.csv` (`is_success`, `total_steps`, `average_agent_response_time`) and the `<case>.metadata.json` thread ids — `trace_cost.py --eval-run` produces the joined CSV.
- Expected volume (conversations per day) for Layer 5; ask if unknown.

## Read-only diagnostics

- The CSV/JSON exists and the price table's `as_of` is recent enough to quote.
- Which models are unpriced (reported as tokens only).

---

## Layer 1 — per scenario (per session)

| Case / session | Result | Turns | Gens | Input | Output | $ | Agents |
|---|---|---|---|---|---|---|---|

Sorted by tokens, descending; totals and averages below. With an Agent Ops run, `Result` is `is_success`.

**Headline:** `$ per successful journey = total $ ÷ successes`. Say it before anything else.

## Layer 2 — per turn and per handoff (context growth)

Each model call re-sends its context. Two growth mechanisms show in traces:

- **turns** — later user turns carry the whole conversation; input tokens climb with each exchange;
- **handoffs** — each collaborator call starts a new context (system prompt + tools + the message), so a four-agent journey pays the base cost several times per conversation (12 generations for one loan application).

Show one multi-turn or multi-handoff conversation as a sequence of generations with input/output tokens and the agent that made each call.

## Layer 3 — patterns (computed, never assumed)

- **Base cost** — input tokens of the first generation of an agent ≈ its instructions + tool definitions.
- **Growth rate** — average input increase per turn (and per handoff).
- **Input : output ratio** — usually 10:1 or more; a low ratio means verbose answers.
- **Wasted spend** — dollars of failed cases, as $ and % of total.
- **Concentration** — share of total $ in the top three conversations and the top agent.
- **Model split** — $ per model; whether an expensive model is doing cheap work.

## Layer 4 — recommendations (only what the data supports)

| Pattern | Recommendation | Verify with |
|---|---|---|
| base cost > ~3,000 input tokens for an agent | shorten instructions and tool docstrings; remove unused tools from that agent | base cost of the first generation; Agent Ops suite |
| growth > ~3,000 tokens per turn | fewer turns: ask for all facts at once, avoid clarification loops | turns per case; `total_steps` |
| many handoffs per conversation | merge collaborators that always run together; let the orchestrator call the tool directly | generations per conversation; routing accuracy |
| failed cases hold a large share of spend | fix the behaviour first (Agent Ops) — that is the cheapest optimization | `is_success`; $ per successful journey |
| in:out ratio > 15:1 | work only on input; output savings are negligible | ratio |
| one conversation or agent dominates | look for retry loops, redundant tool calls, over-long tool outputs | per-agent $, tool response sizes in the trace |
| expensive model on simple steps | a cheaper model for that agent, after a tool-calling check | Agent Ops suite on the changed agent, then cost again |

## Layer 5 — projection

`$ per conversation × conversations per day × 30` → monthly, at list price; state the price source and that production conversations tend to run longer than test cases. Add a threshold for an alert (for example, conversations above twice the average tokens) and name where it would be watched (Control Plane, Langfuse dashboard, or the application's run-level usage).

---

## Report template

```
## Cost report — <agent / use case> (<run or window>, prices <source>, as of <date>)

Headline: $<x> per successful journey (<n> conversations, <s> successes) · $<y> per conversation · <t> tokens per conversation (<in> in / <out> out)

Per scenario                 (Layer 1 table)
Context growth               (Layer 2: one worked conversation)
Patterns                     base ≈ <t> tokens · growth ≈ <t>/turn · in:out <r>:1 · wasted $<w> (<p>%) · top-3 share <s>% · model split <…>
Recommendations              (Layer 4, data-backed, each with its verification)
Projection                   <n>/day → ≈ $<m>/month · alert above <t> tokens/conversation
Caveats                      model-inference cost at list price; invoice depends on the plan; unpriced models: <…>
```

## Cost × quality (two versions)

```
| | v1 | v2 |
|---|---|---|
| journey success | 3/5 | 5/5 |
| rubric | 18/20 | 20/20 |
| $ per conversation | … | … |
| $ per successful journey | … | … |
```

Present this before any single-version number: the comparison is what decisions are made on.

---

## Done when

- The headline, the five layers, and the caveats are written with the price source and date.
- With an Agent Ops run: the joined table and the cost × quality comparison.
- Next step chosen: optimize (`module-optimize.md`), set up Langfuse for ongoing visibility, or stop.
