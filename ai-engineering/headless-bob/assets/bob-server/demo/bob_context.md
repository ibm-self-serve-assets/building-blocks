# Bobserver Demo Context

You are running inside the Bobserver container.

## Directories and Files

- Workspace root: `/workspace`
- Read-only bundled sample data: `/app/demo`
- Raw CSV with duplicates: `/workspace/orders_raw.csv`
- Clean CSV target: `/workspace/orders_deduped.csv`
- Seed CSV used only for reset/bootstrap: `/workspace/orders.csv`
- SQLite database target: `/workspace/demo.db`
- Demo reset command: `/app/scripts/reset-demo.sh`

## Available Tools

- Bob Shell: `bob`
- SQLite CLI: `sqlite3`

## Rules

- Create, update, and delete demo artifacts only under `/workspace`.
- Use `/app/demo` as read-only source material.
- Do not treat `/workspace/orders.csv` as the deduplicated output.
- The deduplication step must read `/workspace/orders_raw.csv` and write `/workspace/orders_deduped.csv`.
- When you finish, print the commands you ran, files or tables created, and validation output.
