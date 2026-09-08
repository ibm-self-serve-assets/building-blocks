# Text2SQL

**IBM product**: IBM watsonx.data intelligence

Reference assets for converting natural-language questions into SQL using **governed metadata and Text-to-SQL capabilities in IBM watsonx.data intelligence**.

The included FastAPI code is a thin reference wrapper; it does not replace data-source authorization, governance, or SQL review.

## Architecture

```text
User question
     |
     v
Governed metadata / examples
IBM watsonx.data intelligence
     |
     v
   Text-to-SQL
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

## Included assets

| Path | Purpose |
|---|---|
| [`assets/applications/text_to_sql_app/`](assets/applications/text_to_sql_app/) | FastAPI wrapper for Text-to-SQL generation and optional controlled execution |
| [`assets/metadata_enrichment_text2sql/`](assets/metadata_enrichment_text2sql/) | Reference metadata-enrichment flow to improve Text-to-SQL context |
| [`assets/README.md`](assets/README.md) | Product/API setup and onboarding notes |
| [`bob-modes/`](bob-modes/) | IBM Bob Text2SQL mode |
| [`bob-skills/`](bob-skills/) | Metadata-enrichment and SQL-review skills |

## Quick start

```bash
cd assets/applications/text_to_sql_app
cp .env.example .env
# Configure APP_API_KEY, IBM_CLOUD_API_KEY, TEXT_TO_SQL_ENDPOINT,
# project/container values, and any optional database execution settings.
pip install -r requirements.txt
python app.py
# Swagger UI: http://localhost:8080/docs
```

Primary route:

```text
POST /texttosql
```

For onboarding, metadata preparation, and product API examples, read [`assets/README.md`](assets/README.md).

## Developer guidance

Good Text2SQL output depends heavily on context. Improve quality by supplying:

- accurate table/column metadata;
- business descriptions and terms;
- representative SQL examples;
- relationship/join information;
- dialect information;
- clear boundaries for which schemas/tables can be queried.

## Production guardrails

- Generated SQL is not an authorization mechanism.
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
