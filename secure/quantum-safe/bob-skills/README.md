# Quantum Safe Explorer Skills

This directory contains Bob skills for Quantum Safe cryptography analysis using IBM Quantum Safe Explorer (QSE).

## 🎯 Overview

The `skills.zip` skill empowers Bob to help you scan codebases for quantum-vulnerable cryptographic APIs and implement quantum-safe cryptography compliance. This skill provides comprehensive capabilities for running IBM Quantum Safe Explorer (QSE) scans, interpreting cryptographic findings, and uploading results to IBM Guardium Cryptographic Manager (QCM).

## 📦 Available Skill

### qse (Quantum Safe Explorer)

A comprehensive skill for working with IBM Quantum Safe Explorer, providing capabilities for:

#### 1. 🔍 **Cryptographic Vulnerability Scanning**
Analyze codebases for quantum-vulnerable cryptographic implementations:
- Scan Java, Go, Python, Dart, and C++ projects
- Identify quantum-vulnerable cryptographic APIs and algorithms
- Detect non-compliant cryptographic usage patterns
- Support for both source-code and bytecode-level analysis

#### 2. 🧬 **Cryptographic Analytics (Java)**
Perform deep bytecode-level cryptographic analysis for Java projects:
- Bytecode-level deep analysis using the `-da` flag
- Class file scanning via the `-cf` parameter
- Comprehensive cryptographic algorithm detection
- Full quantum readiness assessment combining Analytics + API Discovery

#### 3. 🌐 **API Discovery**
Discover and analyze cryptographic API usage across all supported languages:
- Source-code level API usage analysis
- Identifies cryptographic libraries and function calls
- Supports `.java`, `.go`, `.dart`, `.py`, and `.cpp` projects
- No compiled artifacts required

#### 4. 🔬 **Language Detection & Scan Orchestration**
Automatically detect project language and run the appropriate scans:
- File extension counting with language-specific marker detection
- Intelligent scan type selection (Cryptographic Analytics + API Discovery for Java, API Discovery only for others)
- Handles ambiguous or multi-language projects gracefully

#### 5. 📤 **QCM Integration**
Upload QSE findings to IBM Guardium Cryptographic Manager for centralized tracking:
- Retrieves QCM import profile IDs via `gcm_api` MCP tool
- Uploads findings JSON to QCM with repository URL stamping
- Validates upload success and confirms completion
- Full end-to-end scan-to-upload workflow

#### 6. 🔒 **Security & Compliance**
Implement quantum-safe cryptography compliance workflows:
- Identify quantum-vulnerable algorithms (RSA, ECC, AES key sizes, etc.)
- Map findings to quantum-safe migration paths
- Centralized findings management via IBM Guardium Cryptographic Manager
- Repository URL tagging for traceability

## 🚀 Installation and Setup

### Step 1: Download the Skill
Download the `skills.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/skills.zip
```

After extraction, you should see a `qse` folder inside a `skills/` directory in your `.bob/skills` directory.

### Step 3: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/qse
```

You should see the skill files: `SKILL.md`, `1_workflow.md`, `2_best_practices.md`, `3_command_construction.md`, `4_language_detection.md`, `5_examples.md`, and `6_qcm_integration.md`.

### Step 4: Configure QCM Integration (Optional)
If you plan to upload findings to IBM Guardium Cryptographic Manager, configure the `gcm-mcp-server` MCP server in your Bob workspace with the required credentials:

```json
{
  "mcpServers": {
    "gcm-mcp-server": {
      "env": {
        "GCM_USERNAME": "<your-gcm-username>",
        "GCM_PASSWORD": "<your-gcm-password>"
      }
    }
  }
}
```

### Step 5: Activate the Skill
To use the skill:
1. Open Bob and select any mode you want to work in
2. Enable the **Skills** button in that mode
3. The `qse` skill will be available for use within that mode

## 💡 Usage Examples

Once activated, you can ask Bob to help with tasks like:

### Quantum Readiness Scans
- *"Scan my Java project at /path/to/project for quantum safety"*
- *"Run a complete quantum readiness assessment on this codebase"*
- *"Check my Go application for quantum-vulnerable cryptographic APIs"*

### Language-Specific Scans
- *"Run a Cryptographic Analytics scan on my Java project"*
- *"Perform an API Discovery scan on this Python application"*
- *"Scan the Dart project in /path/to/flutter-app for crypto vulnerabilities"*

### QCM Upload
- *"Upload the QSE findings to IBM Guardium Cryptographic Manager"*
- *"After the scan, upload results to QCM using profile ID xyz"*

### Full Workflow
- *"Scan my project and upload findings to QCM"*
- *"Run a full quantum-safe assessment and send results to Guardium"*

## 🎓 What Bob Can Help You Build

With this skill, Bob can assist you in:

1. **Quantum Readiness Assessments**: Full end-to-end cryptographic vulnerability scans for Java, Go, Python, Dart, and C++ projects
2. **Cryptographic Analytics Reports**: Deep bytecode-level analysis of Java projects for comprehensive findings
3. **API Discovery Reports**: Source-code level cryptographic API usage reports for all supported languages
4. **QCM Integration Workflows**: Automated scan-to-upload workflows for centralized findings management in IBM Guardium
5. **Migration Planning**: Identify quantum-vulnerable algorithms and map them to quantum-safe alternatives
6. **CI/CD Integration Guidance**: Advice on integrating QSE scans into your DevSecOps pipelines

## 📋 Prerequisites

To work with this skill effectively, you should have:

- IBM Quantum Safe Explorer (QSE) CLI installed at `/usr/local/bin/qse-cli-artifacts`
- A supported project codebase: Java, Go, Python, Dart, or C++
- For Java projects: compiled class files in `target/classes`, `build/classes/java/main`, `out/production`, or `bin`
- For QCM upload: access to IBM Guardium Cryptographic Manager with valid credentials
- The `gcm-mcp-server` MCP tool configured (QCM upload only)

## 🔧 Key Technologies

This skill helps you work with:

- **IBM Quantum Safe Explorer (QSE) CLI**: Cryptographic vulnerability scanning engine
- **IBM Guardium Cryptographic Manager (QCM)**: Centralized cryptographic findings management
- **Java / Go / Python / Dart / C++**: Supported project languages for scanning
- **gcm_api MCP Tool**: API integration with IBM Guardium / QCM
- **QSE Findings JSON**: Structured scan output format for reporting and uploads

## 🐛 Troubleshooting

### Skill doesn't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Ensure the `skills/qse/SKILL.md` file exists after extraction
3. Check file permissions on the extracted files
4. Restart Bob to refresh the skills list
5. Ensure you've enabled the Skills button in your current mode

### QSE scan fails to execute
1. Verify QSE CLI is installed at `/usr/local/bin/qse-cli-artifacts`
2. Confirm the input path exists and is accessible
3. Ensure you have read permissions on the project directory
4. For Java projects, verify class files exist in a standard output directory

### Skill is active but Bob doesn't detect the correct language
1. Be explicit in your request (e.g., "scan this Java project")
2. Ensure the project has language-specific markers (`pom.xml` for Java, `go.mod` for Go, etc.)
3. If the project has mixed languages, specify the primary language directly

### QCM upload fails
1. Verify `gcm-mcp-server` is configured with valid `GCM_USERNAME` and `GCM_PASSWORD`
2. Confirm the QSE findings JSON file was generated (check `./qse_explorer_result/`)
3. Ensure a QSE import profile exists in QCM before uploading
4. Check network connectivity to the IBM Guardium Cryptographic Manager instance

## 📚 Related Resources

- [IBM Quantum Safe Explorer Documentation](https://www.ibm.com/docs/en/guardium-crypto-manager)
- [IBM Guardium Cryptographic Manager](https://www.ibm.com/products/guardium-data-security-center)
- [Parent Directory README](../README.md) - Complete quantum-safe cryptography implementation guide
- [Bob Modes Directory](../bob-modes/) - Quantum Safe Explorer custom Bob mode

## 🎯 Skill Capabilities Summary

| Capability | Description |
|------------|-------------|
| **Language Detection** | Automatically detect Java, Go, Python, Dart, or C++ from file extensions and project markers |
| **Cryptographic Analytics** | Deep bytecode-level cryptographic analysis for Java projects |
| **API Discovery** | Source-code level cryptographic API usage scan for all supported languages |
| **Java Full Assessment** | Run both Cryptographic Analytics and API Discovery for complete Java coverage |
| **Command Construction** | Build correct QSE CLI commands with all required parameters and flags |
| **Findings Location** | Locate and identify the most recent QSE findings JSON after a scan |
| **Repository URL Stamping** | Update findings JSON with the project's GitHub repository URL |
| **QCM Profile Lookup** | Retrieve QSE import profile IDs from IBM Guardium Cryptographic Manager |
| **QCM Upload** | Upload findings JSON to QCM for centralized cryptographic management |
| **Error Handling** | Handle scan failures, missing files, and QCM connectivity issues gracefully |

## 💬 Support

For issues or questions about this skill:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for quantum-safe cryptography context
3. Ask Bob directly — the skill includes comprehensive workflow and best practices knowledge
4. Refer to IBM Quantum Safe Explorer documentation for CLI-specific questions

## 📝 Version Information

- **Skill Version**: 1.0.0
- **Compatible with**: IBM Quantum Safe Explorer (QSE) CLI, IBM Guardium Cryptographic Manager
- **Supported Languages**: Java, Go, Python, Dart, C++
- **Last Updated**: 2026-07-07
- **Status**: Production Ready ✅

---

**Note**: This skill requires IBM Quantum Safe Explorer CLI installed at `/usr/local/bin/qse-cli-artifacts`. For QCM upload functionality, the `gcm-mcp-server` MCP tool must be configured with valid IBM Guardium credentials.

Made with ❤️ for IBM Quantum Safe cryptography
