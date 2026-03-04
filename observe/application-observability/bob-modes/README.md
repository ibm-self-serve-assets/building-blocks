# 🤖 Bob Modes for Application Observability

---

## 🔗 Navigation

**Parent:**
- [← Back to Application Observability](../README.md)

**Assets:**
- [Observability Dashboard](../assets/application-observability/README.md)
- [Instana MCP Server](../assets/instana-mcp/)

**Other Building Blocks:**
- [Build & Deploy](../../../build-and-deploy/authentication-mgmt/README.md)
- [Optimize](../../../optimize/finops/README.md)

---

## Overview

This directory contains custom IBM Bob mode configurations designed to extend IBM Bob's capabilities with domain-specific intelligence and workflow orchestration.

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

-   Mode metadata (name, description, version).
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

## Installing Bob Modes and MCP Server

This section provides step-by-step instructions for installing both the custom Bob mode and the MCP server configuration.

------------------------------------------------------------------------

## Part 1: Installing the Custom Bob Mode

The custom Bob mode ([`application-observability.yaml`](base-modes/application-observability.yaml:1)) defines the behavior, expertise, and capabilities of IBM Bob when working with application observability tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

### Method 1: Copy to Bob's Global Modes Directory (Recommended)

#### Windows

``` powershell
Copy-Item base-modes/application-observability.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

#### Linux / macOS

``` bash
cp base-modes/application-observability.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
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

## Part 2: Installing the MCP Server Configuration

The MCP server configuration ([`application-observability.json`](base-modes/application-observability.json:1)) enables IBM Bob to connect to the Application Observability MCP server and access observability tools and data.

### Step 1: Locate Your MCP Settings File

IBM Bob stores MCP server configurations in a JSON file. The location varies by operating system:

#### Windows
```
%APPDATA%\Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json
```

#### Linux
```
~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
```

#### macOS
```
~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
```

### Step 2: Add the MCP Server Configuration

1. Open the `cline_mcp_settings.json` file in a text editor
2. If the file is empty or doesn't exist, create it with the following structure:

```json
{
  "mcpServers": {
    "Application Observability": {
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--transport",
        "streamablehttp",
        "https://mcp-instana.268gjj8oawf7.us-south.codeengine.appdomain.cloud/mcp"
      ],
      "description": "Base MCP Server for Application Observability Building Block",
      "disabled": false,
      "alwaysAllow": [
        "manage_instana_resources",
        "manage_custom_dashboards",
        "analyze_infrastructure_elicitation",
        "get_actions",
        "get_action_details",
        "get_action_types",
        "get_action_tags",
        "get_action_matches",
        "submit_automation_action",
        "get_action_instance_details",
        "list_action_instances",
        "delete_action_instance",
        "get_event",
        "get_kubernetes_info_events",
        "get_agent_monitoring_events",
        "get_issues",
        "get_incidents",
        "get_changes",
        "get_events_by_ids",
        "get_website_page_load",
        "get_website_catalog_metrics",
        "get_website_beacon_metrics_v2",
        "get_website_catalog_tags",
        "get_website_tag_catalog",
        "get_website_beacon_groups",
        "get_website_beacons",
        "get_websites",
        "create_website",
        "delete_website",
        "rename_website",
        "get_website_geo_location_configuration",
        "update_website_geo_location_configuration",
        "get_website_ip_masking_configuration",
        "update_website_ip_masking_configuration",
        "get_website_geo_mapping_rules",
        "set_website_geo_mapping_rules",
        "upload_source_map_file",
        "clear_source_map_upload_configuration"
      ]
    }
  }
}
```

3. If the file already contains other MCP servers, merge the "Application Observability" entry into the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      ...
    },
    "Application Observability": {
      "command": "uvx",
      ...
    }
  }
}
```

4. Save the file

### Step 3: Verify Installation

1. Restart IBM Bob (VS Code)
2. Open IBM Bob chat interface
3. Switch to the "🔍 Application Observability" mode from the mode selector
4. The MCP server should automatically connect
5. You can verify the connection by asking Bob to use one of the MCP tools (e.g., "Get incidents from the last 24 hours")

---

## 📚 Related Resources

### Observability Assets
- [Application Observability Overview](../README.md)
- [Instana Dashboard](../assets/application-observability/README.md)
  - [Quick Start](../assets/application-observability/QUICKSTART.md)
  - [Project Summary](../assets/application-observability/PROJECT_SUMMARY.md)

### Applications to Monitor
- [Retail Application](../../../build-and-deploy/Iaas/assets/retailapp/README.md)
- [Ansible Deployment](../../../build-and-deploy/Iaas/assets/deploy-bob-anisble/README.md)

### Related Building Blocks
- [Automated Resilience](../../../optimize/automated-resilience-and-compliance/assets/automate-resilience/README.md)
- [Network Performance](../../network-performance/README.md)
- [FinOps](../../../optimize/finops/README.md)

---

**[⬆ Back to Top](#-bob-modes-for-application-observability)**