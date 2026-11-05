# Factory Pulse Streamhouse — Specification Set

These specs describe the solution in enough detail to recreate it. They were reverse-engineered from the code, so where code and older docs disagree, the specs follow the code and flag the difference as an open question.

## Reading order

| # | Spec | Type | Covers |
|---|------|------|--------|
| 1 | [requirements/product-overview.spec.md](requirements/product-overview.spec.md) | Requirements | Vision, personas, journey, glossary, traceability matrix |
| 2 | [requirements/live-monitoring-and-simulation.spec.md](requirements/live-monitoring-and-simulation.spec.md) | Requirements | Plants, telemetry, scenarios, operator actions, SSE, twin, map |
| 3 | [requirements/streaming-analytics-and-ai.spec.md](requirements/streaming-analytics-and-ai.spec.md) | Requirements | Kafka, Flink, governance, Tableflow, RTCE/MCP, AI context |
| 4 | [requirements/deployment-and-operations.spec.md](requirements/deployment-and-operations.spec.md) | Requirements | Local, Docker, Code Engine, Terraform, security |
| 5 | [api/factory-pulse.openapi.yaml](api/factory-pulse.openapi.yaml) | OpenAPI 3.1 | Every HTTP/SSE endpoint |
| 6 | [design/backend-server.design.md](design/backend-server.design.md) | Design | Flask app, simulation, Kafka, config |
| 7 | [design/frontend-ui.design.md](design/frontend-ui.design.md) | Design | React UI, components, styling |
| 8 | [design/digital-twin-simulation.design.md](design/digital-twin-simulation.design.md) | Design | Browser/server simulation, robot arm twin |
| 9 | [design/streaming-platform.design.md](design/streaming-platform.design.md) | Design | Terraform, topics, schemas, Flink SQL |
| 10 | [design/deployment-ops.design.md](design/deployment-ops.design.md) | Design | Dockerfile, deploy scripts, tests, backup |
| 11 | [design/watsonx-orchestrate-agent.design.md](design/watsonx-orchestrate-agent.design.md) | Design | Planned agent integration (not yet implemented) |

## Known cross-cutting findings (verify before rebuilding)

- `server/mcp.py` shadows the `mcp` SDK package when started as `python server/app.py`.
- `tests/simulation.test.js` and one test in `tests/test_deploy.py` target a removed Node server.
- The browser simulation and Python simulation diverge in several behaviours (see the digital-twin design, §9–10).
- Port inconsistency: image 8080, local container 4000, HEALTHCHECK hard-coded to 8080.
- Kafka payloads are plain JSON strings, while the streaming spec describes Schema Registry framing. Confirm which one Flink expects.
- The watsonx Orchestrate agent is a design only; its routes do not exist in `server/app.py`.
