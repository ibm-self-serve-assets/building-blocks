# 🔍 Application Observability with IBM Instana

---

## 📑 Table of Contents

- [Overview](#overview)
- [What's Included](#whats-included)
- [Key Components](#key-components)
- [Getting Started](#getting-started)
- [Use Cases](#use-cases)
- [Architecture](#architecture)
- [Best Practices](#best-practices)
- [Related Resources](#related-resources)

---

## 🔗 Navigation

**Observe Building Blocks:**
- [← Back to Observe](../README.md)
- [Network Performance →](../network-performance/README.md)

**Assets:**
- [Observability Dashboard →](assets/application-observability/README.md)
- [Instana MCP Server →](assets/instana-mcp/)
- [Bob Modes →](bob-modes/README.md)

**Other Categories:**
- [Build & Deploy](../../build-and-deploy/authentication-mgmt/README.md)
- [Optimize](../../optimize/finops/README.md)

---

## Overview

This building block provides a complete application observability solution using **IBM Instana**. It includes a production-ready Python Dash dashboard for monitoring application health, an MCP server for AI-powered observability automation, and custom Bob modes for enhanced development workflows.

### What You Get

✅ **Real-time Monitoring Dashboard** - Python Dash application with interactive visualizations  
✅ **IBM Instana Integration** - Full REST API client with comprehensive metrics  
✅ **MCP Server** - Model Context Protocol server for AI-powered observability  
✅ **Custom Bob Modes** - Specialized modes for observability tasks  
✅ **Production Ready** - Complete with setup scripts, logging, and error handling

---

## What's Included

### 1. Instana Observability Dashboard

A comprehensive Python Dash application for monitoring applications through IBM Instana.

**Location:** [`assets/application-observability/`](assets/application-observability/README.md)

**Features:**
- 📊 Real-time service health monitoring
- 📈 Interactive visualizations (Plotly charts)
- 🎯 Composite health scoring algorithm
- 📋 Detailed service metrics tables
- 🔄 Auto-refresh capabilities
- 🎨 Modern, responsive UI with Bootstrap

**Tech Stack:**
- Python 3.8+ with Dash framework
- Dash Bootstrap Components
- Plotly for visualizations
- pandas for data processing
- IBM Instana REST API integration

**Quick Start:**
```bash
cd assets/application-observability
./scripts/setup.sh  # Unix/macOS/Linux
# or
scripts\setup.bat   # Windows
```

[📖 Full Documentation](assets/application-observability/README.md) | [⚡ Quick Start](assets/application-observability/QUICKSTART.md) | [📊 Project Summary](assets/application-observability/PROJECT_SUMMARY.md)

---

### 2. Instana MCP Server

Model Context Protocol server for integrating Instana observability with AI assistants like IBM Bob.

**Location:** [`assets/instana-mcp/`](assets/instana-mcp/)

**Capabilities:**
- 🤖 AI-powered incident analysis
- 📡 Real-time event streaming
- 🔍 Automated root cause analysis
- 📊 Kubernetes event monitoring
- ⚠️ Agent monitoring and alerts

**Deployment Options:**
- **Code Engine:** [`deploy-ce/`](assets/instana-mcp/deploy-ce/) - IBM Cloud Code Engine deployment
- **Container:** [`mcp-server/`](assets/instana-mcp/mcp-server/) - Docker containerized server

**MCP Tools Available:**
- `get_event` - Retrieve specific events by ID
- `get_kubernetes_info_events` - K8s events with detailed analysis
- `get_agent_monitoring_events` - Agent monitoring insights
- `get_issues` - Issue event tracking
- `get_incidents` - Critical incident management
- `get_changes` - Change event monitoring
- `get_events_by_ids` - Batch event retrieval

---

### 3. Custom Bob Modes

Specialized IBM Bob modes for application observability workflows.

**Location:** [`bob-modes/`](bob-modes/README.md)

**Includes:**
- **Application Observability Mode** ([`application-observability.yaml`](bob-modes/base-modes/application-observability.yaml))
  - Domain-specific observability expertise
  - Instana integration patterns
  - Dashboard generation guidance
  - Performance analysis workflows
  - Service dependency mapping

**Installation:**
```bash
# Copy to Bob's global modes directory
cp bob-modes/base-modes/application-observability.yaml \
   ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

[📖 Bob Modes Documentation](bob-modes/README.md)

---

## Key Components

### Dashboard Application

**Service Health Monitoring:**
- Real-time service call counts
- Error rate tracking with trends
- Latency monitoring (response times)
- Composite health scores (0-100)

**Interactive Visualizations:**
- Summary cards with key metrics
- Service health bar charts
- Error rate analysis charts
- Latency distribution graphs
- Detailed service metrics tables

**Health Score Algorithm:**
- 40% Error rate (lower is better)
- 30% Latency (lower is better)
- 30% Call volume (higher indicates activity)

### MCP Server Integration

**Event Analysis:**
- Kubernetes info events with detailed insights
- Agent monitoring events with frequency analysis
- Issue and incident tracking
- Change event monitoring
- Automated problem detection

**AI-Powered Features:**
- Natural language time ranges ("last 24 hours")
- Automated event summarization
- Top problems identification
- Actionable fix suggestions

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- IBM Instana instance with API access
- IBM Instana API token with read permissions
- Network connectivity to Instana API endpoints

### Quick Setup

1. **Clone or navigate to the project:**
   ```bash
   cd observe/application-observability
   ```

2. **Choose your component:**

   **For Dashboard:**
   ```bash
   cd assets/application-observability
   ./scripts/setup.sh
   # Edit .env with your Instana credentials
   ./scripts/run.sh
   # Access at http://localhost:8050
   ```

   **For MCP Server:**
   ```bash
   cd assets/instana-mcp/mcp-server
   # Configure environment variables
   docker build -t instana-mcp .
   docker run -p 8080:8080 instana-mcp
   ```

   **For Bob Modes:**
   ```bash
   cd bob-modes
   # Follow installation instructions in README.md
   ```

---

## Use Cases

### 1. Real-Time Application Monitoring

Monitor your applications deployed on OpenShift or Kubernetes:
- Track service health across microservices
- Identify performance bottlenecks
- Monitor error rates and latency
- Visualize service dependencies

**Example:** Monitor the [Retail Application](../../build-and-deploy/Iaas/assets/retailapp/README.md) deployed via [Ansible](../../build-and-deploy/Iaas/assets/deploy-bob-anisble/README.md)

### 2. AI-Powered Incident Response

Use the MCP server with IBM Bob for intelligent incident management:
- Ask Bob: "What incidents occurred in the last 24 hours?"
- Get automated root cause analysis
- Receive actionable remediation suggestions
- Track incident resolution progress

### 3. Development Workflow Enhancement

Use custom Bob modes for observability-focused development:
- Generate monitoring dashboards
- Implement observability patterns
- Design service instrumentation
- Create alerting strategies

### 4. Performance Optimization

Identify and resolve performance issues:
- Analyze latency trends
- Detect anomalies in service behavior
- Optimize resource utilization
- Improve user experience

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User / Developer                      │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Browser    │  │   IBM Bob    │  │   CLI Tools  │ │
│  │  Dashboard   │  │  (with MCP)  │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│              Application Observability Layer             │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Dash Dashboard  │         │   MCP Server     │     │
│  │  - Visualizations│         │  - AI Analysis   │     │
│  │  - Metrics       │◄────────┤  - Event Stream  │     │
│  │  - Health Scores │         │  - Automation    │     │
│  └────────┬─────────┘         └────────┬─────────┘     │
└───────────┼──────────────────────────────┼──────────────┘
            │                              │
            └──────────────┬───────────────┘
                           ▼
                  ┌─────────────────┐
                  │  IBM Instana    │
                  │  REST API       │
                  │  - Applications │
                  │  - Services     │
                  │  - Metrics      │
                  │  - Events       │
                  │  - Traces       │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Monitored Apps │
                  │  - Microservices│
                  │  - Containers   │
                  │  - Infrastructure│
                  └─────────────────┘
```

### Component Interaction

1. **Dashboard** queries Instana API for metrics and displays visualizations
2. **MCP Server** provides AI-powered analysis and automation capabilities
3. **Bob Modes** enhance development workflows with observability expertise
4. **Instana** collects telemetry from monitored applications

---

## Best Practices

### 1. Dashboard Configuration

- **Target Specific Applications:** Configure `INSTANA_APPLICATION_NAME` for focused monitoring
- **Adjust Refresh Intervals:** Balance real-time updates with API rate limits
- **Customize Health Thresholds:** Tune health score weights for your use case
- **Use Environment Variables:** Never hardcode credentials

### 2. MCP Server Usage

- **Natural Language Queries:** Use time ranges like "last 24 hours" or "last week"
- **Batch Operations:** Retrieve multiple events efficiently with `get_events_by_ids`
- **Event Filtering:** Use specific event types (incidents, issues, changes) for targeted analysis
- **Rate Limiting:** Implement appropriate delays between API calls

### 3. Monitoring Strategy

- **Baseline Metrics:** Establish normal behavior patterns before alerting
- **Composite Scoring:** Use health scores for quick assessment, drill down for details
- **Trend Analysis:** Monitor changes over time, not just current state
- **Service Dependencies:** Understand relationships between services

### 4. Integration with CI/CD

- **Pre-deployment Checks:** Verify service health before deployments
- **Post-deployment Monitoring:** Track metrics after releases
- **Automated Rollbacks:** Use health scores to trigger rollback decisions
- **Performance Regression:** Compare metrics across deployments

---

## 📚 Related Resources

### Observability Assets
- [Instana Observability Dashboard](assets/application-observability/README.md) - Python Dash application
  - [Quick Start Guide](assets/application-observability/QUICKSTART.md)
  - [Project Summary](assets/application-observability/PROJECT_SUMMARY.md)
- [Instana MCP Server](assets/instana-mcp/) - MCP integration
- [Bob Modes](bob-modes/README.md) - Custom Bob modes for observability

### Applications to Monitor
- [Retail Application](../../build-and-deploy/Iaas/assets/retailapp/README.md) - Sample app to monitor
  - [Deployment Guide](../../build-and-deploy/Iaas/assets/retailapp/deploy-steps.md)
  - [JMeter Load Testing](../../build-and-deploy/Iaas/assets/retailapp/jmeter/README.md)
- [Ansible Deployment](../../build-and-deploy/Iaas/assets/deploy-bob-anisble/README.md) - Automated deployment

### Build & Deploy Building Blocks
- [Authentication Management](../../build-and-deploy/authentication-mgmt/README.md) - IBM Security Verify
- [Code Assistant](../../build-and-deploy/code-assistant/README.md) - AI-powered development
- [IaaS](../../build-and-deploy/Iaas/README.md) - Infrastructure as a Service
- [iPaaS](../../build-and-deploy/ipaas/README.md) - Integration platform

### Optimize Building Blocks
- [Automated Resilience](../../optimize/automated-resilience-and-compliance/assets/automate-resilience/README.md) - IBM Concert insights
- [FinOps](../../optimize/finops/README.md) - Cost optimization with IBM Turbonomic
- [Network Performance](../network-performance/README.md) - Network monitoring with IBM SevOne

---

## Support & Contribution

### Getting Help

- **Dashboard Issues:** Check [README](assets/application-observability/README.md) and logs in `assets/application-observability/logs/`
- **MCP Server Issues:** Review MCP server logs and configuration
- **Bob Modes:** See [Bob Modes documentation](bob-modes/README.md)
- **Instana API:** Consult IBM Instana documentation

### Contributing

Contributions are welcome! Areas for enhancement:
- Additional visualizations in the dashboard
- New MCP tools for Instana integration
- Enhanced Bob modes with more patterns
- Integration examples with other IBM products

---

**[⬆ Back to Top](#-application-observability-with-ibm-instana)**
