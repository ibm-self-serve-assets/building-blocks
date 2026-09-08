#!/usr/bin/env bash
set -euo pipefail

/app/scripts/seed-demo-data.sh

exec python3.11 -m uvicorn bobserver.main:app --host 0.0.0.0 --port "${PORT:-8080}"
