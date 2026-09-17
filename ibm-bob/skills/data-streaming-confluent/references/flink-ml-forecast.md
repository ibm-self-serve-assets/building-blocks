# Confluent Flink SQL ML_FORECAST() Reference

## Purpose

Guide for implementing time-series forecasting in Confluent Cloud using the
built-in `ML_FORECAST()` function in Flink SQL. Covers the function's return
type, ARIMA auto-mode, array unpacking patterns, common failure modes, and
how to build a complete multi-step forecast pipeline from a streaming source.

---

## What ML_FORECAST() Is

`ML_FORECAST()` is a **streaming window function** built into Confluent's
Flink SQL runtime. It fits an ARIMA (AutoRegressive Integrated Moving Average)
model to a time series and returns a **one-step-ahead prediction** — the
predicted value for the next time step given all observed history up to the
current row.

It is **not** a batch forecasting function. It runs continuously as new events
arrive and re-fits the model each time a new data point is observed.

---

## Function Signature

```sql
ML_FORECAST(
  value_column,       -- DOUBLE: the metric to forecast
  time_column,        -- TIMESTAMP: the time axis (must be ordered)
  options_json        -- STRING: JSON configuration object
) OVER (
  PARTITION BY group_column
  ORDER BY time_column
  RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

### Options JSON keys

| Key | Type | Default | Description |
|---|---|---|---|
| `minTrainingSize` | INT | 10 | Minimum rows before emitting a prediction |
| `p` | INT | auto | ARIMA AR order — omit for auto-selection |
| `d` | INT | auto | ARIMA differencing order — omit for auto-selection |
| `q` | INT | auto | ARIMA MA order — omit for auto-selection |

**Always omit `p`, `d`, `q` for heterogeneous data.** Manual orders cause
`"Model failed to process data"` on near-constant or low-variance series.
Auto mode selects the simplest convergent model per partition independently.

---

## Return Type — Critical

`ML_FORECAST()` returns **`ARRAY<ROW(...)>`**, not a scalar `DOUBLE`.

```
ARRAY<ROW(
  TIMESTAMP(6)  TIMESTAMP,       -- forecast horizon timestamp
  DOUBLE        FORECAST_VALUE,  -- predicted value  ← position 2
  DOUBLE        LOWER_BOUND,     -- confidence interval lower bound
  DOUBLE        UPPER_BOUND,     -- confidence interval upper bound
  DOUBLE        RMSE,            -- root mean square error of model fit
  DOUBLE        AIC              -- Akaike information criterion
)>
```

Attempting arithmetic directly on the return value causes:
```
Cannot apply '-' to ARRAY<ROW(...)> and DOUBLE
```

The array must be unpacked using `CROSS JOIN UNNEST` before any arithmetic.

---

## Three Array States to Handle

ML_FORECAST can return three distinct states depending on the data series:

| State | Condition | Meaning | `CARDINALITY()` |
|---|---|---|---|
| Non-null, non-empty | ARIMA converged | Valid prediction available | `> 0` |
| `NULL` | Fewer than `minTrainingSize` rows seen | Not enough history yet | N/A |
| Non-null, **empty `[]`** | Near-constant / zero-variance series | ARIMA could not fit | `= 0` |

**The empty array case is the most common gotcha.** `CROSS JOIN UNNEST` of an
empty array produces **zero output rows** — the row silently disappears.
`IS NOT NULL` does not catch it. You must check `CARDINALITY(array) > 0`.

---

## Canonical Two-Layer Unpacking Pattern

### Layer 1 — Run ML_FORECAST, carry array forward

```sql
CREATE VIEW forecast_raw AS
SELECT
  group_id,
  event_date,
  metric_value,
  time_column,
  ML_FORECAST(
    metric_value,
    time_column,
    JSON_OBJECT('minTrainingSize' VALUE 5)
  ) OVER (
    PARTITION BY group_id
    ORDER BY time_column
    RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS forecast_array
FROM source_view;
```

### Layer 2 — Unpack array, handle all three states

```sql
CREATE VIEW forecast_unpacked AS
-- Branch A: ARIMA converged → extract FORECAST_VALUE from position 2
SELECT
  group_id,
  event_date,
  metric_value,
  fc_val AS predicted_value
FROM forecast_raw
CROSS JOIN UNNEST(forecast_array) AS t (fc_ts, fc_val, fc_lo, fc_hi, fc_rmse, fc_aic)
WHERE forecast_array IS NOT NULL AND CARDINALITY(forecast_array) > 0

UNION ALL

-- Branch B: NULL or empty array → pass through with NULL predicted_value
-- COALESCE in the downstream INSERT uses metric_value as fallback
SELECT
  group_id,
  event_date,
  metric_value,
  CAST(NULL AS DOUBLE) AS predicted_value
FROM forecast_raw
WHERE forecast_array IS NULL OR CARDINALITY(forecast_array) = 0;
```

The `UNION ALL` ensures every input row produces exactly one output row
regardless of ARIMA convergence state.

---

## Downstream INSERT Pattern

Use `COALESCE(predicted_value, metric_value)` everywhere the forecast is
referenced so that rows with a NULL prediction (ARIMA did not converge) fall
back to the observed value and still reach the sink:

```sql
INSERT INTO forecast_sink
SELECT
  group_id,
  event_date,
  metric_value                                        AS current_value,
  COALESCE(predicted_value, metric_value)             AS predicted_value,
  (COALESCE(predicted_value, metric_value)
    - metric_value)                                   AS rate_of_change,
  CASE
    WHEN COALESCE(predicted_value, metric_value) >= threshold_high THEN 'CRITICAL'
    WHEN COALESCE(predicted_value, metric_value) >= threshold_mid  THEN 'RISK'
    ELSE 'NORMAL'
  END                                                 AS severity
FROM forecast_unpacked;
```

---

## Feeding ML_FORECAST: Event-Time Windows

ML_FORECAST needs a **regular time series** — one row per group per time
period. Use a `TUMBLE` window to produce it from raw streaming events:

```sql
CREATE VIEW daily_aggregates AS
SELECT
  group_id,
  window_start,
  window_end,
  CAST(CAST(window_start AS DATE) AS STRING) AS event_date,
  UNIX_TIMESTAMP(CAST(window_end AS STRING)) * 1000 AS end_ts,
  MAX(metric) - MIN(metric) AS metric_value       -- or AVG, SUM, etc.
FROM TABLE(
  TUMBLE(
    TABLE source_topic,
    DESCRIPTOR(event_time),
    INTERVAL '1' DAY
  )
)
GROUP BY group_id, window_start, window_end;
```

**Watermark sizing matters.** Set `WATERMARK FOR event_time AS event_time -
INTERVAL '30' MINUTE` (not hours or days) so windows close promptly when
events arrive. A watermark that is too wide delays window closure and
prevents ML_FORECAST from receiving data.

### Advancing the watermark for historical seed data

When you publish historical records (e.g. 10 days of past data at pipeline
startup), the watermark only advances as far as the last event's timestamp
minus the lag. To close all historical windows at once, publish one
**heartbeat record** per partition timestamped 3+ days in the future:

```python
future_ts = int((datetime.now(UTC) + timedelta(days=3)).timestamp() * 1000)
heartbeat = {"group_id": group_id, "timestamp": future_ts, "metric": neutral_value}
```

Use a `neutral_value` that produces `metric_value = 0` for that future
window (e.g. `MAX - MIN = 0` by setting all heartbeat values to the same
number). The future window itself won't close for 3 days and won't pollute
the training series.

---

## JOIN Pattern for Reference Data

**Do not JOIN ML_FORECAST output against a compacted Kafka reference topic
using a regular streaming inner JOIN.** The reference topic emits once at
seed time and then goes silent. In streaming mode:

1. Reference records enter Flink's join state on startup
2. High-activity partition rows arrive and match (state still warm)
3. Low-activity partition rows arrive slightly later — state evicted → **silent drop**

This is the most common cause of "some rows appear, others don't" in
ML_FORECAST pipelines. The symptom is that high-variance series (whose
ARIMA converges fast) appear in the sink while low-variance series
(whose ARIMA takes longer) do not.

**Fix: use an inline `VALUES` table for small reference datasets:**

```sql
INSERT INTO sink
SELECT f.group_id, ..., b.threshold
FROM forecast_unpacked AS f
JOIN (
  VALUES ('ID-001', 1.5), ('ID-002', 0.9), ('ID-003', 2.0)
) AS b (group_id, threshold)
ON f.group_id = b.group_id;
```

The `VALUES` table is a static in-memory constant — no Kafka read, no join
state timing, guaranteed match for every row.

For `FOR SYSTEM_TIME AS OF PROCTIME()` (temporal lookup join): this syntax
is **not supported** in the current Confluent Flink SQL parser version
(`"Encountered FOR"` parse error). Use the `VALUES` workaround instead.

---

## Sink Table Column Order

When writing to a Kafka sink with `PRIMARY KEY ... NOT ENFORCED`, the SELECT
column order must exactly match the `CREATE TABLE` column order. A mismatch
causes:

```
Column types of query result and sink do not match.
Incompatible types for sink column 'X' at position N.
```

Always declare the `CREATE TABLE` column order first, then write the `INSERT
SELECT` columns in the same order.

---

## Interpreting ML_FORECAST Output Fields

| Field | Use |
|---|---|
| `FORECAST_VALUE` | The predicted next-step value — primary output |
| `LOWER_BOUND` / `UPPER_BOUND` | 95% confidence interval for the prediction — use for chart bands |
| `RMSE` | Model fit quality — higher means the series is harder to predict |
| `AIC` | Model selection score — lower is better; compare across ARIMA orders |

The confidence interval **widens** as the model uncertainty increases. Surfacing
`LOWER_BOUND`/`UPPER_BOUND` in the sink gives the UI statistically meaningful
confidence bands rather than hardcoded percentage offsets.

---

## One-Step-Ahead vs Multi-Step Forecasting

`ML_FORECAST()` is fixed at **one-step-ahead**. It cannot be configured to
output multiple future predictions in a single call.

### Options for multi-step prediction

| Approach | How | Trade-off |
|---|---|---|
| **Iterative nightly runs** | Re-publish one new day of real data each night; ML_FORECAST emits one new prediction per night | 7 nightly runs → 7 grounded predictions; requires scheduled pipeline |
| **Linear extrapolation** | Take `rate = predicted − observed` from Flink; project `current + rate × d` for d = 1..N in the application layer | Simple but ignores non-linear trends |
| **Widening confidence bands** | Use `RMSE` from ML_FORECAST to widen the application-layer projection bands proportionally to `d` | More accurate uncertainty representation without re-running ARIMA |

For production pipelines, the iterative nightly run approach is preferred —
each prediction is grounded in one more real data point rather than
extrapolated from a single slope.

---

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `Cannot apply '-' to ARRAY<ROW(...)> and DOUBLE` | Arithmetic on raw ML_FORECAST return value | Unpack with `CROSS JOIN UNNEST` first |
| `Model failed to process data` | Manual `p/d/q` on low-variance series | Remove `p`, `d`, `q` from JSON options — use auto mode |
| Rows silently missing from sink | Empty array `[]` from near-constant series | Add `CARDINALITY(forecast_array) > 0` guard; use `UNION ALL` fallback |
| `Encountered "FOR"` parse error | `FOR SYSTEM_TIME AS OF PROCTIME()` not supported | Use inline `VALUES` table for reference data |
| `Column types do not match` on INSERT | SELECT column order differs from sink CREATE TABLE order | Match SELECT column order exactly to CREATE TABLE definition |
| Only high-variance partitions in sink | Streaming JOIN state eviction for slow-converging ARIMA | Replace Kafka JOIN with inline `VALUES` table |
| All windows show `metric_value = 0` | Watermark not advancing past historical window boundaries | Publish a future-timestamped heartbeat record to flush all windows |

---

## Minimal Working Example

```sql
-- 1. Source table with watermark
CREATE TABLE raw_events (
  entity_id   STRING,
  `timestamp` BIGINT,
  value       DOUBLE,
  event_time  AS TO_TIMESTAMP_LTZ(`timestamp`, 3),
  WATERMARK FOR event_time AS event_time - INTERVAL '30' MINUTE
) DISTRIBUTED BY (entity_id) INTO 1 BUCKETS
WITH ('key.format' = 'json-registry', 'value.format' = 'json-registry', 'value.fields-include' = 'ALL');

-- 2. Daily aggregation (regular time series for ARIMA)
CREATE VIEW daily_series AS
SELECT
  entity_id,
  window_end,
  CAST(CAST(window_start AS DATE) AS STRING) AS series_date,
  AVG(value) AS avg_value
FROM TABLE(TUMBLE(TABLE raw_events, DESCRIPTOR(event_time), INTERVAL '1' DAY))
GROUP BY entity_id, window_start, window_end;

-- 3. ML_FORECAST — raw array output
CREATE VIEW forecast_raw AS
SELECT
  entity_id, series_date, avg_value, window_end,
  ML_FORECAST(avg_value, window_end, JSON_OBJECT('minTrainingSize' VALUE 5))
  OVER (PARTITION BY entity_id ORDER BY window_end
        RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS forecast_array
FROM daily_series;

-- 4. Unpack — handle converged, NULL, and empty array cases
CREATE VIEW forecast_unpacked AS
SELECT entity_id, series_date, avg_value, fc_val AS predicted_value
FROM forecast_raw
CROSS JOIN UNNEST(forecast_array) AS t (fc_ts, fc_val, fc_lo, fc_hi, fc_rmse, fc_aic)
WHERE forecast_array IS NOT NULL AND CARDINALITY(forecast_array) > 0
UNION ALL
SELECT entity_id, series_date, avg_value, CAST(NULL AS DOUBLE) AS predicted_value
FROM forecast_raw
WHERE forecast_array IS NULL OR CARDINALITY(forecast_array) = 0;

-- 5. Sink table — column order is authoritative
CREATE TABLE forecast_output (
  entity_id       STRING,
  series_date     STRING,
  current_value   DOUBLE,
  predicted_value DOUBLE,
  rate_of_change  DOUBLE,
  severity        STRING,
  PRIMARY KEY (entity_id, series_date) NOT ENFORCED
) WITH ('key.format' = 'json-registry', 'value.format' = 'json-registry', 'value.fields-include' = 'ALL');

-- 6. INSERT — column order matches CREATE TABLE; COALESCE handles NULL predictions
INSERT INTO forecast_output
SELECT
  f.entity_id,
  f.series_date,
  f.avg_value                                      AS current_value,
  COALESCE(f.predicted_value, f.avg_value)         AS predicted_value,
  (COALESCE(f.predicted_value, f.avg_value) - f.avg_value) AS rate_of_change,
  CASE
    WHEN COALESCE(f.predicted_value, f.avg_value) >= b.threshold * 3.0 THEN 'CRITICAL'
    WHEN COALESCE(f.predicted_value, f.avg_value) >= b.threshold * 1.8 THEN 'RISK'
    ELSE 'NORMAL'
  END AS severity
FROM forecast_unpacked AS f
JOIN (VALUES ('ID-001', 1.0), ('ID-002', 2.0)) AS b (entity_id, threshold)
ON f.entity_id = b.entity_id;
```
