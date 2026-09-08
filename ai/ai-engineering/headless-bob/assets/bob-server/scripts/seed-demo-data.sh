#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cp /app/demo/orders_raw.csv /workspace/orders_raw.csv
cp /app/demo/orders.csv /workspace/orders.csv
cp /app/demo/bob_context.md /workspace/bob_context.md

if [ ! -f /workspace/demo.db ]; then
  sqlite3 /workspace/demo.db <<'SQL'
.mode csv
CREATE TABLE orders (
  order_id INTEGER,
  customer TEXT,
  region TEXT,
  amount REAL,
  ordered_at TEXT
);
.import --skip 1 /workspace/orders.csv orders
SQL
fi
