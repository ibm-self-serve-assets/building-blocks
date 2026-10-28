#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
exec python3 scripts/start.py "$@"
