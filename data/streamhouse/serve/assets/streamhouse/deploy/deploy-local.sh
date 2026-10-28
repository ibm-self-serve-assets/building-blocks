#!/usr/bin/env sh
# Build and run Factory Pulse as a single container (frontend + API) with podman.
# Usage: deploy/deploy-local.sh [up|down|logs]   (default: up)
# Open http://localhost:4000. Configuration comes from the repo-root .env (required for "up").
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ENV_FILE="$ROOT/.env"

IMAGE="${IMAGE:-factory-pulse}"
NAME="${NAME:-factory-pulse}"
HOST_PORT="${HOST_PORT:-4000}"
ENGINE="${CONTAINER_ENGINE:-podman}"

command -v "$ENGINE" >/dev/null 2>&1 || { echo "[deploy-local] $ENGINE not found." >&2; exit 1; }

# Value of KEY from .env (empty if absent), CRLF-safe, surrounding quotes stripped. Never executes .env.
env_value() {
  sed -n "s/^[[:space:]]*$1=//p" "$ENV_FILE" | tail -n 1 | tr -d '\r' | sed -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/"
}

case "${1:-up}" in
  up)
    [ -f "$ENV_FILE" ] || { echo "[deploy-local] $ENV_FILE not found. Create it (cp .env.example .env) and rerun." >&2; exit 1; }
    echo "[deploy-local] Using $ENV_FILE"
    # VITE_* values are public and baked into the frontend bundle at build time.
    "$ENGINE" build -t "$IMAGE" -f deploy/Dockerfile \
      --build-arg "VITE_GOOGLE_MAPS_API_KEY=$(env_value VITE_GOOGLE_MAPS_API_KEY)" \
      --build-arg "VITE_GOOGLE_MAPS_MAP_ID=$(env_value VITE_GOOGLE_MAPS_MAP_ID)" .
    "$ENGINE" rm -f "$NAME" >/dev/null 2>&1 || true
    # Everything in .env becomes the container environment; PORT is forced to the container port.
    "$ENGINE" run -d --name "$NAME" -p "$HOST_PORT:4000" --env-file "$ENV_FILE" -e PORT=4000 "$IMAGE"
    echo "[deploy-local] Running at http://localhost:$HOST_PORT  (logs: $0 logs, stop: $0 down)"
    ;;
  down) "$ENGINE" rm -f "$NAME" ;;
  logs) "$ENGINE" logs -f "$NAME" ;;
  *) echo "Usage: $0 [up|down|logs]" >&2; exit 1 ;;
esac
