# Text2SQL Bob Skills

Bob skills for natural language to SQL using **IBM watsonx.data Intelligence** (DAI) on IBM Cloud.

## Overview

These skills empower IBM Bob to improve **IBM watsonx.data Intelligence Text2SQL** quality — enriching project metadata for maximum accuracy and diagnosing/tuning generated SQL quality — covering model selection, metadata enrichment, SQL validation, accuracy evaluation, and feedback loop design.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `text2sql-metadata-enrichment` | [`text2sql-metadata-enrichment.zip`](text2sql-metadata-enrichment.zip) | Enriching watsonx.data Intelligence project metadata (table/column descriptions, synonyms, relationships) to maximise Text2SQL accuracy |
| `text2sql-query-optimizer` | [`text2sql-query-optimizer.zip`](text2sql-query-optimizer.zip) | Evaluating and improving Text2SQL output quality — model selection, SQL validation, error diagnosis, accuracy metrics |

---

### `text2sql-metadata-enrichment`

A comprehensive skill for enriching IBM watsonx.data Intelligence project metadata:

- IBM watsonx.data Intelligence project onboarding (`PUT /onboard_for_text_2_sql`)
- Table and column description enrichment via DAI REST API
- Column synonym and relationship hint design
- Natural language query example authoring
- Quality improvement checklist and measurement patterns
- IBM Cloud IAM authentication
- Supported dialects: `presto`, `postgresql`, `mssql`, `oracle`, `snowflake`

### `text2sql-query-optimizer`

A comprehensive skill for evaluating and improving Text2SQL output quality:

- Model selection guide (Granite vs Llama for different query complexity)
- SQL safety validation (syntax check, dangerous keyword detection)
- Text2SQL accuracy evaluation with exact-match and execution accuracy metrics
- Error pattern diagnosis (missing metadata, wrong dialect, JOIN errors)
- Feedback loop design for iterative quality improvement
- Dialect tuning (presto, postgresql, mssql, oracle, snowflake)

---

## Installation

### Step 1 — Install the skill(s)

The zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip text2sql-metadata-enrichment.zip
unzip text2sql-query-optimizer.zip
```

This will create:
```
.bob/skills/text2sql-metadata-enrichment/SKILL.md
.bob/skills/text2sql-query-optimizer/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the desired skill(s). Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What Text2SQL skills do you have active?"*

---

## Usage Examples

### text2sql-metadata-enrichment
- *"Generate metadata enrichment code to add table descriptions for all tables in my watsonx.data Intelligence project"*
- *"Create column synonyms for the ORDER_DATE and CUSTOMER_ID fields to improve Text2SQL accuracy"*
- *"Walk me through onboarding my project for Text2SQL with the correct PUT request"*

### text2sql-query-optimizer
- *"Which model should I use for complex multi-join queries — Granite or Llama?"*
- *"Validate this generated SQL for safety issues before I run it against production"*
- *"Evaluate my Text2SQL pipeline against 50 test queries and report exact-match accuracy"*

---

## What Bob Can Help You Build

1. **Metadata Enrichment Scripts**: Python scripts to bulk-add table/column descriptions via DAI REST API
2. **Synonym Libraries**: Column synonym files for domain-specific terminology
3. **SQL Validators**: Syntax and safety checkers for Text2SQL output
4. **Accuracy Evaluators**: Test harness for measuring exact-match and execution accuracy
5. **Error Diagnosis Reports**: Analysis of common Text2SQL failure patterns
6. **Feedback Loop Tooling**: Iterative improvement pipelines for Text2SQL quality

---

## Prerequisites

Before using these skills, ensure you have:

- IBM watsonx.data Intelligence instance provisioned on IBM Cloud
- A watsonx.data Intelligence Project ID
- Data assets (Presto tables, COS files) imported into the project
- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- Region note: Text2SQL is supported in `ca-tor` (Toronto) region

## Skill Capabilities Summary

| Capability | text2sql-metadata-enrichment | text2sql-query-optimizer |
|---|---|---|
| Project Onboarding | ✅ | — |
| Table/Column Descriptions | ✅ | — |
| Column Synonyms | ✅ | — |
| Model Selection Guide | — | ✅ |
| SQL Safety Validation | — | ✅ |
| Accuracy Evaluation | — | ✅ |
| Error Diagnosis | — | ✅ |
| Feedback Loop Design | — | ✅ |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/text2sql-metadata-enrichment/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Text2SQL returns "No matches in metadata index":**
1. Run the project onboarding first: `PUT /semantic_automation/v1/onboard_for_text_2_sql`
2. Import your data assets into the project after onboarding

## Related

- [`../bob-modes/`](../bob-modes/) — Text2SQL Builder Bob Mode
- [`../README.md`](../README.md) — Text2SQL building block overview
- [`../assets/`](../assets/) — Metadata enrichment scripts and test datasets
