# =============================================================================
# backend-sql-executor — IBM Cloud Code Engine deployment image
# =============================================================================
# Multi-stage build:
#   builder  — installs Python deps + compiles psycopg2 native extension
#   app      — lean runtime with only libpq (no gcc/build tools)
# =============================================================================

# ---- Stage 1: dependency builder ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Build tools needed only to compile psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


# ---- Stage 2: lean runtime image ----
FROM python:3.12-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    PYTHONPATH="/app"

# libpq-dev runtime component only (no gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -u 1001 -ms /bin/bash appuser

WORKDIR /app

COPY --from=builder /venv /venv
COPY tool_sql_executor.py /app/tool_sql_executor.py
COPY sql_validation.py    /app/sql_validation.py
COPY ibmcloud-pg-ca.crt   /app/ibmcloud-pg-ca.crt

USER 1001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:${PORT:-8000}/health || exit 1

CMD ["sh", "-c", "uvicorn tool_sql_executor:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level warning"]
