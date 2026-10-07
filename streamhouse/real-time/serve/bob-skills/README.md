# Serve -- Bob Skills

Bob skills for IBM Confluent Real-Time Context Engine (RTCE), Tableflow, and Continuous RAG patterns.

## Available skills

| Skill | ZIP | Description |
|---|---|---|
| `streamhouse-continuous-rag` | [`streamhouse-continuous-rag.zip`](streamhouse-continuous-rag.zip) | Design and implement Continuous RAG pipelines that combine Streamhouse live operational state with enterprise knowledge to keep AI agents grounded in real-time context |

## Planned skills

A `rtce-context-builder` skill covering RTCE materialized view design, MCP endpoint configuration, and live-state schema design, and a `tableflow-iceberg-setup` skill covering Confluent Tableflow configuration and watsonx.data Iceberg integration are planned here.

## Installing skills

1. Download the `.zip` file.
2. Copy the skill folder to `~/.bob/skills` (global) or `<project>/.bob/skills` (project-level).
3. Reload IBM Bob -- the skill is available in conversation.
