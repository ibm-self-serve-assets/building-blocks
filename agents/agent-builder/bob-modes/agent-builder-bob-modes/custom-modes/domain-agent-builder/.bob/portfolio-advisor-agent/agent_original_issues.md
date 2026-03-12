# Portfolio Advisor Agent — Original Issues & Fixes

This document lists every issue found in the original `portfolio_advisor_agent` configuration and the fixes applied to make the agent (and its RAG pipeline) work correctly with the WXO ADK evaluation framework.

---

## 1. Duplicate `tags` Section in `agent_config.yaml`

**Problem:** The `tags:` block was duplicated — it appeared twice at the end of the file. YAML parsers silently use the last occurrence, but this is confusing and error-prone.

**Original (broken):**
```yaml
tags:
  - finance
  - investment
  - portfolio_management
  - wealth_management
  - asset_tracking

tags:
  - finance
  - investment
  - portfolio_management
  - wealth_management
  - asset_tracking
```

**Fix:** Removed the duplicate block. Kept a single `tags:` section.

---

## 2. Knowledge Base Field Name: Plural vs Singular

**Problem:** The agent config used `knowledge_bases:` (plural), but the WXO platform expects `knowledge_base:` (singular). The platform silently accepted the import without error, but **never actually linked the KB to the agent**. Exporting the agent from the platform confirmed `knowledge_base: []` (empty).

**Original (broken):**
```yaml
knowledge_bases:
  - finance_portfolio_kb
```

**Fix:**
```yaml
knowledge_base:
  - finance_portfolio_kb
```

**How we found it:** Exported the agent config from the platform using `orchestrate agents export -k native -n portfolio_advisor_agent -o export.zip` and inspected the resulting YAML. The `knowledge_base` field was `[]` despite our config referencing the KB.

---

## 3. RAG / Conversational Search Not Enabled (`chat_with_docs`)

**Problem:** Even after fixing the KB field name, the agent still did not query the knowledge base. The exported agent config revealed a `chat_with_docs` section that was `enabled: false` by default. Without this, the RAG retrieval pipeline never triggers — the agent has no mechanism to search the KB.

**Original (missing):** The `chat_with_docs` section was not present in the agent config at all. The platform defaults to `enabled: false`.

**Fix:** Added the following to `agent_config.yaml`:
```yaml
chat_with_docs:
  enabled: true
  generation:
    enabled: true
```

**How we found it:** Exported the agent from the platform and saw:
```yaml
chat_with_docs:
  enabled: false
  ...
  generation:
    ...
    enabled: false
```

Both the top-level `enabled` and `generation.enabled` needed to be `true` for RAG to work.

---

## 4. Knowledge Base Documents: Markdown Files Not Supported

**Problem:** The knowledge base YAML referenced `.md` (Markdown) files, but the WXO platform does not support Markdown as a document format for KB ingestion. Import failed with:
```
Error importing knowledge base 'finance_portfolio_kb': Unsupported file type text/markdown for file named investment_policies.md
```

**Original (broken):**
```yaml
documents:
  - ../data/account_holders.csv
  - ../data/investment_policies.md
  - ../data/compliance_guidelines.md
```

**Fix:** Copied the `.md` files to `.txt` format and updated the KB YAML:
```yaml
documents:
  - ../data/account_holders.csv
  - ../data/investment_policies.txt
  - ../data/compliance_guidelines.txt
```

**Supported formats:** CSV, TXT, PDF, DOCX (per the TROUBLESHOOTING.md).

---

## 5. Agent Instructions Did Not Reference the Knowledge Base

**Problem:** The original agent instructions made no mention of the knowledge base. The agent had no guidance to consult the KB for policy, fee, or compliance questions. As a result, even if RAG had been enabled, the LLM would default to answering from its own training data — producing hallucinated numbers (e.g., saying the Gold tier rebalancing frequency is "Quarterly" when the KB says "Monthly").

**Original (missing):** No mention of KB in the `instructions` field.

**Fix:** Added a `## Knowledge Base` section to the instructions:
```yaml
instructions: |
  ...
  ## Knowledge Base
  You have access to a knowledge base (finance_portfolio_kb) containing important reference documents:
  - **Investment Policies**: Fee schedules, rebalancing thresholds by tier, minimum investment requirements, target asset allocations, prohibited investments, and account upgrade policies.
  - **Compliance Guidelines**: KYC documentation requirements, AML transaction monitoring thresholds, suitability requirements, data privacy policies, and regulatory reporting obligations.
  - **Account Holder Data**: Account holder profiles and portfolio information.

  **IMPORTANT**: When answering questions about fees, policies, rebalancing thresholds, compliance requirements, KYC/AML rules, or any regulatory topic, you MUST consult your knowledge base to provide accurate, up-to-date information. Do NOT rely on general knowledge — always retrieve the specific policy details from your knowledge base.
  ...
```

Also added to the Key Behaviors list:
```yaml
  - Consult the knowledge base for all policy, fee, and compliance questions
```

---

## 6. Knowledge Base Not Imported / Indexed

**Problem:** The knowledge base was referenced in the agent config but was never actually imported into the platform. Running `orchestrate knowledge-bases list` returned an empty table. Without importing, the documents are never vectorized and indexed, so there is nothing for the RAG pipeline to search.

**Fix:** Ran the import command from the agent directory:
```bash
cd portfolio-advisor-agent
orchestrate knowledge-bases import -f knowledge_bases/finance_portfolio_kb.yaml
```

Then verified with:
```bash
orchestrate knowledge-bases list
orchestrate knowledge-bases status -n finance_portfolio_kb
```

The status confirmed: `Ready: True`, `Built In Index Status: ready`, all 3 documents listed.

---

## 7. Tool Import Order (Not Agent-Specific but Critical)

**Problem:** The original workflow attempted to import the agent before its tools were registered. The agent config references tools by name (`get_account_holder_data`, etc.), but these must exist in the platform first.

**Error:**
```
Failed to find tool: get_account_holder_data
```

**Fix:** Import tools first, then the agent:
```bash
# Step 1: Import all tool files
orchestrate tools import -k python -f tools/account_holder_tools.py
orchestrate tools import -k python -f tools/communication_tools.py

# Step 2: Import the agent (which references the tools by name)
orchestrate agents import -f agent_config.yaml
```

---

## Summary of All Changes to `agent_config.yaml`

| Issue | What Changed | Impact |
|-------|-------------|--------|
| Duplicate `tags` | Removed duplicate block | Cleaner config |
| `knowledge_bases` → `knowledge_base` | Fixed field name (plural → singular) | KB actually linked to agent |
| Missing `chat_with_docs` | Added with `enabled: true` | RAG retrieval pipeline activated |
| Missing KB instructions | Added `## Knowledge Base` section to instructions | Agent knows to consult KB for policy questions |
| Missing KB behavior | Added "Consult the knowledge base..." to Key Behaviors | Reinforces KB usage |

## Summary of All Changes to `finance_portfolio_kb.yaml`

| Issue | What Changed | Impact |
|-------|-------------|--------|
| `.md` files not supported | Changed to `.txt` file references | KB import succeeds |
| Documents not imported | Ran `orchestrate knowledge-bases import` | Documents vectorized and searchable |

## Evaluation Results After Fixes

| Scenario | Before Fixes | After Fixes | KB Metrics |
|----------|-------------|-------------|------------|
| 07 — RAG Investment Policy | 0% journey success (hallucinated answers) | **100%** journey success | Faithfulness: 1.0, Relevancy: 1.0 |
| 08 — RAG Compliance & Action | 0% journey success (agent refused to answer) | **100%** journey success | Faithfulness: 1.0, Relevancy: 0.857 |

---

## Debugging Methodology

The key debugging technique was **exporting the agent config from the platform** and comparing it with our source YAML:

```bash
orchestrate agents export -k native -n portfolio_advisor_agent -o export.zip
```

This revealed discrepancies between what we thought we configured and what the platform actually stored — particularly the empty `knowledge_base: []` and `chat_with_docs: enabled: false` defaults that were invisible from the import side.

Similarly, checking KB status was essential:
```bash
orchestrate knowledge-bases status -n finance_portfolio_kb
```

This confirmed the KB was indexed (`Ready: True`) even when the agent wasn't using it — narrowing the problem to the agent-to-KB linkage rather than the KB itself.
