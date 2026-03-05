# Bob Mode for Data Security & Encryption

Custom IBM Bob mode configuration for data security, encryption, and governance in IBM watsonx.data Intelligence.

---

## Overview

This Bob mode provides specialized assistance for:

- **Data Masking**: Implementing PII protection and data redaction strategies
- **Access Control**: Configuring RBAC and role-based data access
- **Governance Policies**: Setting up compliance policies (GDPR, CCPA, HIPAA)
- **Encryption**: Planning and implementing encryption strategies
- **Security Automation**: Automating security deployments and configurations
- **Audit Logging**: Configuring comprehensive audit trails

---

## What's Included

- **[`base-mode/data-security.yaml`](base-mode/data-security.yaml)**: Bob mode configuration for data security development

---

## Mode Capabilities

- Data classification and tagging
- Masking strategy design and implementation
- RBAC policy configuration
- Compliance mapping and enforcement
- Security automation workflows
- Audit logging setup
- Encryption strategy planning
- Incident response guidance
- Secure AI/GenAI pipeline configuration

---

## When to Use This Mode

- Implementing PII protection mechanisms
- Configuring role-based data access controls
- Setting up compliance and governance policies
- Securing AI/GenAI data pipelines
- Troubleshooting security configuration issues
- Automating security deployments
- Planning encryption strategies

---

## Installing Bob Modes

This section provides step-by-step instructions for installing the custom Bob mode.

---

### Installing the Custom Bob Mode

The custom Bob mode ([`base-mode/data-security.yaml`](base-mode/data-security.yaml)) defines the behavior, expertise, and capabilities of IBM Bob when working with data security and encryption tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-mode/data-security.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-mode/data-security.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.