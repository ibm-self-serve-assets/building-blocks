#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace

cp /app/demo/orders_raw.csv /workspace/orders_raw.csv
cp /app/demo/orders.csv /workspace/orders.csv
cp /app/demo/bob_context.md /workspace/bob_context.md

rm -f \
  /workspace/orders_deduped.csv \
  /workspace/orders_export.csv \
  /workspace/regional_order_summary.csv \
  /workspace/demo.db

cat <<'TEXT'
Demo reset complete.

Restored:
  - /workspace/orders_raw.csv
  - /workspace/orders.csv
  - /workspace/bob_context.md

Removed:
  - /workspace/orders_deduped.csv
  - /workspace/orders_export.csv
  - /workspace/regional_order_summary.csv
  - /workspace/demo.db
TEXT
