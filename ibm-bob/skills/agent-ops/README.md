# Agent Ops — Bob skill (watsonx Orchestrate)

A Bob skill for **build-time evaluation, rubric scoring, red-teaming, and trace inspection** of watsonx Orchestrate (WXO) agents, using the evaluation framework in the WXO Agent Development Kit (ADK). Works against **SaaS** instances (IBM Cloud or AWS hosted) and **Developer Edition**.

Validated with ADK 2.18.0 / evaluation framework 1.5.2 on a four-agent loan-underwriting system; those assets ship as `examples/loan_underwriting/`.

## What the skill does

When you ask Bob to test, score, attack, or trace a WXO agent, it runs a three-question interview (environment, intent, current state), proposes a module plan, runs a few read-only checks, and then emits the exact `orchestrate` commands for you to run in your terminal. Bob reads the result files afterwards and tells you what they mean. Bob never runs evaluations, imports, or installs itself.

Six modules, any order:

| Module | Commands | What you get |
|---|---|---|
| **Eval** | `evaluations quick-eval`, `evaluations evaluate` | Smoke test without ground truth; full evaluation with an LLM-simulated user and per-case metrics |
| **Test cases** | `evaluations record`, `evaluations generate`, generator scripts, hand-written JSON | Ground-truth cases with goal DAGs, handoff goals, and per-argument matching rules |
| **Analyze** | `evaluations analyze` | Root cause per failed case, and a decision: test case, agent, or model |
| **Rubric** | `evaluate` with `RubricEvaluation` | Pass/fail per plain-language rule, with the judge's reasoning |
| **Red-teaming** | `evaluations red-teaming list / plan / run` | Attack success rate per attack, transcripts, remediation |
| **Observability** | `observability traces search / export`, Python `TracesController`, REST | Span tree per conversation: handoffs, tool calls, model, tokens, latency |

## When to use it

- Before releasing a WXO agent, and after every prompt, tool, or model change (the test cases are a regression suite)
- When a multi-agent system "works in the chat" but you cannot say how often it takes the right path
- When a policy ("always run the AML check", "never quote a figure a tool did not return") needs to become a pass/fail test
- When you need to know how the agent behaves under pressure from a hostile user
- When a conversation went wrong in production and you need the trace

## When not to use it

| Need | Use instead |
|---|---|
| Runtime enforcement on WXO agents (PII filter, content guardrails, secrets detection, rate limits, model fallback) | the `agent-controls` skill (Guardrails building block) |
| Pass/Flag/Block guardrails on any framework with watsonx.governance | the `real-time-guardrails` skill |
| Cost in tokens or dollars per agent, model, or use case; Langfuse; cost optimization | the `cost-management` skill (Cost Management building block) |
| Evaluating a LangGraph/LangChain app or a RAG pipeline with watsonx.governance metrics | the `build-time-gen-ai-evals` skill |

## Prerequisites

| Component | Requirement |
|---|---|
| Python | 3.12 (what the framework is validated on) |
| ADK | `pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"` — pulls evaluation framework 1.5.x |
| An environment | `orchestrate env add` + `orchestrate env activate` pointing at the instance where the agent is imported; SaaS tokens expire after about two hours |
| Developer Edition only | a Docker runtime; `orchestrate server start -e .env` (`-i` for traces) |
| For `generate` and red-team `plan` | model access through the active environment's gateway (works out of the box on SaaS) |

Full details, including credentials and network egress: `assets/PREREQUISITES.md`.

## What is in the skill

```
agent-ops/
├── SKILL.md                       # loaded by Bob on every invocation: interview, rules, dispatch, field notes
├── README.md                      # this file
├── USAGE-GUIDE.md                 # install and first-run walkthrough
├── setup.sh                       # venv + ADK install
├── reference/                     # loaded on demand per module
│   ├── auth-env-matrix.md         # targets, auth types, token expiry, capability × target matrix
│   ├── module-eval.md             # quick-eval, evaluate, config.yaml, output files, failures
│   ├── module-benchmarks.md       # test case schema, DAGs, handoff goals, arg_matching, record/generate
│   ├── module-analyze.md          # metrics, thresholds, analyze, diagnosis table
│   ├── module-rubric.md           # RubricEvaluation criteria and results
│   ├── module-red-teaming.md      # attack catalogue, plan/run, attack file schema, remediation
│   ├── module-observability.md    # traces CLI, Python, REST, watsonx Orchestrate Agentic Control Plane
│   └── command-emission.md        # block format, what Bob may run
├── examples/
│   ├── loan_underwriting/         # validated on 2.18: 5 cases × v1/v2, rubric, 3 attacks, stories.csv, generator
│   ├── portfolio_advisor/         # 8 single-agent cases incl. RAG and text check
│   ├── minimal_single_tool/       # smallest valid case
│   ├── multi_agent_routing/       # facilitator + 2 collaborators
│   ├── rag_only/                  # knowledge-base cases
│   └── stories_sample.csv         # input for `generate`
└── assets/
    ├── mcp.json                   # watsonx-orchestrate-adk-docs MCP server
    └── PREREQUISITES.md
```

## Installing the skill

```bash
cp -r agent-ops <your-repo>/.bob/skills/
```

Open the agent project in Bob and ask, for example:

- *"Evaluate this agent before I ship it"*
- *"Write five test cases for the refund flow and run them"*
- *"Precision is 0.56 but every case passed — what is going on?"*
- *"Turn these three compliance rules into a rubric and score last night's run"*
- *"Red-team the orchestrator for instruction override and crescendo"*
- *"Show me the trace for the conversation that approved the wrong applicant"*

## Design properties

- **Interview-first, terminal-emitting.** Bob writes the command; you run it. No surprise imports, installs, or instance-level changes.
- **SaaS and Developer Edition.** Both are first-class; the evaluation framework runs against whichever environment is active.
- **Shared-instance safe.** Bob lists before any import, asks for a prefix when names could collide, and never touches assets it did not create.
- **Field notes, labelled.** Behaviours observed on 2.18 / 1.5.2 are marked as such and separated from documented semantics.
- **Live docs.** The bundled MCP server points at the current ADK documentation.

Source of truth for ADK semantics: https://developer.watson-orchestrate.ibm.com/
