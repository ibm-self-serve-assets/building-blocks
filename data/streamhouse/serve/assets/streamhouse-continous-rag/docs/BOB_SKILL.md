# IBM Bob skill

This repository includes a project-scoped Bob skill:

```text
.bob/skills/streamhouse-continuous-rag/SKILL.md
```

IBM Bob project skills are discovered under `.bob/skills/<skill-name>/SKILL.md`. The skill uses YAML front matter with `name` and `description`, followed by the workflow instructions Bob should follow.

Official Bob documentation:
https://bob.ibm.com/docs/ide/features/skills

## Use

Open this repository in IBM Bob. In Agent/Advanced mode, invoke:

```text
/streamhouse-continuous-rag
```

Then ask, for example:

```text
Review the Continuous RAG pipeline and add a new source for Maximo work-order closure notes without exposing credentials.
```

or:

```text
Use the Streamhouse skill to convert the local embedding path to Confluent Flink AI_EMBEDDING and update the deployment documentation.
```

## What the skill enforces

- Confluent Cloud remains the event backbone.
- Continuous knowledge changes are treated as events, not nightly batch jobs.
- The same embedding model is used for chunks and questions.
- RAG answers preserve evidence/grounding.
- secrets stay in environment variables/Code Engine secrets.
- Streamhouse analytical materialization is separated from the low-latency retrieval path.
- relevant code, tests, docs, and diagrams are updated together.
