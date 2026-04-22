# 🛡️ Automated Resilience and Compliance with IBM Concert

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

**Optimize Building Blocks:**
- [← Back to Optimize](../README.md)
- [FinOps →](../finops/README.md)

**Assets:**
- [Concert Insights Dashboard →](assets/automate-resilience/README.md)
- [Bob Modes →](bob-modes/README.md)

**Other Categories:**
- [Build & Deploy](../../build-and-deploy/authentication-mgmt/README.md)
- [Observe](../../observe/application-observability/README.md)

---

## Overview

This building block provides a complete **automated resilience and compliance solution** using **IBM Concert**. It includes a production-ready Python Dash dashboard for comprehensive vulnerability management, application monitoring, and certificate lifecycle tracking, along with custom Bob modes for enhanced development workflows.

### What You Get

✅ **Comprehensive Dashboard** - Python Dash application with multi-tab interface  
✅ **IBM Concert Integration** - Full REST API client with pagination support  
✅ **Vulnerability Management** - CVE tracking with severity-based analytics  
✅ **Application Monitoring** - Multi-level drill-down from portfolio to artifacts  
✅ **Certificate Lifecycle** - Expiry tracking and algorithm analysis  
✅ **Custom Bob Modes** - Specialized modes for resilience automation  
✅ **Production Ready** - Complete with setup scripts, logging, and error handling

---

## What's Included

### 1. IBM Concert Insights Dashboard

A comprehensive Python Dash application for visualizing and managing IBM Concert data across three key areas: CVEs, Applications, and Certificates.

**Location:** [`assets/automate-resilience/`](assets/automate-resilience/README.md)

**Features:**

#### 🔒 CVE Insights
- **Comprehensive Analytics:** View all vulnerabilities with severity categorization
- **Interactive Visualizations:**
  - Severity distribution pie chart
  - Risk score histogram (20 bins)
  - Top 10 highest risk CVEs
  - Priority distribution analysis
- **Detailed Table:** Sortable, filterable with severity-based color coding
- **Statistics:** Total CVEs, critical count, high severity, average risk score

#### 📱 Application Insights
- **Portfolio Overview:**
  - Total applications and vulnerabilities
  - Application status distribution
  - Vulnerability distribution analysis
  - Build artifact correlation
  - Top 10 applications by vulnerability count
- **Multi-Level Drill-Down:**
  1. Select application → View application-specific CVE analytics
  2. View build artifacts → Select artifact for detailed CVE analysis
  3. Compare vulnerabilities across different builds
- **Application CVE Analytics:**
  - Severity distribution charts
  - Risk score histograms
  - Top 10 highest risk CVEs per application
  - Priority-based filtering

#### 🔐 Certificate Insights
- **Lifecycle Management:**
  - Valid, expired, and expiring certificates tracking
  - Expiry timeline visualization
  - Algorithm and key size distribution
- **Expiry Alerts:**
  - 🔴 Critical: ≤7 days until expiry
  - 🟡 Warning: 8-30 days until expiry
  - 🔵 Info: 31-90 days until expiry
- **Certificate Analytics:**
  - Status distribution
  - Top 10 certificates expiring soon
  - Algorithm usage patterns
  - Key size analysis

**Tech Stack:**
- Python 3.8+ with Dash framework (2.14.2)
- Dash Bootstrap Components (1.5.0)
- Plotly (5.18.0) for interactive visualizations
- pandas (2.1.4) for data processing
- IBM Concert REST API integration

**Quick Start:**
```bash
cd assets/automate-resilience
./setup_and_run.sh  # Unix/macOS/Linux
# or
setup_and_run.bat   # Windows
```

[📖 Full Documentation](assets/automate-resilience/README.md) | [⚡ Quick Start](assets/automate-resilience/QUICKSTART.md) | [📊 Project Summary](assets/automate-resilience/PROJECT_SUMMARY.md)

---

### 2. Custom Bob Modes

Specialized IBM Bob modes for automated resilience and compliance workflows.

**Location:** [`bob-modes/`](bob-modes/README.md)

**Includes:**
- **Application Resilience Mode** ([`application-resilience.yaml`](bob-modes/base-modes/application-resilience.yaml))
  - Domain-specific resilience expertise
  - IBM Concert integration patterns
  - Vulnerability management workflows
  - Compliance automation guidance
  - Certificate lifecycle management

**Installation:**
```bash
# Copy to Bob's global modes directory
cp bob-modes/base-modes/application-resilience.yaml \
   ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

[📖 Bob Modes Documentation](bob-modes/README.md)

---

## Key Components

### Dashboard Application Structure

```
assets/automate-resilience/
├── app.py                      # Main Dash application (139 lines)
├── config.py                   # Configuration & logging (87 lines)
├── requirements.txt            # Python dependencies
├── .env.example               # Configuration template
├── setup_and_run.sh/bat       # Automated setup scripts
├── test_api_connection.py     # API connectivity test
│
├── api/                        # IBM Concert API Integration
│   ├── __init__.py
│   └── concert_api.py         # ConcertAPIClient (363 lines)
│
├── ui/                         # Dashboard UI Components
│   ├── __init__.py
│   ├── cves_tab.py            # CVE insights (330 lines)
│   ├── applications_tab.py    # Applications insights (738 lines)
│   └── certificates_tab.py    # Certificates insights (408 lines)
│
├── utils/                      # Data Processing
│   ├── __init__.py
│   └── data_processor.py      # DataProcessor class (382 lines)
│
└── logs/                       # Application logs
    └── app.log                # Runtime logs
```

### IBM Concert API Integration

**Endpoints Used:**

**CVE Endpoints:**
- `GET /core/api/v1/vulnerability/cves` - List all CVEs

**Application Endpoints:**
- `GET /core/api/v1/applications` - List applications
- `GET /core/api/v1/applications/{name}` - Application details
- `GET /core/api/v1/applications/{name}/vulnerability_details` - Application CVEs
- `GET /core/api/v1/applications/{name}/build_artifacts` - Build artifacts
- `GET /core/api/v1/applications/{name}/build_artifacts/{artifact_id}/cves` - Artifact CVEs

**Certificate Endpoints:**
- `GET /core/api/v1/certificates` - List certificates
- `GET /core/api/v1/certificates/{id}` - Certificate details
- `GET /core/api/v1/certificate_issuers` - List certificate issuers

**Authentication Format:**
```python
headers = {
    'authorization': 'C_API_KEY {your_api_key}',  # Literal "C_API_KEY" prefix
    'InstanceID': '{your_instance_id}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
```

### Data Processing Features

**CVE Severity Calculation:**

| Risk Score | Severity |
|------------|----------|
| 9.0 - 10.0 | CRITICAL |
| 7.0 - 8.9  | HIGH |
| 4.0 - 6.9  | MEDIUM |
| 0.1 - 3.9  | LOW |
| 0          | INFORMATIONAL |

**Field Mappings:**
- **CVE Fields:** `cve`, `highest_finding_risk_score`, `wx_details`, `highest_finding_priority`
- **Application Fields:** `name`, `resilience_status`, `last_updated_on`, `criticality`
- **Certificate Fields:** `id`, `subject`, `validity_start_date`, `validity_end_date`, `status`, `metadata`

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- IBM Concert instance with API access
- IBM Concert API credentials:
  - Base URL
  - API Key (C_API_KEY format)
  - Instance ID
- Network connectivity to IBM Concert API endpoints

### Quick Setup

1. **Navigate to the project:**
   ```bash
   cd optimize/automated-resilience-and-compliance/assets/automate-resilience
   ```

2. **Run automated setup:**
   
   **Unix/macOS/Linux:**
   ```bash
   ./setup_and_run.sh
   ```
   
   **Windows:**
   ```cmd
   setup_and_run.bat
   ```
   
   The script will:
   - Create virtual environment
   - Install dependencies
   - Create `.env` file from template
   - Validate configuration
   - Launch the dashboard

3. **Configure credentials:**
   
   Edit `.env` file:
   ```env
   CONCERT_BASE_URL=https://your-concert-instance.ibm.com
   C_API_KEY=your_api_key_here
   INSTANCE_ID=your_instance_id_here
   ```

4. **Test connection (optional):**
   ```bash
   python test_api_connection.py
   ```

5. **Access dashboard:**
   ```
   http://127.0.0.1:8050
   ```

---

## Use Cases

### 1. Vulnerability Management

**Scenario:** Track and prioritize security vulnerabilities across your application portfolio

**Workflow:**
1. Navigate to **CVE Insights** tab
2. Click "Load CVE Data" to fetch latest vulnerabilities
3. Review statistics: Total CVEs, Critical/High counts, Average risk score
4. Analyze visualizations:
   - Severity distribution to understand overall risk
   - Risk score histogram to identify concentration
   - Top 10 highest risk CVEs for immediate action
5. Use the detailed table to:
   - Sort by risk score or priority
   - Filter by severity level
   - Export data for reporting

**Benefits:**
- Prioritize remediation efforts based on risk scores
- Track vulnerability trends over time
- Generate compliance reports

### 2. Application Security Monitoring

**Scenario:** Monitor security posture of applications and their build artifacts

**Workflow:**
1. Navigate to **Applications** tab
2. Click "Load Applications" to view portfolio
3. Review portfolio overview:
   - Total applications and vulnerabilities
   - Status distribution (healthy vs. at-risk)
   - Vulnerability ranges across applications
4. Drill down into specific application:
   - Click application row to view CVE analytics
   - Analyze severity distribution and risk scores
   - Review top vulnerabilities affecting the app
5. Explore build artifacts:
   - View all artifacts for the application
   - Select artifact to see artifact-specific CVEs
   - Compare vulnerabilities across different builds

**Benefits:**
- Identify applications with highest security risk
- Track vulnerability introduction in builds
- Make informed deployment decisions

### 3. Certificate Lifecycle Management

**Scenario:** Prevent service disruptions due to expired certificates

**Workflow:**
1. Navigate to **Certificates** tab
2. Click "Load Certificates" to fetch certificate data
3. Review statistics:
   - Total certificates
   - Valid certificates
   - Expiring soon (30 days)
   - Expired certificates
4. Analyze visualizations:
   - Status distribution for overall health
   - Expiry timeline to plan renewals
   - Algorithm distribution for security compliance
   - Key size analysis for cryptographic strength
5. Review certificate table:
   - Sort by expiry date
   - Filter by status
   - Identify certificates needing renewal

**Benefits:**
- Proactive certificate renewal planning
- Avoid service disruptions
- Ensure cryptographic compliance

### 4. Compliance Reporting

**Scenario:** Generate compliance reports for audits and governance

**Workflow:**
1. Collect data from all three tabs (CVEs, Applications, Certificates)
2. Use visualizations and tables to:
   - Document vulnerability remediation status
   - Show application security posture
   - Prove certificate management practices
3. Export data for compliance documentation
4. Track improvements over time

**Benefits:**
- Streamlined audit preparation
- Evidence-based compliance reporting
- Continuous improvement tracking

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User / Administrator                  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Browser    │  │   IBM Bob    │  │   Reports    │ │
│  │  Dashboard   │  │  (with Mode) │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│         Automated Resilience & Compliance Layer          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Concert Insights Dashboard             │  │
│  │                                                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  │
│  │  │   CVE    │  │   Apps   │  │ Certificates │  │  │
│  │  │ Insights │  │ Insights │  │   Insights   │  │  │
│  │  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │  │
│  │       │             │                │          │  │
│  │       └─────────────┴────────────────┘          │  │
│  │                     │                           │  │
│  │              ┌──────▼──────┐                    │  │
│  │              │ API Client  │                    │  │
│  │              │ - Auth      │                    │  │
│  │              │ - Pagination│                    │  │
│  │              │ - Error     │                    │  │
│  │              │   Handling  │                    │  │
│  │              └──────┬──────┘                    │  │
│  └─────────────────────┼───────────────────────────┘  │
└────────────────────────┼──────────────────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  IBM Concert    │
                │  REST API       │
                │  - CVEs         │
                │  - Applications │
                │  - Certificates │
                │  - Artifacts    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Data Sources   │
                │  - Scanners     │
                │  - Registries   │
                │  - Cert Stores  │
                └─────────────────┘
```

### Data Flow

1. **User Interaction:** User clicks "Load Data" button in dashboard
2. **API Request:** Dashboard sends authenticated request to IBM Concert API
3. **Data Retrieval:** Concert API returns paginated data (CVEs, apps, or certificates)
4. **Data Processing:** DataProcessor transforms raw API data into visualization-ready format
5. **Visualization:** Plotly charts and tables render interactive visualizations
6. **User Analysis:** User interacts with charts, filters, and drill-down features

---

## Best Practices

### 1. Dashboard Configuration

**Environment Variables:**
```env
# Required
CONCERT_BASE_URL=https://your-instance.ibm.com  # No trailing slash
C_API_KEY=your_api_key                          # Without "C_API_KEY" prefix
INSTANCE_ID=your_instance_id

# Optional
DEBUG_MODE=False
HOST=127.0.0.1
PORT=8050
API_TIMEOUT=30
API_PAGE_LIMIT=100
```

**Security:**
- Never commit `.env` file to version control
- Rotate API keys regularly
- Use environment-specific credentials
- Restrict dashboard access to authorized users

### 2. Performance Optimization

**API Usage:**
- Use `API_PAGE_LIMIT` to control data volume
- Implement caching for frequently accessed data
- Schedule data refreshes during off-peak hours
- Monitor API rate limits

**Dashboard Performance:**
- Limit initial data load size
- Use pagination for large datasets
- Implement lazy loading for drill-down views
- Optimize chart rendering with data sampling

### 3. Vulnerability Management

**Prioritization:**
- Focus on CRITICAL and HIGH severity CVEs first
- Consider `highest_finding_priority` field
- Review `total_findings` to understand impact scope
- Use risk score trends to identify worsening issues

**Remediation Workflow:**
1. Identify high-risk CVEs from dashboard
2. Drill down to affected applications
3. Review build artifacts to find introduction point
4. Plan remediation strategy
5. Track progress through dashboard updates

### 4. Certificate Management

**Proactive Monitoring:**
- Set up regular dashboard reviews (weekly/monthly)
- Focus on certificates expiring within 30 days
- Monitor algorithm usage for deprecated algorithms
- Track key size distribution for compliance

**Renewal Process:**
1. Identify expiring certificates (30-90 days out)
2. Initiate renewal process
3. Update certificate stores
4. Verify in dashboard after renewal

### 5. Compliance Reporting

**Regular Reporting:**
- Schedule monthly compliance reviews
- Export data from all three tabs
- Track metrics over time:
  - CVE remediation rate
  - Application security posture
  - Certificate renewal timeliness
- Document improvements for audits

---

## 📚 Related Resources

### Automated Resilience Assets
- [Concert Insights Dashboard](assets/automate-resilience/README.md) - Python Dash application
  - [Quick Start Guide](assets/automate-resilience/QUICKSTART.md)
  - [Project Summary](assets/automate-resilience/PROJECT_SUMMARY.md)
- [Bob Modes](bob-modes/README.md) - Custom Bob modes for resilience

### Optimize Building Blocks
- [FinOps](../finops/README.md) - Cost optimization with IBM Turbonomic

### Observe Building Blocks
- [Application Observability](../../observe/application-observability/README.md) - Monitor with IBM Instana
  - [Dashboard](../../observe/application-observability/assets/application-observability/README.md)
- [Network Performance](../../observe/network-performance/README.md) - Network monitoring with IBM SevOne

### Build & Deploy Building Blocks
- [Retail Application](../../build-and-deploy/Iaas/assets/retailapp/README.md) - Sample application
- [Ansible Deployment](../../build-and-deploy/Iaas/assets/deploy-bob-anisble/README.md) - Automated deployment
- [Authentication Management](../../build-and-deploy/authentication-mgmt/README.md) - IBM Security Verify
- [Code Assistant](../../build-and-deploy/code-assistant/README.md) - AI-powered development

---

## Support & Contribution

### Getting Help

- **Dashboard Issues:** Check [README](assets/automate-resilience/README.md) and logs in `assets/automate-resilience/logs/app.log`
- **API Connection:** Run `test_api_connection.py` to diagnose issues
- **Configuration:** Review `.env.example` for required variables
- **IBM Concert API:** Consult IBM Concert documentation

### Troubleshooting

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Configuration validation failed | Ensure all required variables in `.env` |
| Authentication failed | Verify `C_API_KEY` (without prefix in .env) |
| Access forbidden | Check `INSTANCE_ID` matches your instance |
| No data returned | Verify API endpoint availability |
| Request timeout | Increase `API_TIMEOUT` or check network |

### Contributing

Contributions welcome! Areas for enhancement:
- Additional visualizations and analytics
- Export functionality (PDF, CSV, Excel)
- Scheduled data refresh
- Email/Slack alerting
- Multi-instance support
- Historical trend analysis

---

**[⬆ Back to Top](#️-automated-resilience-and-compliance-with-ibm-concert)**