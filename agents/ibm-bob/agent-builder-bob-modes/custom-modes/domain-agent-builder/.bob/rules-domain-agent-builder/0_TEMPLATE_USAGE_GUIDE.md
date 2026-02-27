# Healthcare Agent Template Usage Guide

## Overview

The **healthcare-assistant-agent** is the reference template for building new WXO agents. Unlike the old agent-template which used placeholders, the healthcare agent is a **proven, deployed, working agent** that demonstrates all the correct patterns.

## Why Use Healthcare Agent as Template?

### ✅ Advantages
1. **Actually Works** - It's deployed and live on WXO
2. **Zero Placeholders** - All real values, no risk of missing replacements
3. **Correct Technical Patterns** - Uses proper YAML formats and tool structures
4. **Domain-Specific Naming** - Shows how to use domain terminology
5. **Production-Ready** - Clean, tested, deployable code

### ❌ Old Template Problems
1. **Never Deployed** - Theoretical, not proven
2. **50+ Placeholders** - Easy to miss during customization
3. **Wrong YAML Format** - Used incorrect `kind: internal` format
4. **Generic Naming** - Didn't show domain-specific patterns
5. **Bloated** - 220-line config vs 84-line healthcare config

## Mandatory Rules (Apply to ALL Agents)

Before customizing, memorize these non-negotiable rules:

| Rule | Correct | Wrong |
|------|---------|-------|
| LLM | `llm: groq/openai/gpt-oss-120b` | Any other model (llama, granite, etc.) |
| Spec version | `spec_version: v1` (first line) | Missing or wrong |
| Name format | `customer_service_agent` | `customer-service-agent` |
| KB format | `embeddings_model_name: ibm/slate-125m-english-rtrvr-v2` | `kind: internal` |
| Tool data | Embedded Python dicts | CSV file loading |
| Tool isolation | Self-contained | Cross-tool imports |
| Max tools | 5 | More than 5 |
| Deploy commands | `uvx --from ibm-watsonx-orchestrate orchestrate ...` | Direct `orchestrate ...` |

## How to Use Healthcare Agent as Template

### Step 1: Copy the Healthcare Agent
```bash
cp -r .bob/healthcare-assistant-agent ./[your-agent-name]-agent
cd ./[your-agent-name]-agent
```

### Step 2: Find and Replace Domain Terms

Use your editor's find/replace to change these terms throughout all files:

| Healthcare Term | Your Domain Term | Example |
|----------------|------------------|---------|
| `patient` | `customer/member/user` | `patient_tools.py` → `customer_tools.py` |
| `care_level` | `tier/segment/level` | `care_level` → `membership_tier` |
| `PAT001` | `CUST001/MEM001` | ID format |
| `healthcare` | `retail/finance/etc` | Domain name |
| `Healthcare Assistant` | `Your Agent Name` | Display name |

### Step 3: Update Key Files

#### 1. agent_config.yaml
- Change `name:` to your agent name (use underscores)
- Update `display_name:` 
- Rewrite `description:` for your domain
- Update tier names (Outpatient/Inpatient/ICU/Emergency → your tiers)
- Customize capabilities and instructions
- Update tool names to match your domain

#### 2. tools/patient_tools.py → tools/[entity]_tools.py
- Rename file to match your entity type
- Update `PATIENT_DATA` to your entity data structure
- Change function names (`get_patient_data` → `get_customer_data`)
- Update field names to match your domain
- Add 5-10 realistic sample records

#### 3. tools/communication_tools.py
- Update communication types for your domain
- Customize HTML templates with your branding
- Change tier-specific styling
- Update message content for your use case

#### 4. data/patients.csv → data/[entities].csv
- Rename file to match your entity type
- Update column headers for your domain
- Generate 5-10 realistic sample records
- Include all tier levels in data

#### 5. knowledge_bases/healthcare_patient_kb.yaml → knowledge_bases/[domain]_kb.yaml
- Rename file to match your domain
- Update `name:` (use underscores, not hyphens)
- Update `description:`
- Update document paths to match your data files
- Keep the correct `embeddings_model_name` format

#### 6. scripts/*.sh
- Update agent name references
- Update display name in messages
- Customize test queries

#### 7. README.md
- Rewrite for your domain
- Update examples and queries
- Document your specific capabilities

### Step 4: Clean Up Healthcare-Specific Files
```bash
rm -rf docs/  # Remove healthcare presentation files
rm .env       # Remove healthcare API key (create your own)
```

### Step 5: Deploy
```bash
# Create your .env file
echo "WXO_API_KEY=your-key-here" > .env

# Make scripts executable
chmod +x scripts/*.sh

# Deploy
./scripts/deploy_all.sh
```

## Critical Patterns from Healthcare Agent

### 1. Correct Knowledge Base Format
```yaml
vector_index:
  embeddings_model_name: ibm/slate-125m-english-rtrvr-v2
```
**NOT:**
```yaml
vector_index:
  kind: internal
  embedding_model: ibm/slate-125m-english-rtrvr
```

### 2. Domain-Specific Tool Naming
✅ **Good:** `get_patient_data()`, `get_patients_by_care_level()`
❌ **Bad:** `get_entity_data()`, `get_entities_by_tier()`

### 3. Self-Contained Communication Tools
Tools CANNOT call other tools. Each must embed its own data:
```python
# Embedded data — each tool has its own copy
PATIENT_DATA = [
    {"patient_id": "PAT001", "name": "Sarah Johnson", "care_level": "Outpatient", ...},
]

@tool
def generate_patient_communication(
    patient_id: str,
    communication_type: str,
    additional_context: Optional[str] = None
) -> Dict[str, Any]:
    # Look up from embedded data (NOT from other tools, NOT from CSV)
    patient = next((p for p in PATIENT_DATA if p["patient_id"] == patient_id), None)
    if not patient:
        return {"error": f"Patient {patient_id} not found"}
    # ... generate HTML ...
```

### 4. Real Data Structures
Match your Python data structure to your CSV structure exactly:
```python
PATIENT_DATA = [
    {
        "patient_id": "PAT001",
        "name": "Sarah Johnson",
        "care_level": "Outpatient",
        # ... matches patients.csv columns
    }
]
```

### 5. Clean Agent Config
- 84 lines total
- No commented sections
- No unnecessary config blocks
- Simple tool list (just names)

### 6. Automated Deployment
```bash
#!/bin/bash
set -e  # Exit on error
# No interactive prompts
# Runs straight through
```

## Domain Mapping Examples

### Healthcare → Retail
- `patient` → `customer`
- `care_level` → `loyalty_tier`
- `PAT001` → `CUST001`
- `Outpatient/Inpatient/ICU/Emergency` → `Basic/Silver/Gold/Platinum`
- `appointment_confirmation` → `order_confirmation`

### Healthcare → Finance
- `patient` → `client`
- `care_level` → `account_tier`
- `PAT001` → `CLI001`
- `Outpatient/Inpatient/ICU/Emergency` → `Basic/Preferred/Private/Wealth`
- `lab_result_alert` → `transaction_alert`

### Healthcare → Education
- `patient` → `student`
- `care_level` → `enrollment_tier`
- `PAT001` → `STU001`
- `Outpatient/Inpatient/ICU/Emergency` → `Free/Basic/Premium/Enterprise`
- `appointment_confirmation` → `class_enrollment`

## Validation Checklist

Before deploying, verify:
- [ ] `spec_version: v1` is the first line of agent_config.yaml and KB YAML
- [ ] `llm: groq/openai/gpt-oss-120b` is set (NOT llama, granite, or other models)
- [ ] All "patient" references changed to your entity type
- [ ] All "care_level" references changed to your tier name
- [ ] All file names updated (patient_tools.py → [entity]_tools.py)
- [ ] Knowledge base name uses underscores (not hyphens)
- [ ] Knowledge base uses `embeddings_model_name` format
- [ ] Agent name uses underscores (not hyphens)
- [ ] All tool names are domain-specific
- [ ] Maximum 5 tools total
- [ ] All tools embed data as Python dicts (no CSV file loading)
- [ ] Communication tools are self-contained (no cross-tool imports)
- [ ] Sample data is realistic for your domain
- [ ] All tiers represented in sample data
- [ ] Communication types match your domain
- [ ] README updated for your domain
- [ ] .env file created with your API key
- [ ] entity_tools.py deleted (it has unfilled placeholders; use patient_tools.py instead)

## Common Mistakes to Avoid

1. **Don't use wrong LLM** — ALWAYS use `groq/openai/gpt-oss-120b`
2. **Don't forget spec_version** — ALWAYS start YAML with `spec_version: v1`
3. **Don't use hyphens** — Agent, KB, and tag names must use underscores
4. **Don't use `kind: internal` in KB** — Use `embeddings_model_name` format
5. **Don't load CSV in tools** — Embed data as Python dicts (WXO can't access local files)
6. **Don't call other tools** — Each tool must be self-contained
7. **Don't keep entity_tools.py** — It has unfilled placeholders; use patient_tools.py as base
8. **Don't exceed 5 tools** — Maximum 5 per agent
9. **Don't use placeholders** — Replace with real values immediately
10. **Don't make scripts interactive** — Keep deployment automated

## Getting Help

If you encounter issues:
1. Compare your files to the healthcare agent
2. Check the TROUBLESHOOTING.md in healthcare agent
3. Verify all find/replace operations completed
4. Ensure YAML syntax is valid
5. Check that all file paths are correct

## Summary

The healthcare-assistant-agent is your **working template**. It's not a "fill-in-the-blanks" template - it's a **find-and-replace template**. Copy it, replace domain terms, customize for your use case, and deploy. This approach is proven to work because the healthcare agent itself is deployed and working.