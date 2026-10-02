# Module: Optimize (levers, estimates, re-test)

**TRIGGER:** the user wants to reduce cost, asks whether a cheaper model would do, wants to cap spend at runtime, or asks what the evaluation framework itself costs.

Bob proposes; the user applies; the Agent Ops suite plus the cost report on the same cases decide (RULE 8).

---

## Inputs

- A baseline from `module-report.md` (per-agent, per-model, per-turn numbers) — without one, do the baseline first.
- The agent YAMLs (`llm`, `style`, `collaborators`, `tools`, instruction length) and the tool docstrings.
- The Agent Ops test cases for the re-test.

## Read-only diagnostics

- `orchestrate models list` — candidate models on the instance.
- Instruction and docstring sizes (Bob reads the files; tokens ≈ characters ÷ 4 as a first estimate).
- Generations per conversation and per agent from the baseline.

---

## Levers (typical payoff order)

| Lever | What it changes | Estimate from the baseline | Risk / check |
|---|---|---|---|
| **Fewer turns** — story-complete prompts, no clarification loops, `planner` style for fixed procedures | input growth per turn | (turns saved) × (average input per turn) × price | behaviour: Agent Ops suite |
| **Fewer handoffs** — merge collaborators that always run together; orchestrator owns the final tool | one full context per handoff | (handoffs saved) × (that agent's base cost) × price | routing accuracy; journey success |
| **Model per agent** — a cheaper model for agents with simple, structured steps | per-token price of those generations | Σ tokens(agent) × (price delta) | tool-calling reliability: in the loan example a small model returned parse-failure fallbacks and a mid-size one narrated tool calls — run the suite on the changed agent before counting the saving |
| **Shorter instructions and tool docstrings** | base cost of every generation of that agent | (tokens removed) × generations × price | keep the rules that the rubric checks; re-run rubric |
| **Smaller tool outputs** — return fields the agent needs, not whole records | input of the generation after each tool call | (bytes removed ÷ 4) × calls × price | agent still has what it needs: journey success |
| **Knowledge-base retrieval** — chunk size, top-k | RAG context per answer | (chunks × size) × price | faithfulness, answer relevancy |
| **Evaluation cost** — `max_user_turns: 3`, `n_runs: 1` while iterating, five cases not fifty | the framework's judge and simulator calls | runs × cases × (framework calls) | signal: enough cases to trust the number (Agent Ops coverage floor) |
| **Runtime cost guardrails** — Rate Limiter per tool, Output Length Guard on verbose agents | caps runaway loops and oversized answers | bounds, not savings | `agent-controls` skill (Guardrails building block) |

Not a lever: **model policies** (`orchestrate models policy`) balance load or fall back across virtual models; they do not route by cost or complexity. Routing is done by assigning models per agent and designing which agent handles which step.

---

## Procedure

1. **Pick one lever** with the largest estimated saving that the risk column allows.
2. **State the estimate** from the baseline (tokens × price delta), labelled with the price source.
3. **The user applies the change** (YAML, instructions, tools) and re-imports.
4. **Re-test on the same cases:** Agent Ops suite (journey success, rubric, red team if the change touched instructions) and `trace_cost.py --eval-run` on the new run.
5. **Report the pair:** Δ$ per conversation, Δ$ per successful journey, and the quality deltas. Keep the change only if quality held.
6. Repeat with the next lever. Keep the baseline JSON of every step so the trail is auditable.

```
## Optimization step <n> — <lever>
Estimate: −$<x> per conversation (<p>%), price <source>
Result:   $<before> → $<after> per conversation · $<before> → $<after> per successful journey
Quality:  journey success <a>/<n> → <b>/<n> · rubric <…> · routing <…>
Decision: keep | revert — <one line>
```

---

## Runtime cost controls (hand-off to Guardrails)

When the goal is to bound spend rather than reduce the average: a **Rate Limiter** control per tool (per minute, per tenant) stops runaway agent loops; an **Output Length Guard** caps verbose answers; both are configuration attached to agents and tools, no code change. Route to the `agent-controls` skill for artifact selection, hooks, and priorities.

---

## Done when

- A lever list for this agent with estimates, ordered and risk-labelled.
- The first lever applied by the user and re-tested, with the before/after pair recorded.
- Where ongoing visibility will live (Control Plane, Langfuse, or run-level usage in the application) and the alert threshold.
