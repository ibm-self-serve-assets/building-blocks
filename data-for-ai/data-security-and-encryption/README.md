# Data Privacy and Encryption with watsonx.data Intelligence

This building block combines two critical areas of data security and encryption:

1. **Project & Catalog Automation**  
   Using Python and IBM Cloud APIs to create projects and catalogs.
   
2. **Data Protection / Masking Workflow**  
   Using REST APIs (cURL templates) to create **categories**, **business terms**, **data protection rules** (redacting email), and **policies** that enforce masking.

3. **Guardium Integration (Coming Soon)**
  Building block to cover advanced data security, monitoring, and encryption enforcement with IBM Guardium.
---

## Overview

This document helps **DevOps engineers, data engineers, and data stewards** to:

- Automate the creation of **IBM Cloud projects and catalogs**.
- Define **data governance artifacts** (Category, Business Term, Rule, Policy).
- Enforce **data masking** for sensitive fields (e.g., email, SSN).
- Validate masking for restricted roles like **Business Users**.

---

## Prerequisites

- IBM Cloud account with access to **watsonx.data Intelligence**.
- IBM Cloud Object Storage instance and credentials.
- IBM **API Key** with sufficient permissions.
- Installed: `curl`, `jq`, Python 3.x, `requests` library.
- Correct service endpoints for your IBM Cloud region.

---

# 1 IBM Project & Catalog Automation

We use a Python script (`setup_ibm_projects_catalog.py`) with `input.json` to automate project and catalog creation.

---

### Input JSON structure (`input.json`)

| Key             | Description                          | Example |
|-----------------|--------------------------------------|---------|
| `ibm_api_key`   | IBM Cloud API key                   | `XXXXXXXXXXXX` |
| `region`        | Target IBM region                   | `eu-de` |

#### Project Config (`project`)

| Key              | Description                        | Example |
|------------------|------------------------------------|---------|
| `name`           | Project name                       | `Demo-Project-for-watsonx.data-Intelligence` |
| `description`    | Project description                | `Demo project` |
| `type`           | Project type                       | `wx` |
| `generator`      | Project generator identifier       | `Projects-for-Intelligence` |
| `public`         | Public project flag                | `false` |

##### Storage

| Key            | Description | Example |
|----------------|-------------|---------|
| `type`         | Storage type | `bmcos_object_storage` |
| `resource_crn` | COS resource CRN | `XXXXXXXXXXXXXXXX` |
| `guid`         | COS instance GUID | `XXXXXXXXXXXXXXXX` |
| `delegated`    | Delegation flag | `false` |

#### Catalog Config (`catalog`)

| Key              | Description        | Example |
|------------------|--------------------|---------|
| `name`           | Catalog name       | `Demo-Catalog-for-watsonx.data-Intelligence` |
| `bss_account_id` | Account ID         | `XXXXXXXXXXXXXXXX` |
| `is_governed`    | Governance enabled | `true` |

##### COS Bucket

| Key                | Description            | Example |
|--------------------|------------------------|---------|
| `bucket_name`      | COS bucket name        | `bucket-xyz` |
| `bucket_location`  | COS bucket location    | `eu-de` |
| `endpoint_url`     | COS endpoint           | `s3.eu-de.cloud-object-storage.appdomain.cloud` |
| `resource_instance_id` | Resource instance | `XXXXXXXXXXXXXXXX` |

##### COS Credentials

Each role (**viewer, editor, admin**) requires:

- `api_key`
- `access_key_id`
- `secret_access_key`
- `service_id`

---

### Run the Automation Script

```bash
python setup_ibm_projects_catalog.py
```

This will:
- Authenticate with IBM Cloud IAM
- Create a project
- Create a catalog
- Print responses for verification

---

# 2 Data Protection & Masking Workflow

Now that projects and catalogs are provisioned, we add **governance rules** to redact sensitive data.

---

## Step 1: Get IAM Token

```bash
export API_KEY="YOUR_IBM_API_KEY"
export TOKEN=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=${API_KEY}" | jq -r .access_token)

echo $TOKEN | head -c 40 && echo "... (truncated)"
```

---

## Step 2: Create Category

```bash
curl -X POST "${WATSONDATA_API_BASE}/v2/categories" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PII",
    "description": "Personally Identifiable Information",
    "short_description": "PII data"
  }'
```

---

## Step 3: Create Business Term

```bash
curl -X POST "${WATSONDATA_API_BASE}/v2/terms" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Email Address",
    "short_description": "User email address",
    "description": "Business term for email",
    "categories": ["<CATEGORY_ID>"]
  }'
```

---

## Step 4: Create Data Protection Rule (Redact Email)

```bash
curl -X POST "${CATALOG_API_BASE}/v3/enforcement/rules" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Redact Email Rule",
    "description": "Mask email columns for Business Users",
    "assetTypes": ["table","view"],
    "masking": {
      "method": "redact",
      "preserveFormat": false
    },
    "criteria": [
      {
        "columnProperty": "columnName",
        "values": ["email"]
      }
    ],
    "targetUsers": {
      "roles": ["Business User"]
    }
  }'
```

---

## Step 5: Create Policy (link Rule + Term)

```bash
curl -X POST "${WATSONDATA_API_BASE}/v2/policies" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PII Redaction Policy",
    "description": "Policy to enforce email redaction",
    "assetTypes": ["table","view"],
    "rules": ["<RULE_ID>"],
    "terms": ["<TERM_ID>"]
  }'
```

---

## Step 6: Validate as Business User

```bash
curl -X GET "${CATALOG_API_BASE}/v2/assets/<ASSET_ID>/data" \
  -H "Authorization: Bearer ${BUSINESS_USER_TOKEN}" \
  -H "Accept: application/json"
```

Expected: Email column is masked (e.g., `***` or `xxxxx`).

---
# 3. Guardium Integration (Coming Soon)

In the next iteration of this building block, we will extend watsonx.data security and encryption by adding IBM Guardium capabilities, including:

Data Activity Monitoring – Track sensitive data access in real-time.

Encryption & Key Management – Enforce encryption policies consistently.

Compliance Reporting – Automate reporting for GDPR, CCPA, HIPAA, and other regulations.

Integration with watsonx.data – Unified data protection and governance.

📘 Learn more: [IBM Guardium Documentation](https://www.ibm.com/docs/en/gdp/12.x)

# Troubleshooting & Notes

- Ensure you replace placeholders (`<TOKEN>`, `<CATEGORY_ID>`, `<RULE_ID>`, etc.) with actual values.
- Use **Data Steward** or Admin privileges for setup.
- API payload formats may vary by region/tenant version.
- Always verify with the official API documentation:  
  https://cloud.ibm.com/apidocs/watson-data-api#introduction  
  https://cloud.ibm.com/apidocs/knowledge-catalog#introduction  

---

# Summary

With this guide, you can:

1. Automate IBM Project & Catalog creation.
2. Enforce governance with masking rules.
3. Protect sensitive data like **emails** with **policies and terms**.
4. Validate masking behavior by simulating different roles.
5. (Soon) Extend to Guardium for end-to-end data security, monitoring, and encryption enforcement.

This ensures data privacy and encryption at scale using watsonx.data Intelligence today, with Guardium integration coming soon.

This ensures **data privacy and encryption at scale** using watsonx.data Intelligence.

---
