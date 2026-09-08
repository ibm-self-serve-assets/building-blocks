# Cryptographic & Quantum-Safe Readiness Skills

Cryptographic & Quantum-Safe Readiness building blocks enable automated cryptographic discovery, quantum vulnerability detection, and CBOM generation with IBM Quantum Safe Explorer and Guardium Cryptographic Manager.

## 📦 Available Assets & Skills

### `skills.zip`

A comprehensive skill and automation package for Quantum Safe Explorer (QSE), providing capabilities for:

- **Cryptographic Vulnerability Scanning**: Scanning Java, Go, Python, Dart, and C++ codebases for quantum-vulnerable cryptographic implementations.
- **Deep Bytecode & API Discovery**: Combining bytecode-level deep analysis with source-level API discovery.
- **Guardium Cryptographic Manager (QCM) Integration**: Uploading findings and CBOM metadata directly to IBM Guardium Cryptographic Manager via MCP tools.
- **Remediation & Migration Workflows**: Identifying legacy algorithms (RSA, ECC) and mapping them to quantum-safe alternatives.

## 🚀 Installation and Setup

### Step 1: Extract the Skill to Bob Workspace
Extract the `skills.zip` archive into your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the package
unzip /path/to/automation/secure/cryptographic-and-quantum-safe-readiness/bob-skills/skills.zip
```

### Step 2: Verify Installation
Check that the skill files are present:

```bash
ls -la .bob/skills/
```

### Step 3: Activate in Bob
1. Open Bob and select your preferred mode.
2. Ensure the **Skills** option is enabled.
3. The Cryptographic & Quantum-Safe Readiness capabilities will be active and ready to assist.
