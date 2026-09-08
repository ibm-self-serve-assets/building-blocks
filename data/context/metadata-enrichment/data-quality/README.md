# Data Quality

**IBM product**: IBM watsonx.data intelligence

Reference assets for defining, executing, and reviewing data-quality rules and quality scores.

## When to use

Use this building block when developers need to:

- define reusable validation rules for governed data assets;
- expose quality-rule operations through an API;
- evaluate records against completeness, validity, uniqueness, range, or pattern checks;
- surface quality scores and exceptions to downstream applications;
- complement metadata enrichment with executable quality controls.

## Flow

```text
Data asset / connection
        |
        v
 Quality rules / profiling
        |
        v
IBM watsonx.data intelligence
        |
        +--> rule results
        +--> quality score
        +--> exception details
```

## Included assets

| Path | Purpose |
|---|---|
| [`assets/quality-rules-engine/`](assets/quality-rules-engine/) | Reference FastAPI service for quality-rule workflows |
| [`bob-modes/`](bob-modes/) | IBM Bob data-quality mode |
| [`bob-skills/data-quality-rules.zip`](bob-skills/data-quality-rules.zip) | IBM Bob data-quality skill |

## Quick start

```bash
cd assets/quality-rules-engine
cp .env.example .env
# Set IBM_API_KEY and the project/service values required by the asset.
pip install -r requirements.txt
python main.py
# Swagger UI: http://localhost:8080/docs
```

Example developer flow:

```text
POST /rules                 -> create/define a rule
POST /rules/{id}/execute    -> execute a rule
GET  /rules/score           -> retrieve aggregate quality score
```

See the asset README for supported rule types, payload examples, Docker usage, and configuration.

## Production notes

- Keep rule definitions close to the business semantics of the governed asset.
- Do not treat a single aggregate score as sufficient evidence of fitness for every workload.
- Review exception handling and output retention before applying to sensitive data.
- Verify supported sources and quality features in the target watsonx.data intelligence version.

## IBM references

- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- Metadata enrichment/data-quality settings: https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=tools-metadata-enrichment
