# Maximo Modernization Bob Skills

Maximo Modernization building blocks enable AI-powered automation script optimization and legacy Java-to-automation script conversion for IBM Maximo Application Suite (MAS).

## 📦 Available Assets & Skills

### `maximo-code-optimization.zip`

A comprehensive skill for analyzing and optimizing Maximo automation scripts:
- Fetch and analyze scripts directly via Maximo REST APIs (`MXAPIAUTOSCRIPT`).
- Automated security analysis (SQL injection prevention, input validation) and performance improvements (MboSet lifecycle, caching).
- Detailed severity-ranked before/after reports and logging best practices with `MXLoggerFactory`.

### `maximo_java_conversion.zip`

A comprehensive skill for converting legacy Maximo Java classes to automation scripts:
- Business logic preservation across Python/Jython, JavaScript, Nashorn, and ECMAScript.
- Automated generation of test scripts alongside converted automation scripts.
- Batch conversion capabilities with comprehensive validation reports.

## 🚀 Installation and Setup

### Step 1: Extract the Skills to Bob Workspace
Extract the desired ZIP archive into your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the package(s)
unzip /path/to/automation/operate/asset-management/bob-skills/maximo-code-optimization.zip
unzip /path/to/automation/operate/asset-management/bob-skills/maximo_java_conversion.zip
```

### Step 2: Verify Installation
Check that the skill files are present:

```bash
ls -la .bob/skills/
```

### Step 3: Activate in Bob
1. Open Bob and select your preferred mode.
2. Ensure the **Skills** option is enabled.
3. The Maximo modernization capabilities will be active and ready to assist.
