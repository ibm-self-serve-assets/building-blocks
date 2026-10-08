# Confluent Cloud setup

Research checked against official Confluent documentation on 2026-09-22.

## Minimum setup: Kafka-only Continuous RAG demo

You need:
- an existing Confluent Cloud environment,
- a Kafka cluster,
- cluster bootstrap endpoint,
- Kafka API key and secret.

Get client configuration from:
**Environment → Kafka cluster → Clients → Python**.

The Python client uses:

```text
security.protocol=SASL_SSL
sasl.mechanisms=PLAIN
sasl.username=<Kafka API key>
sasl.password=<Kafka API secret>
```

Official quick start:
https://docs.confluent.io/cloud/current/client-apps/config-client.html

After putting the values in `.env`, verify authentication without exposing the secret:

```bash
python scripts/verify_confluent.py
```

The verifier lists cluster/topic metadata only; it never prints the API secret.

## Topic bootstrap

For the local demo profile:

```bash
python scripts/create_topics.py --profile local
```

For the Flink-managed embedding profile:

```bash
python scripts/create_topics.py --profile flink
```

The Flink profile deliberately leaves the derived embedding topics to Flink SQL DDL.

## Schema Registry profile

Set:

```bash
SERIALIZATION_MODE=schema-registry-json
CONFLUENT_SCHEMA_REGISTRY_URL=...
CONFLUENT_SCHEMA_REGISTRY_API_KEY=...
CONFLUENT_SCHEMA_REGISTRY_API_SECRET=...
```

The application uses Confluent's JSON Schema serializer and auto-registers topic value schemas for the relevant published topics.

Official Python serializer documentation:
https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html

## Flink-managed Continuous RAG

Confluent Cloud Flink currently provides:
- `ML_RECURSIVE_TEXT_SPLITTER` and other built-in text splitters,
- `AI_EMBEDDING` for registered embedding models,
- `VECTOR_SEARCH_AGG` for supported external vector stores.

Run:

```text
infra/flink/continuous_rag.sql
```

Alternatively, Confluent Cloud's **Create embeddings** Flink Action can generate the managed embedding statement from the console, including optional chunking. The SQL file remains useful when you want the pipeline version-controlled with the application.

Official references:
- https://docs.confluent.io/cloud/current/flink/reference/functions/ml-preprocessing-functions.html
- https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html
- https://docs.confluent.io/cloud/current/ai/external-tables/vector-search.html

## Tableflow

Recommended for the analytical side of the demo. Enable Tableflow on `factory.state` and `factory.exceptions` after the topics have a supported schema.

Confluent-managed storage is the simplest demo option. Tableflow can expose Kafka topics as Iceberg tables; Delta Lake is also supported in applicable configurations.

Official references:
- https://docs.confluent.io/cloud/current/topics/tableflow/overview.html
- https://docs.confluent.io/cloud/current/topics/tableflow/get-started/quick-start-managed-storage.html

## Which API key is which?

- **Kafka API key**: runtime producer/consumer access to one Kafka cluster. Required by FactoryPulse.
- **Schema Registry API key**: schema serialization/deserialization. Required only for `schema-registry-json` profile.
- **Cloud API key**: management APIs. Not required by the app runtime.
- **Tableflow API key**: used by readers that access the Iceberg REST catalog. Not required for the UI itself.
