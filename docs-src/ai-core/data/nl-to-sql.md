# NL to SQL Building Block

**Transform natural language questions into accurate SQL queries using AI, enabling non-technical users to access data.**

## Overview

Convert natural language questions into accurate SQL queries using AI.

### Natural Language Input

Users ask questions in plain English, no SQL knowledge required.

- Conversational interface
- Context-aware understanding
- Multi-turn conversations
- Intent recognition

### AI-Powered Translation

Advanced LLMs convert questions into optimized SQL queries.

- Schema-aware generation
- Query optimization
- Syntax validation
- Error handling

### Instant Results

Execute queries and return results in human-readable format.

- Fast query execution
- Result formatting
- Data visualization
- Export capabilities

## Key Features

### Multi-Database Support

Works with all major database systems.

- PostgreSQL
- MySQL
- SQL Server
- Oracle
- SQLite
- BigQuery

### Schema Understanding

Automatically learns your database structure.

- Table relationship mapping
- Column type inference
- Foreign key detection
- Index optimization

### Security & Validation

Enterprise-grade security and query validation.

- SQL injection prevention
- Permission checking
- Query sanitization
- Audit logging

## Example Queries

### Question: "What were our total sales last quarter?"

```sql
SELECT SUM(amount) as total_sales
FROM sales
WHERE date >= '2025-10-01'
  AND date < '2026-01-01'
```

### Question: "Show me customers who haven't ordered in 6 months"

```sql
SELECT customer_name, last_order_date
FROM customers
WHERE last_order_date < CURRENT_DATE - INTERVAL '6 months'
ORDER BY last_order_date DESC
```

### Question: "Which products are low in stock?"

```sql
SELECT product_name, quantity
FROM inventory
WHERE quantity < reorder_level
ORDER BY quantity ASC
```

### Question: "Top 5 products by revenue this month"

```sql
SELECT product_name, SUM(price * quantity) as revenue
FROM orders
WHERE MONTH(order_date) = MONTH(CURRENT_DATE)
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 5
```

## Use Cases

### Business Intelligence
Empower business users to query data without SQL knowledge.

- Self-service analytics
- Ad-hoc reporting
- Dashboard creation
- Trend analysis

### Customer Support
Enable support teams to quickly access customer data.

- Customer lookup
- Order history
- Issue tracking
- Performance metrics

### Data Exploration
Accelerate data discovery and analysis.

- Schema exploration
- Data profiling
- Pattern discovery
- Quality checks