FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && pip install ".[rest]"

EXPOSE 8080
ENV SERVICE_PORT=8080

CMD ["real-time-guardrails", "serve", "--host", "0.0.0.0", "--port", "8080"]
