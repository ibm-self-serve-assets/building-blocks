# Build frontend (node) and run Python backend in a single container.
# Stage 1: compile the Vite frontend.
FROM node:22-alpine AS build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
# sql.js imports ../flink/*.sql (aliased to /app/flink in vite.config.js)
COPY flink/ /app/flink/
ARG VITE_GOOGLE_MAPS_API_KEY=
ARG VITE_GOOGLE_MAPS_MAP_ID=
ENV VITE_GOOGLE_MAPS_API_KEY=${VITE_GOOGLE_MAPS_API_KEY}
ENV VITE_GOOGLE_MAPS_MAP_ID=${VITE_GOOGLE_MAPS_MAP_ID}
RUN npm run build

# Stage 2: Python runtime serving the API and compiled frontend together.
FROM python:3.11-slim
WORKDIR /app
ENV PORT=8080 STREAM_MODE=mock PYTHONUNBUFFERED=1
COPY deploy/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY server/ ./server/
COPY --from=build /app/frontend/dist ./frontend/dist
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/api/health',timeout=3).status==200 else 1)"
CMD ["python", "server/app.py"]
