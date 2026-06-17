# Asset Management — Building Blocks

**Core Capability**: Build & Deploy
**IBM Products**: IBM Maximo Application Suite (MAS)
**Product Components**: Maximo REST API (OSLC); Maximo Automation Scripts; OpenAI GPT-4; IBM Code Engine; Docker; Node.js; React

## Overview

Building blocks for **IBM Maximo Application Suite (MAS)** code modernization — covering AI-powered automation script analysis and optimisation, Java-to-automation-script conversion, security scanning, performance improvement, and deployment. Includes a full-stack web application (**Maximo Modernization Asset**) and two IBM Bob skills that bring expert Maximo modernization tooling directly to your workflow.

**Modernization covers two complementary capabilities:**
- **Script Optimization** — analyse and AI-optimise existing Maximo automation scripts (security, performance, best practices)
- **Java Conversion** — convert legacy Maximo Java classes into automation scripts (Python, Jython, JavaScript, Nashorn, ECMAScript, MBR)

> **AI-tool agnostic**: The runnable asset works independently of any AI assistant. The Bob skills are optimised for IBM Bob but the patterns apply to any AI coding assistant.

---

## When to Use

| Scenario | Use |
|---|---|
| Analyse existing Maximo automation scripts for security vulnerabilities | [`assets/maximo_code_modernization_asset/`](assets/maximo_code_modernization_asset/) → Script Analyzer |
| AI-optimise Maximo scripts (error handling, MboSet cleanup, caching, transactions) | [`assets/maximo_code_modernization_asset/`](assets/maximo_code_modernization_asset/) → Script Optimizer |
| Convert legacy Maximo Java classes to Python/Jython/JavaScript automation scripts | [`assets/maximo_code_modernization_asset/`](assets/maximo_code_modernization_asset/) → Code Conversion |
| Run batch Java-to-script conversion across multiple Java files | [`assets/maximo_code_modernization_asset/`](assets/maximo_code_modernization_asset/) → Batch Code Conversion |
| Run impact analysis on a script before modifying it in production | [`assets/maximo_code_modernization_asset/`](assets/maximo_code_modernization_asset/) → Impact Analysis |
| Let IBM Bob fetch, analyse, and optimise Maximo scripts from a single prompt | [`bob-skills/maximo-code-optimization.zip`](bob-skills/maximo-code-optimization.zip) |
| Let IBM Bob convert Maximo Java classes to automation scripts interactively | [`bob-skills/maximo_java_conversion.zip`](bob-skills/maximo_java_conversion.zip) |
| Deploy the modernization tool as a containerised service on IBM Code Engine | `assets/maximo_code_modernization_asset/` → Docker build |

> **Which to start with?** Use the **web asset** for a visual dashboard experience. Use the **Bob skills** when you want to work directly in your IDE or terminal with AI guidance.

---

## Getting Started

### Prerequisites

- **IBM Maximo Application Suite** instance with REST API access enabled
- **Maximo API key** — generate in MAS → Security → API Keys
- **OpenAI API key** — for AI-powered script optimisation ([platform.openai.com](https://platform.openai.com/api-keys))
- **Node.js v14+** and **npm** installed locally
- (Optional) **Docker** — for containerised deployment to IBM Code Engine

### Quick Start — Modernization Web App

```bash
cd assets/maximo_code_modernization_asset

# 1. Configure credentials
cp backend/.env.template backend/.env
# Edit backend/.env:
#   MAXIMO_BASE_URL   — your Maximo server URL (e.g. https://maximo.example.com)
#   MAXIMO_API_KEY    — your Maximo API key
#   OPENAI_API_KEY    — your OpenAI API key
#   PORT=5000

# 2. Install and start the backend
cd backend
npm install
npm start
# Backend API → http://localhost:5000

# 3. Install and start the frontend (new terminal)
cd ../frontend
npm install
npm run dev
# Frontend UI → http://localhost:3000
```

Open `http://localhost:3000`. Navigate to **Maximo Configuration**, enter your server URL and API key, then click **Test Connection**. From the dashboard you can:
- **Optimize Scripts** — select any script for AI-powered security and performance analysis
- **Convert Code** — paste or upload a Java class and select a target language
- **Batch Convert** — convert multiple Java files at once
- **Impact Analysis** — assess what a script change would affect

### Quick Start — IBM Bob Skills

```bash
# From the root of your Bob workspace project
unzip bob-skills/maximo-code-optimization.zip
unzip bob-skills/maximo_java_conversion.zip
```

Open IBM Bob → Skills panel → enable `maximo-code-optimization` and/or `maximo-java-conversion`.

Then ask Bob:
```
Use skill maximo-code-optimization and optimize my scripts

Use skill maximo-java-conversion to convert my Java classes to Python
```

### Deploy with Docker (IBM Code Engine)

```bash
cd assets/maximo_code_modernization_asset

docker build -t maximo-modernization .

docker run -p 8080:8080 \
  -e MAXIMO_BASE_URL=https://your-maximo-server.com \
  -e MAXIMO_API_KEY=your-api-key \
  -e OPENAI_API_KEY=your-openai-key \
  maximo-modernization
# App → http://localhost:8080
```

For IBM Code Engine deployment, push the image to IBM Container Registry and create a Code Engine application pointing to it.

---

## Building Blocks

### 1. Maximo Code Modernization Asset

**Location**: [`assets/maximo_code_modernization_asset/`](assets/maximo_code_modernization_asset/)
**Stack**: Node.js (Express) backend + React (Vite) frontend
**Description**: Full-stack web application that connects to a live Maximo environment via REST API and provides a unified dashboard for script optimization and Java-to-script code conversion.

#### Script Optimization

Connects to `MXAPIAUTOSCRIPT` and provides AI-powered analysis and optimisation:

| Capability | Description |
|---|---|
| **Script Dashboard** | Fetches all automation scripts, displays metrics and language breakdown |
| **Security Analysis** | Detects SQL injection, input validation gaps, JSON/XML injection, auth context issues |
| **Performance Optimisation** | Identifies missing `MboSet.close()`, uncached queries, loop inefficiencies |
| **AI Optimisation** | GPT-4 applies Maximo best practices (error handling, MboSet lifecycle, logging, transactions) |
| **Push Back to Maximo** | Writes the optimised script directly back to Maximo via REST `PUT` |

#### Java Code Conversion

Converts legacy Maximo Java classes to automation scripts without requiring a live Maximo connection:

| Capability | Description |
|---|---|
| **Single File Conversion** | Upload or paste a Java class and convert to a chosen target language |
| **Batch Conversion** | Convert multiple Java files in one operation |
| **Business Logic Preservation** | Retains original validation rules, field updates, status transitions |
| **Test Script Generation** | Auto-generates a test script alongside the converted automation script |
| **Conversion Report** | Before/after comparison, mandatory rule validation, deployment guidance |

#### Supported Target Languages

| Language | Engine | Version |
|---|---|---|
| Python (Jython) | Jython | 2.7.4 |
| JavaScript | Nashorn | 15.6 |
| Nashorn | Nashorn | 15.6 |
| ECMAScript | Nashorn | 15.6 |
| Maximo Business Rules (MBR) | MBR | 1.0 |

#### Analysis Coverage (both capabilities)

| Category | Checks |
|---|---|
| Security | SQL injection, input validation, JSON/XML injection, auth context |
| Resource management | MboSet lifecycle (`close()`), connection pool leaks, memory leaks |
| Error handling | Try-catch-finally, MXLoggerFactory logging, graceful degradation |
| Performance | Query caching, loop efficiency, batch operations |
| Code quality | Null safety, logic validation, documentation |

[View Asset README →](assets/maximo_code_modernization_asset/README.md)

---

## Bob Skills

**Location**: [`bob-skills/`](bob-skills/)

Two Bob skills are available — each focused on one modernization task. Both are pre-structured so installation is a single `unzip` from your project root.

| Skill | Zip | What Bob Does |
|---|---|---|
| `maximo-code-optimization` | [`maximo-code-optimization.zip`](bob-skills/maximo-code-optimization.zip) | Fetches scripts from Maximo, analyses for security/performance issues, generates optimised versions and before/after reports |
| `maximo-java-conversion` | [`maximo_java_conversion.zip`](bob-skills/maximo_java_conversion.zip) | Converts Maximo Java classes to automation scripts in any supported language, validates business logic preservation, generates conversion reports |

### Install

```bash
# From the root of your Bob workspace project
unzip bob-skills/maximo-code-optimization.zip
unzip bob-skills/maximo_java_conversion.zip
```

This creates:
```
.bob/skills/maximo-code-optimization/   ← optimization skill
.bob/skills/maximo-java-conversion/     ← java conversion skill
```

Open IBM Bob → Skills panel → enable the skill(s) you need.

### `maximo-code-optimization` — Example Prompts

```
Use skill maximo-code-optimization and optimize my scripts

Use skill maximo-code-optimization to analyze MX_WO_SCRIPT for security issues

Use skill maximo-code-optimization to review all scripts before production deployment
```

Bob output structure:
```
maximo-scripts/
├── original/          # Originals fetched from Maximo
├── optimized/         # Optimised versions with fixes applied
└── reports/
    └── SUMMARY_REPORT.md
```

### `maximo-java-conversion` — Example Prompts

```
Use skill maximo-java-conversion to convert my Java classes to Python

Use skill maximo-java-conversion to convert WorkOrderValidator.java to Jython

Use skill maximo-java-conversion to convert all Java files in java-input/ to JavaScript
```

Place your `.java` files in `java-input/` before asking Bob. Bob output structure:
```
output-script/
├── python/            # Python (Jython) converted scripts
├── javascript/        # JavaScript converted scripts
└── ...
conversion-reports/
└── <ClassName>_conversion_report.md
```

See [`bob-skills/README.md`](bob-skills/README.md) for full installation and usage details.

---

## Architecture

```
IBM Maximo Application Suite
  MXAPIAUTOSCRIPT REST API
        │
        │  API key authentication
        ▼
Maximo Modernization Backend (Express / Node.js)
        │
        ├─ MaximoService     — fetch, analyse, update scripts
        ├─ AIOptimizer       — GPT-4 best-practice optimisation
        ├─ CodeConverter     — Java → automation script (template-based)
        └─ ImpactAnalyzer    — dependency and risk analysis
        │
        │  /api/* REST endpoints
        ▼
React Frontend (Vite)
  Dashboard · Script Analyzer · Script Optimizer · Code Conversion · Batch Conversion · Impact Analysis
        │
        │  (optional) push optimised script back
        ▼
IBM Maximo — updated automation scripts
```

---

## IBM References

- [IBM Maximo Application Suite Documentation](https://www.ibm.com/docs/en/mas)
- [Maximo REST API (OSLC)](https://www.ibm.com/docs/en/mam/7.6.1?topic=suite-using-oslc-rest-api)
- [Maximo Automation Scripts](https://www.ibm.com/docs/en/mam/7.6.1?topic=scripts-automation)
- [IBM Code Engine Documentation](https://cloud.ibm.com/docs/codeengine)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
