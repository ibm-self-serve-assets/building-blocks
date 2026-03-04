# Bob Modes

This directory contains custom IBM Bob mode configurations designed to
extend IBM Bob's capabilities with domain-specific intelligence and
workflow orchestration.

Bob modes define structured prompts, behavioral constraints, and domain
context that enable IBM Bob to operate with specialized expertise across
observability, security, DevSecOps, infrastructure automation, and
secret management domains.

------------------------------------------------------------------------

## Overview

Custom Bob modes allow you to:

-   Inject domain-specific knowledge into Bob interactions.
-   Standardize workflows across teams.
-   Automate repetitive engineering tasks,
-   Integrate Bob with external systems (e.g., Vault, Ansible, Instana).
-   Enable consistent architectural and operational guidance.

These modes are particularly useful in enterprise environments where
governance, repeatability, and domain accuracy are critical.

------------------------------------------------------------------------

## Available Modes

### Application Resilience Mode

**File:** [`application-resilience.yaml`](base-modes/application-resilience.yaml:1)
**Location:** `bob-modes/base-modes/application-resilience.yaml`

This mode enhances IBM Bob with application resilience and compliance capabilities, including:

- Python Dash application development for IBM Concert APIs
- Vulnerability management and CVE tracking
- Application monitoring and certificate lifecycle management
- Interactive data visualizations with Plotly
- Multi-tab interfaces with dynamic data loading
- Production-ready error handling and logging

Use this mode when building dashboards for vulnerability management, compliance tracking, or application resilience monitoring.

------------------------------------------------------------------------

## Mode Structure

Each mode YAML file typically includes:

-   Mode metadata (name, description, version)/
-   Behavioral instructions.
-   Domain context.
-   Response formatting rules.
-   Integration hooks.
-   Constraints and guardrails.

Custom modes can be extended or modified to include:

-   DevSecOps workflows.
-   Vault deployment automation.
-   Secret scanning and remediation logic.
-   Infrastructure-as-Code orchestration.
-   Architecture generation patterns.

------------------------------------------------------------------------

## Installing Bob Modes

You can install custom modes using one of the following methods.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

------------------------------------------------------------------------

### Method 1: Copy to Bob's Global Modes Directory (Recommended)

#### Windows

``` powershell
Copy-Item base-modes/application-resilience.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

#### Linux / macOS

``` bash
cp base-modes/application-resilience.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

------------------------------------------------------------------------

### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference
this directory directly.

1.  Open IBM Bob configuration settings
2.  Add the local directory path under custom modes
3.  Restart IBM Bob

This approach is useful for development and version-controlled mode
updates.

------------------------------------------------------------------------

## Verifying Installation

After installation, verify the mode is available:

1. Restart IBM Bob (VS Code)
2. Open IBM Bob chat interface
3. Look for "🛡️ Automate Resilience" in the mode selector
4. Select the mode to start using application resilience capabilities

------------------------------------------------------------------------



