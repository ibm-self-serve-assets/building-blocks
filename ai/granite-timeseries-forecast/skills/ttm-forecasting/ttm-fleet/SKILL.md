---
name: ttm-fleet
description: TTM concurrent fleet forecasting — runs per-truck TTM predictions in parallel using ThreadPoolExecutor, handles timeouts and fallbacks, normalises cargo temperatures before building context windows, and logs governance payloads to IBM OpenScale in a fire-and-forget thread.
---

# TTM Fleet — Concurrent Forecasting & Governance

## Overview

The fleet endpoint runs one TTM forecast per truck in parallel. All workers are independent — a timeout on one truck does not fail the others.

<Steps>
<Step>
Configure `FLEET_WORKERS` and `PER_TRUCK_TIMEOUT` for your fleet size (see **Fleet Configuration** below).
</Step>

<Step>
Apply cargo temperature normalisation before building each truck's context window (see **Cargo Temperature Normalisation**).
</Step>

<Step>
Run all truck forecasts concurrently using `ThreadPoolExecutor` (see **Concurrent Forecasting Pattern**).
</Step>

<Step>
If governance logging is required, activate it via `provision.py` and pass cargo context before calling `forecast()` (see **OpenScale Governance Logging**).
</Step>
</Steps>

---

## Fleet Configuration

```python
PER_TRUCK_TIMEOUT = 8        # seconds — one TTM native API round-trip
FLEET_WORKERS     = min(10, len(trucks))
```

Adjust `PER_TRUCK_TIMEOUT` if native API latency increases (e.g. cross-region calls). Increase `FLEET_WORKERS` only when fleet size exceeds 10 trucks.

---

## Concurrent Forecasting Pattern

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def forecast_fleet_optimization(trucks: list) -> list:
    FLEET_WORKERS     = min(10, len(trucks))
    PER_TRUCK_TIMEOUT = 8

    with ThreadPoolExecutor(max_workers=FLEET_WORKERS) as pool:
        future_map = {
            pool.submit(_forecast_one, t['truckId']): t['truckId']
            for t in trucks
        }

    results = []
    for future, truck_id in future_map.items():
        try:
            results.append(future.result(timeout=PER_TRUCK_TIMEOUT))
        except TimeoutError:
            # Timed-out truck falls back to current-temp-vs-threshold heuristic
            results.append(_fallback_heuristic(truck_id))
        except Exception as e:
            results.append({"truckId": truck_id, "error": str(e)})

    return results
```

Each worker calls `_forecast_one(truck_id)` which:
1. Fetches the truck's telemetry
2. Applies cargo normalisation
3. Calls `ttm_model.forecast()` via Path 1 (native API) or Path 2 (local)
4. Returns a structured result dict

---

## Cargo Temperature Normalisation

The simulation can push truck temperatures to extremes (e.g. +29 °C for a frozen-cargo truck). Clamp to a realistic operating range **before** building the TTM context window:

```python
_CARGO_BASE = {
    'frozen_foods':                        -21.0,
    'temperature_sensitive_vaccines':      -15.0,
    'fresh_produce':                         6.0,
    'dairy_products':                        5.0,
    'pharmaceuticals':                       5.0,
}

def normalise_cargo_temp(telemetry_temp: float, cargo_type: str, critical_threshold: float) -> float:
    cargo_base = _CARGO_BASE.get(cargo_type, telemetry_temp)

    if abs(telemetry_temp - cargo_base) > 10:
        # Incident detected — set slight breach margin for context window
        return critical_threshold + 2.0
    return telemetry_temp
```

This prevents garbage context windows from reaching the TTM model and keeps OpenScale drift monitoring meaningful.

---

## Risk Assessment Algorithm

```python
risk_score = int(
    0.5 * temperature_risk +   # forecast-based (TTM prediction vs threshold)
    0.3 * weather_risk +       # external weather data
    0.2 * value_risk           # cargo $ value normalised to 0-100
)
```

| Score | Level | Action |
|---|---|---|
| > 70 | CRITICAL | Immediate intervention — reroute to nearest station |
| 40–70 | WARNING | Monitor closely — prepare contingency plan |
| < 40 | NORMAL | Continue normal operations |

---

## OpenScale Governance Logging

When `GOVERNANCE_PAYLOAD_LOGGING=true` and `governance/artifacts/deployment.json` contains valid OpenScale IDs, every native API call logs a payload record in a **fire-and-forget daemon thread** — forecast latency is never affected.

### What gets logged

| Field | Source |
|---|---|
| `temp_mean`, `temp_std`, `temp_min`, `temp_max` | Summary stats of the 512-point context window |
| `critical_threshold` | Passed from `forecasting_service.py` via `kwargs` |
| `cargo_type` | Passed from `forecasting_service.py` via `kwargs` |
| `predicted_temp_mean` | `mean(96-step forecast)` |

### Activating governance

```bash
cd governance/setup
python provision.py    # writes subscription_id and payload_data_set_id to deployment.json
```

Until `provision.py` has run, logging is silently skipped — it never blocks the service.

### Passing cargo context to the logger

```python
# In forecasting_service.py — set before calling forecast()
self.ttm_model._last_cargo_type         = cargo_type
self.ttm_model._last_critical_threshold = critical_threshold
predicted_temps = self.ttm_model.forecast(ttm_input)
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Fleet endpoint is slow (>15 s) | Confirm `ThreadPoolExecutor` is used with `FLEET_WORKERS = min(10, len(trucks))`. If a worker is blocking, increase `PER_TRUCK_TIMEOUT` (default 8 s). |
| One truck timeout crashes all results | Each future is resolved independently — check that `future.result(timeout=...)` is called per-future inside the loop, not on the pool as a whole. |
| OpenScale payload logging silently skipped | `governance/artifacts/deployment.json` missing or has no `payload_data_set_id`. Run `python governance/setup/provision.py`. |
| Cargo temperatures unrealistically high/low | Apply `normalise_cargo_temp()` before building the context window — never pass raw telemetry directly to TTM when simulation is active. |
