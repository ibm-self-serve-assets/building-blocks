# Maximo Modernization Bob Skills

Bob skills for **IBM Maximo Application Suite (MAS)** code modernization — covering AI-powered automation script optimization and Java-to-automation-script conversion.

## Overview

These skills empower IBM Bob to act as an expert Maximo modernization assistant — fetching and optimising existing Maximo automation scripts **or** converting legacy Java classes to automation scripts — all from a single prompt in your IBM Bob workspace.

**Two complementary skills, one modernization goal:**

| Skill | Zip | Use When |
|---|---|---|
| `maximo-code-optimization` | [`maximo-code-optimization.zip`](maximo-code-optimization.zip) | Analyse and AI-optimise existing Maximo automation scripts — security fixes, performance improvements, best-practice enforcement |
| `maximo-java-conversion` | [`maximo_java_conversion.zip`](maximo_java_conversion.zip) | Convert legacy Maximo Java classes to automation scripts (Python, Jython, JavaScript, Nashorn, ECMAScript, MBR) |

---

### `maximo-code-optimization`

A comprehensive skill for analysing and optimising Maximo automation scripts:

- Retrieve automation scripts directly from Maximo environments via REST API (`MXAPIAUTOSCRIPT`)
- Security analysis: SQL injection, input validation gaps, JSON/XML injection, authentication context issues
- Performance optimisation: missing `MboSet.close()`, uncached queries, loop inefficiencies
- AI-powered optimisation using GPT-4 with Maximo-specific best practices
- Detailed before/after reports with severity-ranked issue summaries
- Robust error handling with `MXLoggerFactory` logging patterns
- Deployment guidance and testing recommendations

### `maximo-java-conversion`

A comprehensive skill for converting legacy Maximo Java classes to automation scripts:

- Business logic preservation — retains validation rules, field updates, status transitions, and MboSet patterns
- Multi-language output: Python (Jython), JavaScript, Nashorn, ECMAScript, MBR
- Security best practices enforced: SQL injection prevention, input validation, access control
- Performance optimisation: efficient queries, MboSet lifecycle, batch operations, caching
- MXLoggerFactory error handling patterns applied to all converted scripts
- Test script generation alongside every converted script
- Comprehensive conversion reports with mandatory rule validation

---

## Installation

### Step 1 — Install the skill(s)

Both zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip maximo-code-optimization.zip
unzip maximo_java_conversion.zip
```

This will create:
```
.bob/skills/maximo-code-optimization/
├── SKILL.md
├── knowledge/
├── examples/
└── tools/fetch_maximo_scripts.py

.bob/skills/maximo-java-conversion/
├── SKILL.md
├── knowledge/
├── examples/
└── tools/
    ├── java_to_script_converter.py
    ├── business_logic_analyzer.py
    └── maximo_best_practices.py
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the skill(s) you need. Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What Maximo modernization skills do you have active?"*

---

## Usage Examples

### maximo-code-optimization

```
Use skill maximo-code-optimization and optimize my scripts

Use skill maximo-code-optimization to analyze MX_WO_SCRIPT for security issues

Use skill maximo-code-optimization to review all scripts before production deployment

Use skill maximo-code-optimization to optimize scripts for better performance
```

### maximo-java-conversion

```
Use skill maximo-java-conversion to convert my Java classes to Python

Use skill maximo-java-conversion to convert WorkOrderValidator.java to Jython

Use skill maximo-java-conversion to convert all Java files in java-input/ to JavaScript

Use skill maximo-java-conversion to validate the converted scripts
```

For Java conversion, place your `.java` files in the `java-input/` folder first:
```bash
cp /path/to/YourJavaClass.java java-input/
```

---

## What Bob Can Help You Build

### With `maximo-code-optimization`:
1. **Optimised Scripts**: Fetch → analyse → fix → push back to Maximo, all from a single prompt
2. **Security Reports**: Ranked issue lists (Critical/High/Medium/Low) with before/after code
3. **Performance Fixes**: Corrected MboSet lifecycle, query caching, loop optimisation
4. **Deployment Guides**: Step-by-step deployment instructions per script

### With `maximo-java-conversion`:
1. **Converted Scripts**: Java class → Maximo automation script in your chosen language
2. **Test Scripts**: Auto-generated test script for each converted file
3. **Conversion Reports**: Before/after comparison, mandatory rule validation, next steps
4. **Batch Conversions**: All `.java` files in `java-input/` converted in one operation

---

## Output Structures

### maximo-code-optimization
```
maximo-scripts/
├── original/          # Originals fetched from Maximo REST API
├── optimized/         # Optimised versions with all fixes applied
└── reports/
    └── SUMMARY_REPORT.md   # Issue counts, severity breakdown, deployment steps
```

### maximo-java-conversion
```
output-script/
├── python/            # Python (Jython) converted scripts
├── javascript/        # JavaScript / Nashorn converted scripts
├── ecmascript/
└── mbr/
conversion-reports/
└── <ClassName>_conversion_report.md
```

---

## Skill Capabilities Summary

| Capability | maximo-code-optimization | maximo-java-conversion |
|---|---|---|
| Fetch scripts from Maximo REST API | ✅ | — |
| Security analysis & fixes | ✅ | ✅ |
| Performance optimisation | ✅ | ✅ |
| MboSet lifecycle enforcement | ✅ | ✅ |
| MXLoggerFactory error handling | ✅ | ✅ |
| AI-powered optimisation (GPT-4) | ✅ | — |
| Java → automation script conversion | — | ✅ |
| Business logic preservation check | — | ✅ |
| Test script generation | — | ✅ |
| Before/after comparison report | ✅ | ✅ |
| Push optimised script back to Maximo | ✅ | — |

## Supported Target Languages (maximo-java-conversion)

| Language | Engine | Version |
|---|---|---|
| Python (Jython) | Jython | 2.7.4 |
| JavaScript | Nashorn | 15.6 |
| Nashorn | Nashorn | 15.6 |
| ECMAScript | Nashorn | 15.6 |
| Maximo Business Rules (MBR) | MBR | 1.0 |

## Prerequisites

- IBM Bob installed and configured
- **For `maximo-code-optimization`**: Maximo environment with REST API access + Maximo API key
- **For `maximo-java-conversion`**: Python 3.x (for the command-line converter tool); `.java` source files
- OpenAI API key set in environment (for AI-powered optimisation in `maximo-code-optimization`)

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/maximo-code-optimization/SKILL.md` (or `maximo-java-conversion/SKILL.md`) exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**maximo-code-optimization — Maximo connection fails:**
1. Verify Maximo URL is accessible from your machine
2. Validate the API key in MAS → Security → API Keys
3. Check network/VPN access to the Maximo server

**maximo-java-conversion — No Java files found:**
1. Confirm `.java` files are placed directly in `java-input/`
2. Verify files have the `.java` extension
3. Re-run the skill in interactive mode

**maximo-java-conversion — Business logic differs after conversion:**
1. Compare the original `.java` with the generated script
2. Review the mandatory rule checks in the conversion report
3. Manually validate critical business rules in a Maximo test environment

## Related

- [`../README.md`](../README.md) — Asset Management building block overview and Getting Started guide
- [`../assets/maximo_code_modernization_asset/`](../assets/maximo_code_modernization_asset/) — Full-stack web app for visual script optimization and Java conversion
