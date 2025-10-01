# Data Privacy and Encryption with watsonx.data Intelligence

This combined README covers two things in one place:

1. **Project & Catalog automation** (Python script approach, token steps) — useful for provisioning projects and catalog.
2. **Data protection / masking workflow** — step-by-step cURL templates to create a *category*, *business term*, *data protection (masking) rule* that **redacts email**, and a *policy* that ties the rule + business term together. 

> **NOTE:** Replace all placeholder values (`$TOKEN`, `$API_KEY`, `<REGION>`, `<CATALOG_API_BASE>`, `<WATSONDATA_API_BASE>`, `<ROLE_ID>`, etc.) with your real values for your tenant/region. Consult your instance endpoints in IBM Cloud for exact base URLs.


---

# Overview

This document helps DevOps / data engineers and data stewards automate:

- provisioning projects & catalogs,
- and creating governance artifacts required for masking sensitive fields (like email and SSN):

  1. Create a Category (e.g., `PII`)  
  2. Create a Business Term (e.g., `Email Address`) and link to Category  
  3. Create a Data Protection Rule that **redacts** `email` columns  
  4. Create/attach a Policy that references the rule and business term  
  5. Validate masked output as a user with the restricted role (Business User)

This approach enforces masking at the catalog / governance layer so consumers (UI, APIs) receive masked results according to the policy.

---

# Prerequisites

- IBM Cloud account with access to your watsonx data intelligence.
- IBM Cloud Object Store.
- An IBM **API key** with privileges to create catalog artifacts (or credentials of a user with Manager / Data Steward privileges).
- `curl`, `jq` and a terminal (or Postman) available.
- Knowledge of the correct service endpoints for your region / instance — you will need:
  - Catalog API base (e.g. `https://<catalog-instance>.dataplatform.cloud.ibm.com` or region-specific `https://api.eu-de.dataplatform.cloud.ibm.com`)
  - Watson Data API base for terms / policies (often same dataplatform host)
- The commands below assume `jq` for extracting IDs.

---

# Get an IAM token (one-liner)

Use your IBM Cloud API key to generate an IAM token — store it in `$TOKEN`:

```bash
export API_KEY="YOUR_IBM_API_KEY"

export TOKEN=$(curl -s -X POST "https://iam.cloud.ibm.com/identity/token"   -H "Content-Type: application/x-www-form-urlencoded"   -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=${API_KEY}"   | jq -r .access_token)

# verify
echo "$TOKEN" | head -c 40 && echo "... (truncated)"
```

If you prefer Python, the sample project script you have already does the same and saves token to `os.environ["TOKEN"]`.

---

# Base URL / endpoint guidance

Replace the placeholders below with your actual service endpoints:

- `CATALOG_API_BASE` — Knowledge Catalog enforcement/create-rule endpoint owner, e.g.:
  - `https://<catalog-instance>.dataplatform.cloud.ibm.com`  
  - or `https://api.<region>.dataplatform.cloud.ibm.com` (if that matches your tenant)
- `WATSONDATA_API_BASE` — Watson Data API base used for `categories`, `terms`, `policies` endpoints (commonly same domain as your dataplatform instance)

Set these environment variables before running the cURL commands:

```bash
export CATALOG_API_BASE="https://api.eu-de.dataplatform.cloud.ibm.com"   # example
export WATSONDATA_API_BASE="$CATALOG_API_BASE" 
```

> If you're unsure which base to use, visit the **Service instance** in IBM Cloud → Service details → API endpoints or check the IBM docs for the region endpoints.

---

# Data protection / masking workflow (high-level)

1. **Create a Category** (e.g., `PII`) — categories help classify terms and assets.  
2. **Create a Business Term** (e.g., `Email Address`) and tag it with the category.  
3. **Create a Data Protection Rule** (Knowledge Catalog rule) that targets columns named `email` and sets `masking.method = "redact"`.  
4. **Create a Policy** (Watson Data policy) that references the rule and the business term (so the policy is aware of what to protect).  
5. **Publish/Apply** the rule/policy to the catalog/project and validate.  
6. **Test** with a token for a Business User (role) to ensure data is masked when queried.

---

# API examples (templates) — **Fill placeholders** and run

> All commands require `$TOKEN` set and appropriate API base variables.

---

## 1) Create a Category (Watson Data API)

```bash
curl -X POST "${WATSONDATA_API_BASE}/v2/categories"   -H "Authorization: Bearer ${TOKEN}"   -H "Content-Type: application/json"   -H "Accept: application/json"   -d '{
    "name": "PII",
    "description": "Personally Identifiable Information",
    "short_description": "PII data",
    "parent_id": null
  }'
```

**Response:** `{ "id": "<category_id>", ... }` — save `category_id` for the next step.

---

## 2) Create a Business Term and link to Category

```bash
curl -X POST "${WATSONDATA_API_BASE}/v2/terms"   -H "Authorization: Bearer ${TOKEN}"   -H "Content-Type: application/json"   -H "Accept: application/json"   -d '{
    "name": "Email Address",
    "short_description": "User email address",
    "description": "Business term for user's email address",
    "categories": ["PII"]           # or use category id array if required
  }'
```

**Response:** contains `"id": "<term_id>"` — save `term_id`.

> Note: If API expects category IDs instead of names, pass `["<category_id>"]` — check your /categories response.

---

## 3) Create a Data Protection Rule that redacts `email` columns (Knowledge Catalog)

**Knowledge Catalog** exposes enforcement rules endpoints; below is a typical template. Replace `CATALOG_API_BASE` accordingly.

```bash
curl -X POST "${CATALOG_API_BASE}/v3/enforcement/rules"   -H "Authorization: Bearer ${TOKEN}"   -H "Content-Type: application/json"   -d '{
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
      "roles": ["Business User"]   # can be role name or role ID depending on your catalog
    }
  }'
```

**Response:** JSON with rule details and `id` (or `rule_id`) — save `rule_id`.

> **Important:** The exact field names (e.g., `columnProperty`, `criteria` structure, `targetUsers`) depend on the Knowledge Catalog API version. If the call fails, consult the `CreateRule` reference in your instance docs (https://cloud.ibm.com/apidocs/knowledge-catalog#createrule) and adapt payload fields accordingly.

---

## 4) Create a Policy and associate the rule + business term (Watson Data API)

Use the policy creation endpoint and include the `rule_id` and `term_id` in the policy payload.

```bash
curl -X POST "${WATSONDATA_API_BASE}/v2/policies"   -H "Authorization: Bearer ${TOKEN}"   -H "Content-Type: application/json"   -H "Accept: application/json"   -d '{
    "name": "PII Redaction Policy",
    "description": "Policy to enforce email redaction",
    "assetTypes": ["table","view"],
    "rules": [
      { "rule_id": "<RULE_ID>" }
    ],
    "terms": [
      { "term_id": "<TERM_ID>" }
    ]
  }'
```

**Response:** contains `"id": "<policy_id>"` — policy enforces the rule and is now associated with the given term(s).

> Depending on your version of the API, the `rules`/`terms` property may accept arrays of strings or objects. If required, use `"rules": ["<RULE_ID>"]` and `"terms": ["<TERM_ID>"]`. Check the Watson Data API docs: https://cloud.ibm.com/apidocs/watson-data-api#create-policy

---

## 5) Publish / Activate the Rule & Policy

Some environments require you to **publish** or **activate** the rule/policy or assign them to a catalog or project. Example (hypothetical endpoint):

```bash
curl -X POST "${CATALOG_API_BASE}/v3/enforcement/rules/${RULE_ID}/publish"   -H "Authorization: Bearer ${TOKEN}"   -H "Content-Type: application/json"   -d '{"catalog_id": "<CATALOG_ID>"}'
```

> Check your Knowledge Catalog docs for the exact publish/activation API for rules. In many cases, the rule becomes effective after creation if it is scoped to the correct catalog/project.

---

# How to extract IDs quickly (jq examples)

Assume the create command returns JSON with an `id` field.

```bash
# Example: create category and extract id
category_id=$(curl -s -X POST "${WATSONDATA_API_BASE}/v2/categories"   -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json"   -d '{"name":"PII","description":"PII","short_description":"PII"}'   | jq -r '.id')

echo "Category ID: $category_id"

# Create term and get id
term_id=$(curl -s -X POST "${WATSONDATA_API_BASE}/v2/terms"   -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json"   -d '{"name":"Email Address","short_description":"Email","categories":["'"${category_id}"'"]}'   | jq -r '.id')

echo "Term ID: $term_id"
```

Similarly for rule/policy:

```bash
rule_id=$(curl -s -X POST "${CATALOG_API_BASE}/v3/enforcement/rules" ... | jq -r '.id')
policy_id=$(curl -s -X POST "${WATSONDATA_API_BASE}/v2/policies" ... | jq -r '.id')
```

---

# Testing / validating masked data (login / call as Business User)

1. Obtain an IAM token for a user who has the **Business User** role (or simulate this by creating a service ID and assigning that role).
2. Query an asset (table) via the asset data or query endpoint:

```bash
curl -X GET "${CATALOG_API_BASE}/v2/assets/<asset_id>/data"   -H "Authorization: Bearer ${BUSINESS_USER_TOKEN}"   -H "Accept: application/json"
```

If masking rule & policy are in effect, the `email` column values should be redacted (e.g., replaced with `***` or `xxxxx`, depending on masking `method`).

---

# Permissions & notes / troubleshooting

- **Permissions:** The caller needs proper rights to create categories/terms/rules/policies. Typically a **Data Steward** or admin role is required.
- **API version differences:** Field names and endpoints can vary by service/API version. Always confirm with your instance’s API docs. The authoritative docs are:
  - Knowledge Catalog: https://cloud.ibm.com/apidocs/knowledge-catalog#introduction
  - Watson Data API: https://cloud.ibm.com/apidocs/watson-data-api#introduction

---

# References (read further)

- Watson Data API (categories / terms / policies):  
  https://cloud.ibm.com/apidocs/watson-data-api#introduction
- Knowledge Catalog — Create Rule:  
  https://cloud.ibm.com/apidocs/knowledge-catalog#createrule
- Knowledge Catalog / Dataplatform docs on masking and governance (how masking works):  
  https://dataplatform.cloud.ibm.com/docs/content/wsj/governance/data-protection-rules.html

---

