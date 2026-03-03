# Bob Modes

This directory contains custom Bob mode configurations that extend IBM Bob's capabilities with domain-specific expertise.

---

## Available Modes

### Data for AI Mode
**File:** [`data-ai-mode-config.yaml`](data-ai-mode-config.yaml:1)

A specialized mode for data engineering, data architecture, and AI/ML data operations.

**Capabilities:**
- Data Engineering: ETL/ELT pipelines, data ingestion, validation
- Data Architecture: Schema design, data modeling, technology selection
- AI/ML Data: RAG systems, NL2SQL, vector databases, embeddings
- Data Operations: Quality checks, monitoring, security, documentation

**Use Cases:**
- Building data pipelines
- Designing database schemas
- Implementing RAG systems
- Creating NL2SQL engines
- Setting up vector databases
- Data quality and profiling

---

## Installing Bob Modes

### Method 1: Copy to Bob's Modes Directory

**Windows:**
```powershell
Copy-Item data-ai-mode-config.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux/Mac:**
```bash
cp data-ai-mode-config.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

### Method 2: Reference from Current Location

Edit Bob's configuration to reference modes from this directory.

