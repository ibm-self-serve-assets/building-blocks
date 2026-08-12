---
name: text2sql-metadata-enrichment
description: Expert guidance for enriching IBM watsonx.data Intelligence metadata to maximise Text2SQL accuracy — covers adding business descriptions, column synonyms, table relationships, and semantic hints via the DAI REST API, and using the metadata_enrichment Python scripts in the building-blocks repository.
---

# watsonx.data Intelligence Text2SQL Metadata Enrichment

## Purpose

Expert guidance for enriching metadata in **IBM watsonx.data Intelligence** projects to maximise **Text2SQL** query accuracy. The watsonx.data Intelligence Text2SQL service uses metadata (table descriptions, column descriptions, synonyms, relationships) to understand natural language queries and generate correct SQL.

## IBM Cloud Product Coverage

| IBM Cloud Product | Usage |
|---|---|
| watsonx.data Intelligence (DAI) | Text2SQL API; metadata enrichment; project/asset management |
| IBM Cloud IAM | POST /identity/token (apikey grant) |
| IBM watsonx.ai | LLM used for SQL generation (meta-llama/llama-3-3-70b-instruct default) |

## Rules

- DAI base URL: `https://api.{region}.dai.cloud.ibm.com`
- Text2SQL endpoint: `GET /semantic_automation/v1/text_to_sql`
- Onboarding endpoint: `PUT /semantic_automation/v1/onboard_for_text_2_sql`
- Always onboard the project **before** importing data assets
- Metadata enrichment increases SQL accuracy significantly — always add table/column descriptions
- Supported dialects: `presto`, `postgresql`, `mssql`, `oracle`, `presto_sql`, `snowflake`

---

## Scope

- watsonx.data Intelligence project onboarding for Text2SQL
- Table and column metadata enrichment via DAI REST API
- Adding synonyms, business descriptions, and relationship hints
- Evaluating and improving Text2SQL query accuracy
- Feedback loop design for iterative quality improvement

---

## Procedure

### Phase 1: Onboard Project for Text2SQL

```bash
curl -X PUT 'https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/onboard_for_text_2_sql' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{"containers": [{"container_id": "{PROJECT_ID}", "container_type": "project"}]}'
```

### Phase 2: Import Data Assets

1. Navigate to your watsonx.data Intelligence project
2. Add data connection (Presto, PostgreSQL, Snowflake, etc.)
3. Import specific tables as project assets

### Phase 3: Metadata Enrichment — Table Description

```python
# PATCH /v2/assets/{asset_id}/attributes
# Adds business description to a table asset
payload = {
    "description": "Contains customer purchase transactions. Each row is one order line item. "
                   "Primary key is ORDER_ID. Joined with CUSTOMERS on CUSTOMER_ID."
}
requests.patch(
    f"{WXDI_BASE}/v2/assets/{asset_id}/attributes",
    headers={"Authorization": f"Bearer {token}"},
    params={"project_id": project_id},
    json=payload,
)
```

### Phase 4: Column Synonyms

```python
# Synonyms help Text2SQL map natural language terms to column names
column_metadata = {
    "ORDER_DATE": {
        "synonyms": ["purchase date", "transaction date", "when ordered"],
        "description": "Date when the customer placed the order (YYYY-MM-DD format)"
    },
    "CUSTOMER_ID": {
        "synonyms": ["client id", "buyer id", "account number"],
        "description": "Unique identifier for the customer — foreign key to CUSTOMERS.ID"
    },
    "AMOUNT": {
        "synonyms": ["price", "cost", "total", "revenue", "sale value"],
        "description": "Total order amount in USD including tax"
    }
}
```

### Phase 5: Run Text2SQL Query

```bash
curl 'https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/text_to_sql?container_id={PROJECT_ID}&container_type=project&dialect=presto&model_id=meta-llama%2Fllama-3-3-70b-instruct' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{"query": "What were the top 10 customers by total sales last month?", "raw_output": true}'
```

### Phase 6: Quality Improvement Checklist

- [ ] Add description to every table asset
- [ ] Add description and synonyms to every column
- [ ] Document all foreign key relationships
- [ ] Add examples of natural language queries in table description
- [ ] Use domain-specific terminology in synonyms
- [ ] Test with representative queries and measure accuracy

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| DAI Text2SQL (ca-tor) | `https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/text_to_sql` |
| DAI Onboard (ca-tor) | `https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/onboard_for_text_2_sql` |
