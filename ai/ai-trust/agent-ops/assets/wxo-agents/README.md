# Agent Ops — Technical Assets

Production-ready Python scripts for testing, monitoring, and improving AI agents using the watsonx Orchestrate Agent Development Kit (ADK) evaluation framework.

These scripts wrap the ADK CLI commands with programmatic output parsing — suitable for CI/CD pipeline integration.

## What's Inside

| Script | What It Does |
|--------|-------------|
| `01_agent_evaluation.py` | Run benchmarks with LLM-simulated users, parse results for journey success, tool call precision/recall |
| `02_agent_analysis.py` | Diagnose agent failures with default and enhanced analysis modes |
| `03_quick_eval.py` | Fast referenceless validation — catch tool schema issues without ground truth |
| `04_benchmark_generation.py` | Generate test cases from plain-English user stories |
| `05_red_teaming.py` | Adversarial security testing against 15 attack types |
| `06_langfuse_observability.py` | Track cost, latency, and token usage per interaction via Langfuse |

Also includes:
- `sample_agent/` — A complete sample agent (config, tools, knowledge base) ready for import
- `sample_data/` — Benchmark scenarios and user stories for testing

## Prerequisites

- **Python 3.12** (NOT 3.13+ — ADK does not support it)
- WXO Developer Edition running locally
- ADK CLI installed:
  ```bash
  pip install 'ibm-watsonx-orchestrate[agentops]>=2.5.1,<2.9.0'
  pip install 'ibm-watsonx-orchestrate-evaluation-framework>=1.2.7,<2.0.0'
  pip install 'langfuse<4'
  ```

## Quick Start

```bash
# 1. Create a Python 3.12 virtual environment
python3.12 -m venv agent-ops-env
source agent-ops-env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start WXO Developer Edition (with Langfuse for script 06)
orchestrate server start -e .env -l

# 4. Import the sample agent
cd sample_agent
orchestrate tools import -k python -f tools/support_tools.py
orchestrate agents import -f agent_config.yaml
cd ..

# 5. Run evaluation
python 01_agent_evaluation.py
```

## Recommended Evaluation Workflow

```
quick-eval → generate → evaluate → analyze → red-team → observe
   (03)        (04)       (01)       (02)       (05)      (06)
```

1. **Quick-eval** (script 03) — Fast sanity check for tool schema issues
2. **Generate** (script 04) — Create benchmarks from user stories
3. **Evaluate** (script 01) — Full evaluation with simulated users
4. **Analyze** (script 02) — Diagnose any failures
5. **Red-team** (script 05) — Security testing
6. **Observe** (script 06) — Cost and performance visibility

## Metrics Reference

### Agent Metrics
| Metric | Target | What It Measures |
|--------|--------|-----------------|
| Journey Success | 1.0 | Did the agent complete all goals? (binary) |
| Journey Completion % | 100% | Percentage of goals met |
| Tool Call Precision | >= 0.5 | Correct calls / total calls made |
| Tool Call Recall | >= 0.9 | Expected calls made / total expected |
| Agent Routing F1 | >= 0.9 | Harmonic mean of precision and recall |

### RAG Metrics
| Metric | Target | What It Measures |
|--------|--------|-----------------|
| Faithfulness | >= 0.8 | Answer grounded in retrieved docs |
| Answer Relevancy | >= 0.7 | Answer addresses the question |
| Response Confidence | > 0.5 | LLM confidence in generated response |

### Red-Teaming Attack Types
| Category | Attacks |
|----------|---------|
| On-policy | instruction_override, emotional_appeal, role_playing, hypothetical_scenario, authority_impersonation, crescendo_attack |
| Off-policy | jailbreaking, prompt_leakage, topic_derailment, social_engineering, data_extraction |

## Benchmark JSON Format

```json
{
  "agent": "agent_name",
  "story": "Instructions for the LLM-simulated user",
  "starting_sentence": "First message the simulated user sends",
  "goals": {
    "tool_a-1": ["tool_b-1"],
    "tool_b-1": []
  },
  "goal_details": [
    {
      "type": "tool_call",
      "name": "tool_a-1",
      "tool_name": "tool_a",
      "args": {"param": "value"},
      "arg_matching": {"param": "strict"}
    }
  ]
}
```

Argument matching modes: `"strict"` (exact match), `"fuzzy"` (semantic match), `"optional"` (can be omitted).
