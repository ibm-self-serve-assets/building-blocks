---
name: text2sql-query-optimizer
description: Expert guidance for evaluating and improving IBM watsonx.data Intelligence Text2SQL generated SQL quality — covers model selection (Granite vs Llama), dialect tuning, prompt engineering for SQL, SQL validation patterns, feedback loop design, error diagnosis, and metadata-driven accuracy improvement.
---

# watsonx.data Intelligence Text2SQL Query Optimizer

## Purpose

Expert guidance for evaluating **IBM watsonx.data Intelligence Text2SQL** output quality, diagnosing poor query results, tuning model parameters, and implementing feedback loops to iteratively improve accuracy.

## IBM Cloud Product Coverage

| IBM Cloud Product | Usage |
|---|---|
| watsonx.data Intelligence | Text2SQL API: `/semantic_automation/v1/text_to_sql` |
| IBM watsonx.ai | LLM selection: ibm/granite-3-8b-instruct, meta-llama/llama-3-3-70b-instruct |
| IBM Cloud IAM | Bearer token authentication |

## Rules

- Model selection: `ibm/granite-3-8b-instruct` for SQL-specialist tasks; `meta-llama/llama-3-3-70b-instruct` for complex multi-join queries
- Always validate generated SQL before execution (syntax check, table/column existence)
- Dialect must match target system: `presto`, `postgresql`, `mssql`, `oracle`, `snowflake`
- Set `"raw_output": false` to get structured response with explanation
- Enrich metadata before changing model — metadata quality has highest impact on accuracy

---

## Scope

- Text2SQL model selection and parameter tuning
- Generated SQL validation and safety checks
- Error pattern diagnosis and remediation
- Quality evaluation metrics (exact match, execution accuracy)
- Feedback loop implementation for iterative improvement

---

## Procedure

### Phase 1: Model Selection Guide

| Model | Strengths | Use Case |
|---|---|---|
| `ibm/granite-3-8b-instruct` | SQL-specialist, fast | Standard OLAP queries |
| `meta-llama/llama-3-3-70b-instruct` | Complex reasoning | Multi-table JOINs, sub-queries |
| `ibm/granite-20b-code-instruct` | Code generation | Complex aggregations |

### Phase 2: Text2SQL API Request

```python
import requests

def run_text2sql(query: str, dialect: str, model_id: str, project_id: str, token: str) -> dict:
    url = f"https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/text_to_sql"
    params = {
        "container_id": project_id,
        "container_type": "project",
        "dialect": dialect,
        "model_id": model_id,
    }
    payload = {"query": query, "raw_output": False}
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, params=params, json=payload)
    resp.raise_for_status()
    return resp.json()
```

### Phase 3: SQL Validation

```python
import sqlparse
from sqlparse import tokens as T

def validate_sql(sql: str, dialect: str) -> dict:
    """Basic SQL safety and syntax validation."""
    parsed = sqlparse.parse(sql)
    issues = []

    if not parsed:
        issues.append("No SQL statement generated")
        return {"valid": False, "issues": issues}

    stmt = parsed[0]
    stmt_type = stmt.get_type()

    # Only allow SELECT for read-only Text2SQL
    if stmt_type not in ("SELECT", None):
        issues.append(f"Unexpected statement type: {stmt_type} — only SELECT is permitted")

    # Check for dangerous patterns
    dangerous = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER"]
    sql_upper = sql.upper()
    for keyword in dangerous:
        if keyword in sql_upper:
            issues.append(f"Dangerous keyword detected: {keyword}")

    return {"valid": len(issues) == 0, "issues": issues, "statement_type": stmt_type}
```

### Phase 4: Accuracy Evaluation

```python
def evaluate_text2sql(test_cases: list[dict], project_id: str, token: str) -> dict:
    """
    Evaluate Text2SQL accuracy against a test set.

    test_cases format:
    [{"nl_query": "...", "expected_sql": "...", "dialect": "presto"}]
    """
    total = len(test_cases)
    exact_matches = 0
    results = []

    for case in test_cases:
        result = run_text2sql(case["nl_query"], case["dialect"], "ibm/granite-3-8b-instruct",
                              project_id, token)
        generated = result.get("sql", "").strip().lower()
        expected = case["expected_sql"].strip().lower()

        match = generated == expected
        if match:
            exact_matches += 1

        results.append({
            "query": case["nl_query"],
            "expected": expected,
            "generated": generated,
            "match": match,
        })

    return {
        "total": total,
        "exact_match_accuracy": exact_matches / total if total else 0,
        "results": results,
    }
```

### Phase 5: Common Error Patterns

| Error | Cause | Fix |
|---|---|---|
| "No matches in metadata index" | Project not onboarded | Run `PUT /onboard_for_text_2_sql` first |
| Wrong table name | Missing metadata description | Add table description with exact table name |
| Wrong column aggregation | Missing column description | Add column description with aggregation examples |
| Incorrect JOIN | Missing relationship hint | Add foreign key relationship in table description |
| Dialect error | Wrong dialect parameter | Match dialect to actual data source type |

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| DAI Text2SQL (ca-tor) | `https://api.ca-tor.dai.cloud.ibm.com/semantic_automation/v1/text_to_sql` |
