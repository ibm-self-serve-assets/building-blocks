# Text2SQL

**IBM product**: IBM watsonx.data intelligence

Reference assets for converting natural-language questions into SQL using governed enterprise metadata. The IBM product remains responsible for Text-to-SQL generation; the included application is a thin reference wrapper.

## Included assets

| Path | Purpose |
|---|---|
| [`assets/applications/text_to_sql_app/`](assets/applications/text_to_sql_app/) | Secured FastAPI reference wrapper for Text-to-SQL generation and optional controlled execution |
| [`assets/metadata_enrichment_text2sql/`](assets/metadata_enrichment_text2sql/) | Metadata enrichment/reference flow for improving Text-to-SQL context |
| [`bob-modes/`](bob-modes/) | IBM Bob Text2SQL mode |
| [`bob-skills/`](bob-skills/) | IBM Bob skills for metadata context and query review |

## Quick start

```bash
cd assets/applications/text_to_sql_app
cp .env.example .env
# Set APP_API_KEY, IBM_CLOUD_API_KEY, TEXT_TO_SQL_ENDPOINT and project values.
pip install -r requirements.txt
python app.py
# Swagger UI: http://localhost:8080/docs
```

Primary route:

```text
POST /texttosql
```

## Production guardrails

- Generated SQL is not an authorization mechanism. Data-source permissions remain authoritative.
- Keep `SQL_EXECUTION_ENABLED=false` unless controlled execution is explicitly required.
- The reference execution path permits only a single `SELECT`/CTE query and rejects common DDL/DML keywords.
- Use read-only database credentials, row/column controls, query/resource limits, and audit logging.
- Keep TLS verification enabled; use CA bundles rather than `verify=False`.
- Enrich metadata and provide representative SQL examples to improve generation accuracy.
- Review IBM product status/limitations before production use; availability can differ by deployment/version.

## IBM references

- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- Data intelligence natural-language query settings: https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=tools-data-intelligence
- Additional context for Text-to-SQL: https://www.ibm.com/docs/en/watsonx/wdi/2.2.x?topic=asset-providing-additional-context-text-sql-conversions
