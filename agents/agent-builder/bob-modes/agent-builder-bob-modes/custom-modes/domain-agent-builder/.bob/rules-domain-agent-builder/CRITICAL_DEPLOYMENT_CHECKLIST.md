# Critical Deployment Checklist for WXO Agents

This checklist covers the most common deployment failures. **Check ALL items before deploying.**

## ⚠️ Issue 1: Agent Naming (CRITICAL)

### Rule
Agent names MUST use underscores (_), NEVER hyphens (-)

### ✅ Correct Examples
```yaml
name: customer_service_agent
name: healthcare_assistant_agent
name: retail_customer_agent
name: personal_asset_management_agent
```

### ❌ Incorrect Examples (WILL FAIL)
```yaml
name: customer-service-agent
name: healthcare-assistant-agent
name: retail-customer-agent
```

### Where to Check
- `agent_config.yaml` - line with `name:`
- Project directory name (should match agent name)

---

## ⚠️ Issue 2: Knowledge Base Naming (CRITICAL)

### Rule
Knowledge base names MUST use underscores (_), NEVER hyphens (-)

### ✅ Correct Examples
```yaml
name: healthcare_kb
name: retail_customer_kb
name: asset_management_kb
```

### ❌ Incorrect Examples (WILL FAIL)
```yaml
name: healthcare-kb
name: retail-customer-kb
name: asset-management-kb
```

### Where to Check
- `knowledge_bases/*.yaml` - line with `name:`
- `agent_config.yaml` - `knowledge_bases:` section

## ⚠️ Issue 4: Tags Format (CRITICAL)

### Rule
Tags MUST use underscores (_), NEVER hyphens (-)

### ✅ Correct Examples
```yaml
tags:
  - finance
  - investment
  - portfolio_management
  - asset_tracking
  - customer_service
```

### ❌ Incorrect Examples (WILL FAIL)
```yaml
tags:
  - portfolio-management
  - asset-tracking
  - customer-service
```

### Where to Check
- `agent_config.yaml` - `tags:` section at the end of file

---

---

## ⚠️ Issue 3: Knowledge Base Vector Index Format (CRITICAL)

### Rule
Use `embeddings_model_name` format for vector index configuration.

### ✅ Correct Format
```yaml
vector_index:
  embeddings_model_name: ibm/slate-125m-english-rtrvr-v2
```

### ❌ Incorrect Format (WILL FAIL)
```yaml
vector_index:
  kind: internal
  embedding_model: ibm/slate-125m-english-rtrvr
```

### Proof
The deployed, working `healthcare_patient_kb.yaml` uses `embeddings_model_name: ibm/slate-125m-english-rtrvr-v2`.

### Where to Check
- All files in `knowledge_bases/` directory
- Look for `vector_index:` section

---

## Additional Checks

### Spec Version
```yaml
spec_version: v1  # lowercase 'v'
```

### File Paths
- All paths in knowledge base YAML must be relative: `../data/file.csv`
- Verify all referenced files exist

### Tool Names
- Tool names in `agent_config.yaml` must match actual tool function names
- Tool functions must have `@tool` decorator

---

## Pre-Deployment Validation Script

Run these checks before deploying:

```bash
# Check for hyphens in agent name
grep "^name:" agent_config.yaml | grep "\-" && echo "ERROR: Agent name has hyphens!" || echo "✓ Agent name OK"

# Check for hyphens in KB names
grep "^name:" knowledge_bases/*.yaml | grep "\-" && echo "ERROR: KB name has hyphens!" || echo "✓ KB names OK"

# Check for hyphens in tags (look for pattern like "word-word" after "  - ")
sed -n '/^tags:/,/^[^ ]/p' agent_config.yaml | grep "^  - " | grep -E "[a-z]\-[a-z]" && echo "ERROR: Tags have hyphens!" || echo "✓ Tags OK"

# Check KB vector index format is correct (embeddings_model_name)
grep "embeddings_model_name" knowledge_bases/*.yaml > /dev/null && echo "✓ KB format OK" || echo "ERROR: KB missing embeddings_model_name!"

# Check for incorrect kind:internal format
grep "kind: internal" knowledge_bases/*.yaml && echo "ERROR: Using wrong kind:internal format!" || echo "✓ No kind:internal"

# Check spec version
grep "^spec_version:" agent_config.yaml | grep -v "v1" && echo "ERROR: Wrong spec version!" || echo "✓ Spec version OK"

# Check LLM
grep "^llm: groq/openai/gpt-oss-120b" agent_config.yaml > /dev/null && echo "✓ LLM OK" || echo "ERROR: Wrong LLM! Must be groq/openai/gpt-oss-120b"

# Check for file system access in tools (should not exist in deployed tools)
grep -rn "os.path\|open(\|csv.DictReader\|csv.reader" tools/ && echo "ERROR: Tools using file system access!" || echo "✓ No file system access in tools"
```

---

## Common Error Messages

### "Invalid agent name"
- **Cause**: Agent name contains hyphens
- **Fix**: Change all hyphens to underscores in `name:` field

### "Knowledge base import failed"
- **Cause 1**: KB name contains hyphens
- **Fix**: Change KB name to use underscores
- **Cause 2**: Wrong vector_index format
- **Fix**: Use `embeddings_model_name: ibm/slate-125m-english-rtrvr-v2` format

### "Invalid spec version"
- **Cause**: Using uppercase 'V' or wrong version
- **Fix**: Use exactly `spec_version: v1`

---

## Quick Reference

| Item | Must Use | Never Use |
|------|----------|-----------|
| Agent name separator | underscore `_` | hyphen `-` |
| KB name separator | underscore `_` | hyphen `-` |
| Tag separator | underscore `_` | hyphen `-` |
| Vector index format | `embeddings_model_name: ibm/slate-125m-english-rtrvr-v2` | `kind: internal` / `embedding_model:` |
| Spec version | `spec_version: v1` | anything else |
| LLM | `groq/openai/gpt-oss-120b` | llama, granite, mixtral, etc. |
| Tool data access | Embedded Python dicts | CSV file loading |
| Tool dependencies | Self-contained | Cross-tool imports |
| Max tools | 5 | More than 5 |

---

## ⚠️ Issue 5: Post-Deployment Testing (CRITICAL)

### Rule
ALWAYS test the agent after deployment before considering it complete

### Why This Matters
- Deployment success ≠ Agent works correctly
- Data access issues only appear when tools run in WXO
- "Entity not found" errors indicate embedded data problems
- Testing catches issues before users encounter them

### Required Tests

#### 1. Entity Retrieval Test
```
Query: "Get [entity_type] [FIRST_ID_FROM_DATA]"
Example: "Get customer CUS001" or "Get student STU001"
Expected: Should return entity details
If fails: Data access problem - tool cannot read embedded data
```

#### 2. Communication Generation Test
```
Query: "Generate [report/notification] for [FIRST_ID]"
Example: "Generate progress report for STU001"
Expected: Should return HTML-formatted output with entity data
If fails: Most common issue - "Entity not found" error
Root cause: Tool trying to load from CSV instead of embedded data
```

#### 3. Filtering Test
```
Query: "Show me all [tier/status] [entity_type]"
Example: "Show me all Premium customers"
Expected: Should return filtered list
```

#### 4. Metrics Test
```
Query: "Calculate metrics for [entity_type]"
Example: "Calculate customer metrics"
Expected: Should return calculated values
```

### Common Test Failures

#### "Entity with ID XXX not found"
- **Root Cause**: Tool trying to load data from CSV files
- **Why It Happens**: WXO tools cannot access local files
- **Fix**:
  1. Update tool to embed data as Python dictionaries
  2. Remove CSV loading code (os.path, open(), csv.DictReader)
  3. Re-import tools: `uvx --from ibm-watsonx-orchestrate orchestrate tools import -k python -f tools/tool.py`
  4. Redeploy agent: `uvx --from ibm-watsonx-orchestrate orchestrate agents deploy --name agent_name`
  5. Re-test with same query

#### Tool doesn't respond or times out
- **Root Cause**: Tool has errors or infinite loops
- **Fix**: Check tool logs, review code, fix errors, re-import

#### Incorrect or incomplete output
- **Root Cause**: Logic errors or data structure mismatches
- **Fix**: Verify embedded data structure, check field names, fix logic

### Testing Checklist

- [ ] Agent appears in WXO interface
- [ ] Entity retrieval works with known IDs
- [ ] Communication generation produces HTML output
- [ ] No "entity not found" errors
- [ ] No "file not found" errors
- [ ] Filtering and search work correctly
- [ ] Metrics calculations are accurate
- [ ] Error handling works gracefully
- [ ] Agent responds within 10 seconds

### When to Proceed

✅ **Proceed to documentation when:**
- All critical tests pass
- No data access errors
- Communication tools generate proper output
- Any issues discovered have been fixed and re-tested

❌ **DO NOT proceed if:**
- Any critical test fails
- "Entity not found" errors occur
- Tools cannot access embedded data
- Agent doesn't respond

---

## If Deployment Still Fails

1. **Copy the exact error message**
2. **Check which step failed** (tools, KB, or agent)
3. **Verify all three critical issues above**
4. **Check file paths** in knowledge base YAML
5. **Verify tool names** match between config and Python files
6. **Check .env file** has valid WXO_API_KEY

---

## If Tests Fail After Deployment

1. **Identify the failing test** (entity retrieval, communication, etc.)
2. **Check the error message** (especially "entity not found")
3. **Verify data access method** (embedded vs file loading)
4. **Fix the issue** (update tool code)
5. **Re-import tools** (uvx orchestrate tools import)
6. **Redeploy agent** (uvx orchestrate agents deploy)
7. **Re-test** (same query that failed)
8. **Repeat until all tests pass**

---

**Last Updated**: 2026-02-09
**Template Version**: 3.0