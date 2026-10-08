# Architecture decisions

## ADR-001 — Keep the frontend dependency-free

Decision: serve static HTML/CSS/JavaScript from FastAPI.

Reason: a single Python container is easier to build and deploy on Code Engine and still supports a polished live dashboard.

## ADR-002 — Kafka as durable Continuous RAG change log

Decision: store raw knowledge and embedding results on Kafka topics.

Reason: demonstrates event-driven knowledge freshness and replay. A Code Engine restart can rebuild its read index without persistent local disk.

## ADR-003 — Demo fallback embedding

Decision: include a dependency-free deterministic embedding for the local profile.

Reason: user already has Confluent Cloud; the base demo should not require another paid AI provider. This mode is explicitly marked as a demo fallback.

## ADR-004 — Confluent Flink is the managed/production profile

Decision: provide SQL using built-in text splitters and `AI_EMBEDDING`.

Reason: keeps chunking/embedding continuously close to the event stream and gives the demo a clear Confluent-native upgrade path.

## ADR-005 — Tableflow is not in the synchronous RAG path

Decision: use Tableflow for historical/analytical materialization.

Reason: RAG freshness and interactive latency should use Kafka/Flink/vector retrieval, while Tableflow addresses open-table analytical access.

## ADR-006 — Optional watsonx generation

Decision: retrieval works independently; watsonx.ai only synthesizes the final grounded response when configured.

Reason: separates fresh data/retrieval architecture from LLM vendor selection and keeps the demo runnable with only Confluent credentials.
