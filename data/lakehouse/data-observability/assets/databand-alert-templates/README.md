# Databand Alert Policy Templates

Pre-built **IBM Databand** alert policy templates covering the most common  
data quality failure modes, applied via the Databand REST API v1.

## IBM Cloud Products Used

| Product | Role |
|---|---|
| **IBM Databand** | Alert policy definitions and evaluation |
| **IBM Cloud IAM** | Authentication for API calls |

## Included Templates (`alert_policies.yaml`)

| Template Key | Metric | Operator | Threshold | Severity |
|---|---|---|---|---|
| `null_rate_policy` | `null_rate` | `> 5%` | 0.05 | High |
| `row_count_drop_policy` | `row_count` | `< 80% of prior run` | 0.80 | Critical |
| `schema_drift_policy` | `schema_drift` | `== true` | true | High |
| `sla_breach_policy` | `duration_seconds` | `> 7200 s` | 7200 | Medium |
| `quality_score_policy` | `quality_score` | `< 0.85` | 0.85 | High |
| `duplicate_rate_policy` | `duplicate_rate` | `> 2%` | 0.02 | Medium |

## Quick Start

```bash
pip install requests pyyaml python-dotenv click tenacity
cp ../../databand-pipeline-monitor/.env.example .env
# Edit .env with DATABAND_URL and DATABAND_ACCESS_TOKEN

# Apply null-rate alert for pipeline "customer_pipeline"
python apply_alert_templates.py --template null_rate_policy --pipeline customer_pipeline

# Apply all templates
python apply_alert_templates.py --all --pipeline customer_pipeline

# Dry-run: print rendered payloads without calling Databand
python apply_alert_templates.py --all --pipeline customer_pipeline --dry-run
```

## IBM Cloud References

- [IBM Databand Alert Policies](https://www.ibm.com/docs/en/databand?topic=monitoring-alert-policies)
- [IBM Databand API Reference](https://databand.ai/docs/api)
