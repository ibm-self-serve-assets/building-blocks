#!/usr/bin/env sh
# Provision Confluent Cloud via Terraform, write .env, and launch the local UI.
set -eu
cd "$(dirname "$0")/.."
exec python3 scripts/deploy.py up "$@"
