FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY . .

RUN uv sync --frozen --no-dev

EXPOSE 9248

CMD ["uv", "run", "building-blocks-mcp-remote-marketplace"]
