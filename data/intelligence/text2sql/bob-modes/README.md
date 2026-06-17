# Bob Mode for Text-to-SQL

Custom IBM Bob mode configuration for Text-to-SQL development using **IBM watsonx.data Intelligence** on IBM Cloud.

---

## Overview

This Bob mode provides specialized assistance for:

- **watsonx.data Intelligence Text2SQL**: Converting natural language questions to validated, executable SQL using the DAI Text2SQL API
- **Metadata Enrichment**: Table descriptions, column descriptions, synonyms, and query example authoring via the DAI REST API to maximise query accuracy
- **Multi-Dialect SQL**: Presto, PostgreSQL, SQL Server, Oracle, Snowflake dialect support
- **SQL Quality Assurance**: Safety validation, syntax checks, and accuracy evaluation (exact-match + execution accuracy)
- **Deployment**: IBM Code Engine and Red Hat OpenShift setup for FastAPI Text2SQL applications

---

## What's Included

- **[`base-modes/text-to-sql.zip`](base-modes/text-to-sql.zip)**: Bob mode configuration for Text-to-SQL development

---

## Mode Capabilities

- IBM Cloud IAM authentication (API key → Bearer token with auto-refresh)
- watsonx.data Intelligence project onboarding (`PUT /onboard_for_text_2_sql`)
- Text2SQL API call: `POST /v2/text_to_sql/generate` with question, project ID, and dialect
- Table description enrichment via `PUT /metadata/tables/{table_id}`
- Column description, synonym, and query example enrichment
- Model selection guidance (Granite vs Llama for simple vs complex queries)
- SQL safety validation (syntax check, dangerous keyword detection: DROP, DELETE, TRUNCATE)
- Accuracy evaluation: exact-match score and execution accuracy computation
- Error pattern diagnosis: missing metadata, wrong dialect, ambiguous joins
- FastAPI application development for Text2SQL REST endpoints
- IBM Code Engine Dockerfile and deployment configuration
- Red Hat OpenShift deployment YAML generation

---

## When to Use This Mode

- Implementing a natural language to SQL interface for a watsonx.data project
- Enriching table and column metadata to improve Text2SQL accuracy
- Evaluating the quality of generated SQL queries
- Troubleshooting DAI API authentication or Text2SQL failures
- Selecting the best LLM model for SQL query complexity
- Deploying a Text2SQL FastAPI application to IBM Code Engine
- Designing SQL validation middleware for safety and correctness

---

## Installing Bob Modes

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/text-to-sql.zip`](base-modes/text-to-sql.zip)) defines the behavior, expertise, and capabilities of IBM Bob when working with Text-to-SQL development.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/text-to-sql.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/text-to-sql.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.
