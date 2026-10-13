# Bob Modes for Agent Evaluation

## What are Bob modes?

[Bob](https://bob.ibm.com) is IBM's AI code assistant. **Custom modes** give Bob a persona, a workflow, and rules for a specific job. A mode is a `.bob/` folder:

- `custom_modes.yaml` — who Bob is in this mode, the mandatory rules, the references
- `workflow.md` — the phase-by-phase procedure with commands and report formats
- reference files Bob uses as templates

Drop the folder into your project, switch to the mode in Bob's mode selector, and Bob is ready.

**Mode or skill?** The [Agent Ops skill](../bob-skills/) is advisory: Bob emits commands for you to run. The mode is hands-on: Bob runs the commands, reads the results, and proposes fixes, asking before anything that changes the instance. Same knowledge, different stance; pick the one that fits how you work.

## Modes in this directory

### Base modes

| Mode | Description |
|---|---|
| [Agent Ops](base-modes/) | Evaluate watsonx Orchestrate agents before release with the ADK evaluation framework (ADK 2.18+): quick-eval, ground-truth test cases with handoff goals, evaluate, analyze, rubric scoring, red-teaming, and traces — on SaaS or Developer Edition. Ships the validated loan-underwriting reference cases. |

## Prerequisites

- [Bob](https://bob.ibm.com)
- Python 3.12 and the ADK with the agentops extra:
  ```bash
  pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"
  ```
- An activated `orchestrate` environment where the agent is imported: a SaaS instance (IBM Cloud or AWS hosted) or Developer Edition (`orchestrate server start -e .env`, then `orchestrate env activate local`)

See the mode's README for installation and the workflow.
