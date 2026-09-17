# Text2SQL

**IBM product**: IBM watsonx.data intelligence

Reference assets for converting natural-language questions into SQL. Two complementary approaches are included:

- **`watsonx-text2sql`** — uses the managed Text-to-SQL API in IBM watsonx.data intelligence with governed metadata.
- **`NL2SQL`** — a self-contained custom pipeline with semantic schema retrieval (OpenSearch k-NN or pgvector) and hardened read-only SQL execution, targeting PostgreSQL and IBM Db2.

## Architecture

### watsonx-text2sql

```text
User question
     |
     v
Governed metadata / examples
IBM watsonx.data intelligence
     |
     v
   Text-to-SQL API
     |
     v
SQL validation / policy gate
     |
     +----> return SQL
     |
     +----> optional controlled execution
                    |
                    v
               IBM data source
```

### NL2SQL

```text
User question
     |
     v
Schema Retriever (FastAPI)
  OpenSearch k-NN / pgvector
     |
     v
LLM SQL generation
     |
     v
SQL Executor (FastAPI)
  AST-based safety validation
     |
     v
IBM data source (PostgreSQL / Db2)
```

## Included assets

### `assets/watsonx-text2sql/` — watsonx.data Intelligence Text-to-SQL

Built on the IBM watsonx.data intelligence managed Text-to-SQL API. Uses governed metadata and the platform's native SQL generation endpoint.

| Path | Purpose |
|---|---|
| [`assets/watsonx-text2sql/applications/text_to_sql_app/`](assets/watsonx-text2sql/applications/text_to_sql_app/) | FastAPI wrapper for Text-to-SQL generation and optional controlled execution |
| [`assets/watsonx-text2sql/metadata_enrichment_text2sql/`](assets/watsonx-text2sql/metadata_enrichment_text2sql/) | Reference metadata-enrichment flow to improve Text-to-SQL context |
| [`assets/watsonx-text2sql/README.md`](assets/watsonx-text2sql/README.md) | Product/API setup and onboarding notes |

### `assets/NL2SQL/` — Custom NL2SQL with Schema Retrieval

A self-contained NL-to-SQL system using semantic schema retrieval and hardened read-only SQL execution.

| Path | Purpose |
|---|---|
| [`assets/NL2SQL/embedding/`](assets/NL2SQL/embedding/) | Schema introspection and vector ingestion pipeline |
| [`assets/NL2SQL/backend/schema_retriever/`](assets/NL2SQL/backend/schema_retriever/) | FastAPI semantic schema retrieval service |
| [`assets/NL2SQL/backend/sql_executor/`](assets/NL2SQL/backend/sql_executor/) | FastAPI hardened read-only SQL execution service |
| [`assets/NL2SQL/setup/`](assets/NL2SQL/setup/) | One-time OpenSearch / pgvector index setup |
| [`assets/NL2SQL/docker-build/`](assets/NL2SQL/docker-build/) | Dockerfiles and IBM Cloud Code Engine deployment scripts |
| [`assets/NL2SQL/PLAYBOOK.md`](assets/NL2SQL/PLAYBOOK.md) | Operational runbook — troubleshooting and maintenance |
| [`assets/NL2SQL/README.md`](assets/NL2SQL/README.md) | Full NL2SQL quickstart and API reference |

### IBM Bob extensions

| Path | Purpose |
|---|---|
| [`bob-modes/`](bob-modes/) | IBM Bob Text2SQL mode |
| [`bob-skills/text2sql-metadata-enrichment.zip`](bob-skills/text2sql-metadata-enrichment.zip) | Bob skill — metadata enrichment for Text-to-SQL context |
| [`bob-skills/text2sql-query-optimizer.zip`](bob-skills/text2sql-query-optimizer.zip) | Bob skill — SQL query review and optimisation |

## Quick start

### watsonx-text2sql

```bash
cd assets/watsonx-text2sql/applications/text_to_sql_app
cp .env.example .env
# Configure APP_API_KEY, IBM_CLOUD_API_KEY, TEXT_TO_SQL_ENDPOINT,
# project/container values, and any optional database execution settings.
pip install -r requirements.txt
python app.py
# Swagger UI: http://localhost:8080/docs
```

Primary route: `POST /texttosql`

For onboarding, metadata preparation, and product API examples, see [`assets/watsonx-text2sql/README.md`](assets/watsonx-text2sql/README.md).

### NL2SQL

```bash
cd assets/NL2SQL
cp .env.example .env
# Edit .env with your credentials

# One-time index setup (OpenSearch default)
VECTOR_BACKEND=opensearch python setup.py

# Ingest schemas
python embedding/ingest.py

# Start services
uvicorn backend.schema_retriever.schema_retriever:app --host 0.0.0.0 --port 8080
uvicorn backend.sql_executor.tool_sql_executor:app --host 0.0.0.0 --port 8000
```

See [`assets/NL2SQL/README.md`](assets/NL2SQL/README.md) for the full quickstart and [`assets/NL2SQL/PLAYBOOK.md`](assets/NL2SQL/PLAYBOOK.md) for operational guidance.

## Developer guidance

Good Text-to-SQL output depends heavily on context. Improve quality by supplying:

- accurate table/column metadata;
- business descriptions and terms;
- representative SQL examples;
- relationship/join information;
- dialect information;
- clear boundaries for which schemas/tables can be queried.

## Production guardrails

- Generated SQL is not an authorization mechanism.
- Never commit `.env` files — use `.env.example` as the template and populate values locally.
- Keep `SQL_EXECUTION_ENABLED=false` unless controlled execution is explicitly required.
- Use read-only database credentials where execution is enabled.
- Enforce row/column controls in the underlying data platform.
- Validate the generated SQL before execution.
- Restrict DDL/DML when the use case only needs analytics queries.
- Apply query timeout/resource limits and audit logging.
- Keep TLS verification enabled.

## IBM references

- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- watsonx.data intelligence documentation: https://www.ibm.com/docs/en/watsonx/wdi/2.4.x
- Text-to-SQL installation capability setting: https://www.ibm.com/docs/en/software-hub/5.4.x?topic=services-specifying-installation-options
