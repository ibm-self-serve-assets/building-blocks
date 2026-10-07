# =============================================================================
# schema-retriever — IBM Cloud Code Engine deployment image
# =============================================================================
# Multi-stage build:
#   builder  — installs Python deps into an isolated venv (no pip in final image)
#   app      — lean runtime image, non-root, no build tools
#
# Build context is prepared by build.sh, which stages these files here:
#   schema_retriever_opensearch.py  ← from schema_retriever/
#   embedders.py                    ← from embedding/
#   connectors/                     ← from embedding/connectors/
#   requirements.txt                ← from schema_retriever/
#
# embedders.py is placed at /app/embedders.py so the flat import
#   "from embedders import ..."  in schema_retriever_opensearch.py resolves
#   correctly via PYTHONPATH=/app.
# =============================================================================

# ---- Stage 1: dependency builder ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt .

# Install into an isolated venv so the final stage only copies /venv
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


# ---- Stage 2: lean runtime image ----
FROM python:3.12-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    # /app is on PYTHONPATH so "from embedders import ..." resolves
    PYTHONPATH="/app"

# curl for the HEALTHCHECK — no build tools in runtime image
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Non-root user (UID 1001 avoids conflicts with common host UIDs)
RUN useradd -u 1001 -ms /bin/bash appuser

WORKDIR /app

# Copy venv from builder stage
COPY --from=builder /venv /venv

# Copy application source (staged into build context by build.sh)
COPY schema_retriever.py             /app/schema_retriever.py
COPY schema_retriever_opensearch.py  /app/schema_retriever_opensearch.py
COPY schema_retriever_pgvector.py    /app/schema_retriever_pgvector.py
COPY embedders.py                    /app/embedders.py
COPY connectors/                     /app/connectors/
COPY ibmcloud-pg-ca.crt              /app/ibmcloud-pg-ca.crt

# Drop to non-root before the process starts
USER 1001

# Code Engine injects $PORT at runtime; default to 8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -sf http://localhost:${PORT:-8080}/health || exit 1

CMD ["sh", "-c", "uvicorn schema_retriever:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --log-level warning"]
