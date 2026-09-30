# Cost Management

Part of **[Control](../)** in the **[AI Control Plane](../../)**.

AI agents turn every interaction into model calls, tool calls, and tokens. Without visibility, spend grows quietly: a looping agent, a verbose prompt, or an oversized model can burn through a budget before anyone notices. **Cost Management** gives you that visibility, starting at the level of each agent interaction.

---

## Why This Matters

- **Agent cost is hard to predict.** The same request can take one model call or ten, depending on how the agent reasons and which tools it calls.
- **Token budgets burn silently.** Without per-interaction tracking, runaway loops and oversized prompts show up only on the invoice.
- **Cost has to be weighed against quality.** Choosing a smaller model or a shorter prompt only makes sense when you can see both the cost and the evaluation results.

---

## Available Today — Agent Cost and Token Tracking

For **watsonx Orchestrate agents**, cost and token usage can be captured per interaction through Langfuse, alongside the traces and latency data that [Agent Ops](../agent-ops/) uses.

| Capability | What It Does |
|---|---|
| **Cost per scenario** | See tokens, cost, and pass or fail for every evaluation scenario, so expensive paths show up before production |
| **Context growth per turn** | See how cost climbs as multi-turn conversations grow, a key driver of multi-turn cost |
| **Cost patterns** | Base cost, growth rate, input-to-output token ratio, and spend wasted on failed runs |
| **Production projection** | Project cost at your expected conversation volume, with data-driven recommendations |

Tracking runs on Langfuse, either locally with watsonx Orchestrate Developer Edition or on a hosted Langfuse instance. Cost appears when Langfuse has pricing for the agent's model. Models it does not already know, including many watsonx-served models, need their pricing registered first. Latency is always recorded.

### Where the code lives

- [`agent-ops/assets/wxo-agents/06_langfuse_observability.py`](../agent-ops/assets/wxo-agents/06_langfuse_observability.py) — tracks cost, latency, and token usage per interaction via Langfuse. It runs as the last step of the Agent Ops evaluation workflow, so it stays with the other Agent Ops scripts.

---

## Coming Soon — Enterprise Cost Management

- **Allocation** of AI spend by team, use case, or model.
- **Budgets and alerts** before costs become unmanageable.
- **Optimization** — identifying waste and cost per outcome across AI workloads.

---

## Bob Skills

The [Agent Ops Bob skill](../../../ibm-bob/skills/agent-ops/) includes Langfuse cost analysis. Ask Bob, for example, *"How do I set up Langfuse so I can see cost per scenario?"*

📖 Docs: [Cost Management](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/cost-management/)
