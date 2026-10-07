import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import jaydebeapi
import prestodb
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from custom_types.texttosqlRequest import TextToSQLRequest
from custom_types.texttosqlResponse import TextToSQLResponse

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="IBM watsonx.data intelligence Text2SQL reference API")

cors_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "APP-API-KEY"],
    )

API_KEY_NAME = "APP-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

_token: str | None = None
_token_updated_at: datetime | None = None


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable is not set: {name}")
    return value


def _tls_verify_value() -> bool | str:
    """Use system trust by default, or a user-provided CA bundle."""
    return os.getenv("REQUESTS_CA_BUNDLE") or True


def get_auth_token(api_key: str) -> str:
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=30,
        verify=_tls_verify_value(),
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("IBM IAM response did not contain an access token")
    return token


def get_headers() -> dict[str, str]:
    global _token, _token_updated_at
    now = datetime.now(timezone.utc)
    if _token is None or _token_updated_at is None or now - _token_updated_at > timedelta(minutes=20):
        _token = get_auth_token(_require_env("IBM_CLOUD_API_KEY"))
        _token_updated_at = now
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {_token}",
    }


async def get_api_key(value: str | None = Security(api_key_header)) -> str:
    configured = os.getenv("APP_API_KEY")
    if configured and value == configured:
        return value
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Could not validate application credentials.",
    )


def validate_read_only_sql(sql: str) -> str:
    """Conservative guardrail for the optional demo execution path."""
    normalized = sql.strip().rstrip(";").strip()
    if not normalized:
        raise ValueError("Generated SQL is empty")
    if ";" in normalized:
        raise ValueError("Multiple SQL statements are not allowed")
    if not re.match(r"^(select|with)\b", normalized, flags=re.IGNORECASE):
        raise ValueError("Only SELECT/CTE queries are allowed")

    forbidden = re.compile(
        r"\b(insert|update|delete|merge|drop|alter|truncate|create|grant|revoke|call|execute|replace)\b",
        flags=re.IGNORECASE,
    )
    if forbidden.search(normalized):
        raise ValueError("Generated SQL contains a disallowed statement")
    return normalized


def get_db_connection(dbtype: str):
    if dbtype == "db2":
        driver_path = _require_env("DB2_JDBC_DRIVER_PATH")
        host = _require_env("DB2_HOSTNAME")
        port = _require_env("DB2_PORT")
        database = _require_env("DB2_DATABASE")
        schema = os.getenv("DB2_SCHEMA", "")
        user = _require_env("DB2_USERNAME")
        password = _require_env("DB2_PASSWORD")
        url = f"jdbc:db2://{host}:{port}/{database}:sslConnection=true;"
        if schema:
            url = f"jdbc:db2://{host}:{port}/{database}:currentSchema={schema};sslConnection=true;"
        return jaydebeapi.connect(
            "com.ibm.db2.jcc.DB2Driver",
            url,
            [user, password],
            driver_path,
        )

    if dbtype == "presto":
        connection = prestodb.dbapi.connect(
            host=_require_env("PRESTO_HOSTNAME"),
            port=int(_require_env("PRESTO_PORT")),
            user=_require_env("PRESTO_USERNAME"),
            catalog=_require_env("PRESTO_CATALOG"),
            schema=_require_env("PRESTO_SCHEMA"),
            http_scheme="https",
            auth=prestodb.auth.BasicAuthentication(
                _require_env("PRESTO_USERNAME"),
                _require_env("PRESTO_PASSWORD"),
            ),
        )
        ca_bundle = os.getenv("PRESTO_CA_BUNDLE")
        if ca_bundle:
            connection._http_session.verify = ca_bundle
        return connection

    raise ValueError("dbtype must be 'db2' or 'presto' for this IBM reference implementation")


def execute_query(sql: str, dbtype: str) -> list[dict[str, Any]]:
    if os.getenv("SQL_EXECUTION_ENABLED", "false").lower() != "true":
        raise ValueError("SQL execution is disabled. Set SQL_EXECUTION_ENABLED=true only for a controlled environment.")
    safe_sql = validate_read_only_sql(sql)
    conn = get_db_connection(dbtype)
    try:
        cursor = conn.cursor()
        cursor.execute(safe_sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/")
def index():
    return {"service": "IBM watsonx.data intelligence Text2SQL reference API"}


@app.post("/texttosql", response_model=TextToSQLResponse)
def text_to_sql(request: TextToSQLRequest, _: str = Security(get_api_key)):
    endpoint = _require_env("TEXT_TO_SQL_ENDPOINT")
    payload = {"query": request.question, "raw_output": request.raw_output}
    params = {
        "container_id": request.container_id,
        "container_type": request.container_type,
        "dialect": request.dialect,
        "top_n": request.top_n,
    }

    response = requests.post(
        endpoint,
        headers=get_headers(),
        json=payload,
        params=params,
        timeout=60,
        verify=_tls_verify_value(),
    )
    response.raise_for_status()
    data = response.json()

    queries = data.get("generated_sql_queries") or []
    if not queries:
        raise HTTPException(status_code=502, detail="Text-to-SQL service did not return a generated SQL query")

    generated = queries[0]
    sql = generated.get("sql", "")
    result: dict[str, Any] = {
        "nl_question": request.question,
        "sql_query": sql,
        "score": generated.get("score"),
        "model_id": data.get("model_id"),
        "resource_usage": data.get("resource_usage"),
    }

    if request.raw_output and "wx_ai_raw_output" in data:
        result["raw_output"] = data["wx_ai_raw_output"]

    if request.db_execute:
        try:
            result["query_response"] = execute_query(sql, request.dialect)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info("Text2SQL request completed; dialect=%s execute=%s", request.dialect, request.db_execute)
    return TextToSQLResponse(response=result)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), reload=False)
