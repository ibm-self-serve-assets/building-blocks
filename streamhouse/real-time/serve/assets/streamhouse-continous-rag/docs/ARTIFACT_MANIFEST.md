# Artifact manifest

This repository is organized so the demo, architecture, Bob skill, and deployment material travel together.

| Area | Artifact | Purpose |
|---|---|---|
| Application | `app/main.py` | FastAPI API, SSE feed, demo orchestration |
| Runtime config | `app/config.py`, `.env.example` | Confluent, RAG, watsonx, topic configuration |
| Continuous RAG | `app/services/rag.py` | local continuous indexer, managed query-embedding broker |
| Retrieval | `app/services/vector_index.py` | Kafka-replayed demo vector read model with latest-document filtering |
| Confluent | `app/services/kafka.py` | Kafka producer/consumer and optional Schema Registry serialization |
| UI | `app/static/` | dark enterprise dashboard, RAG evidence UI, live event views |
| Schemas | `app/schemas/` | JSON Schema contracts used by optional Schema Registry profile |
| Flink | `infra/flink/continuous_rag.sql` | continuous chunk + embedding path |
| Vector search | `infra/flink/external_vector_search_example.sql` | production-scale `VECTOR_SEARCH_AGG` pattern |
| Code Engine | `deploy/Dockerfile`, `infra/code-engine/deploy.sh` | Python 3.12 image and IBM Cloud deployment |
| Bob skill | `.bob/skills/streamhouse-continuous-rag/` | project-scoped Streamhouse/Continuous RAG development skill |
| Demo data | `demo_knowledge/` | synthetic SOP/work-order knowledge |
| Demo scripts | `scripts/` | topic creation, credential verification, seeding, simulation |
| Tests | `tests/` | chunking, embedding, retrieval/latest-version behavior |
| Architecture | `docs/ARCHITECTURE.md` | system boundaries and topic model |
| Setup | `docs/CONFLUENT_SETUP.md` | Confluent credentials, topics, Flink/Tableflow setup |
| Deployment | `docs/DEPLOY_CODE_ENGINE.md` | Code Engine runbook |
| Security | `docs/SECURITY.md` | secret and demo security notes |
| Demo | `docs/DEMO_SCRIPT.md` | 8–10 minute presentation flow |
| Bob | `docs/BOB_SKILL.md` | skill location and usage |
| API spec | `specs/API_SPEC.md` | endpoint contract; runtime OpenAPI at `/openapi.json` |
| UI spec | `specs/UI_SPEC.md` | visual/interaction specification |
| Technical spec | `specs/TECHNICAL_SPEC.md` | runtime stack, service contracts |
