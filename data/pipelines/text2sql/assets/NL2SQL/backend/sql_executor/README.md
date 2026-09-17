# sql_executor — SQL Execution API (called by LLM)

**Always-on FastAPI service.** The LLM calls `POST /run-sql` with a generated SELECT statement and receives the query results.

## What it does

- Accepts a SQL string and validates it is **read-only** (SELECT / EXPLAIN / WITH … SELECT only).
- Rejects queries containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, etc.
- Automatically injects `LIMIT` if not present (capped at `MAX_ROWS`).
- Executes the query via a connection pool with a per-statement timeout.
- Returns sanitised errors — Postgres internals are never forwarded verbatim to the caller.

## Files

| File | Purpose |
|---|---|
| `tool_sql_executor.py` | Hardened FastAPI app — read-only SQL execution service |

## Usage

```bash
cd NL2SQL/backend/sql_executor
pip install -r requirements.txt
cp .env.example .env   # fill in target DB credentials

uvicorn tool_sql_executor:app --host 0.0.0.0 --port 8000
```

## API

### `POST /run-sql`

```json
{ "sql": "SELECT order_id, status FROM public.orders WHERE customer_id = 42" }
```

Returns:
```json
{
  "sql": "SELECT order_id, status FROM public.orders WHERE customer_id = 42 LIMIT 100",
  "result": [{"order_id": 1, "status": "PAID"}, ...]
}
```

### `GET /health`

Returns `{"ok": true, "db": "mydb", "host": "..."}` when the pool is healthy.

## Deployment (IBM Cloud Code Engine)

See [`docker-build/backend/sql-executor/`](../../docker-build/backend/sql-executor/) for the Dockerfile, `ce-app.yaml`, and `build.sh`.
