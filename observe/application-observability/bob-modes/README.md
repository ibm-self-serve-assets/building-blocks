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

### Application Observability Mode

**File:** `application-observability.yaml`.
**Location:** `Bob Modes/Base Modes/application-observability.yaml`

This mode enhances IBM Bob with observability-specific capabilities,
including:

-   Full-stack application monitoring guidance.
-   Integration with IBM Instana.
-   Dashboard generation patterns.
-   Performance analysis workflows.
-   Service dependency mapping.

Use this mode when working on observability dashboards, monitoring
strategy, or resilience engineering initiatives.

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

------------------------------------------------------------------------

### Method 1: Copy to Bob's Global Modes Directory (Recommended)

#### Windows

``` powershell
Copy-Item application-observability.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

#### Linux / macOS

``` bash
cp application-observability.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

------------------------------------------------------------------------

### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference
this directory directly.

1.  Open IBM Bob configuration settings\
2.  Add the local directory path under custom modes\
3.  Restart IBM Bob

This approach is useful for development and version-controlled mode
updates.

