# Production Dockerfile for Sample SSE MCP Server
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run with python directly (simpler for testing)
CMD ["mcp-instana", "--transport", "streamable-http", "--log-level", "DEBUG", "--tools", "app,events"]
