# Lineage Impact Analyzer

**IBM Products**: IBM watsonx.data Intelligence (Manta), IBM Cloud IAM, IBM Cloud Object Storage
**Language**: Python 3.12
**Type**: CLI tool

## Overview

CLI tool for **downstream impact analysis** using the **IBM watsonx.data Intelligence** Manta lineage REST API. Given a source data asset, it traverses the full downstream dependency graph, renders a human-readable impact tree in the terminal, and optionally archives a structured JSON impact report to **IBM Cloud Object Storage** for audit and compliance.

## Prerequisites

- IBM Cloud API key
- IBM watsonx.data Intelligence instance and project ID
- (Optional) IBM Cloud Object Storage bucket for report archiving

## Quick Start

```bash
pip install -r requirements.txt

# Set credentials as environment variables
export IBM_API_KEY=your_api_key
export WXDI_BASE_URL=https://<region>.dataplatform.cloud.ibm.com
export WXDI_PROJECT_ID=your_project_id

# Show downstream impact tree in terminal
python impact_analyzer.py --asset-id your-asset-id

# Save JSON report to file
python impact_analyzer.py --asset-id your-asset-id --output impact_report.json

# Archive report to IBM COS
export COS_API_KEY=your_cos_key
export COS_INSTANCE_CRN=your_cos_crn
export COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
export COS_BUCKET=lineage-reports
python impact_analyzer.py --asset-id your-asset-id --archive-cos
```

## Command Line Options

| Option | Description | Required |
|---|---|---|
| `--asset-id` | Source asset ID to analyze | Yes |
| `--output` | Save impact report to JSON file | No |
| `--archive-cos` | Archive report to IBM COS | No |
| `--max-depth` | Maximum traversal depth (default: 10) | No |
| `--format` | Output format: `tree` or `json` (default: `tree`) | No |

## Example Output

```
Impact Analysis for asset: customer_master_table
Analyzed at: 2024-06-15T10:30:00Z

customer_master_table
├── customer_etl_job (Job)
│   ├── customer_curated_table (Dataset)
│   │   ├── revenue_report_view (Dataset)
│   │   │   └── quarterly_dashboard (Application)
│   │   └── customer_segmentation_model (ML Model)
│   └── customer_audit_log (Dataset)
└── customer_sync_job (Job)
    └── crm_customer_export (Dataset)

Total downstream assets: 7
Direct dependents: 2
Max depth reached: 4
```

## JSON Report Format

```json
{
  "asset_id": "customer_master_table",
  "analyzed_at": "2024-06-15T10:30:00Z",
  "total_downstream_count": 7,
  "max_depth": 4,
  "impact_tree": {
    "id": "customer_master_table",
    "type": "Dataset",
    "children": [...]
  }
}
```

## IBM Cloud References

- [IBM watsonx.data Intelligence on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/watsonx-data-intelligence)
- [watsonx.data Intelligence API Reference](https://cloud.ibm.com/apidocs/watsonx-data-intelligence)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
