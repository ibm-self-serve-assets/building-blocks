# Automated Resilience and Compliance Skills

This directory contains Bob skills for Automated Resilience and Compliance using IBM Concert.

## 🎯 Overview

The `automated-resilience-concert.zip` skill empowers Bob to help you build, deploy, and manage IBM Concert resilience and compliance dashboards and integrations. This skill provides comprehensive capabilities for creating production-ready monitoring solutions that track vulnerabilities, applications, and certificate lifecycles across your infrastructure.

## 📦 Available Skill

### automated-resilience-concert

A comprehensive skill for working with IBM Concert, providing capabilities for:

#### 1. 🎨 **Concert Dashboard Development**
Build production-ready Dash applications with IBM Carbon Design System for monitoring and managing Concert data:
- Multi-tab dashboards (CVE Insights, Application Insights, Certificate Insights)
- Real-time data visualization with Plotly charts
- Interactive filtering and drill-down capabilities
- Responsive design with professional UI components
- Comprehensive analytics and statistics

#### 2. 🔌 **IBM Concert API Integration**
Create robust API clients for IBM Concert REST API:
- Session-based authentication with credential management
- Pagination support for large datasets
- Response normalization and error handling
- Support for all major endpoints (CVEs, applications, certificates, artifacts)
- Server-side filtering and search capabilities

#### 3. 🔒 **Vulnerability Management**
Implement comprehensive CVE tracking and analysis:
- CVE severity categorization (Critical, High, Medium, Low, Informational)
- Risk score analysis and distribution
- Priority-based vulnerability tracking
- Top 10 highest risk CVE identification
- Total findings and impact assessment
- Severity distribution visualization

#### 4. 📱 **Application Security Monitoring**
Build interfaces for application portfolio security:
- Portfolio overview with status distribution
- Multi-level drill-down (Portfolio → Application → Build Artifacts → CVEs)
- Application-specific CVE analytics
- Build artifact vulnerability tracking
- Vulnerability comparison across builds
- Application criticality assessment

#### 5. 🔐 **Certificate Lifecycle Management**
Track and manage certificate lifecycles:
- Valid, expired, and expiring certificate tracking
- Expiry timeline visualization
- Algorithm and key size distribution analysis
- Expiry alerts (Critical: ≤7 days, Warning: 8-30 days, Info: 31-90 days)
- Certificate status monitoring
- Proactive renewal planning

#### 6. 📊 **Data Processing & Analytics**
Implement sophisticated data processing:
- Risk score calculation and severity mapping
- UNIX timestamp conversion and formatting
- JSON metadata parsing
- Statistical analysis and aggregation
- Interactive chart generation
- Export-ready data formatting

#### 7. 🏗️ **Production-Ready Deployment**
Deploy Concert integrations with enterprise standards:
- Python virtual environment setup
- Automated setup scripts (Unix/Windows)
- Environment variable management
- Comprehensive logging and error handling
- Configuration validation
- Health checks and monitoring

#### 8. 🔒 **Security & Compliance**
Implement secure Concert integrations:
- Secure credential storage and session management
- API authentication with C_API_KEY format
- SSL/TLS certificate handling
- No persistent data storage (memory-only)
- Secure API communication patterns
- Compliance reporting capabilities

## 🚀 Installation and Setup

### Step 1: Download the Skill
Download the `automated-resilience-concert.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/automated-resilience-concert.zip
```

After extraction, you should see an `automated-resilience-concert` folder in your `.bob/skills` directory.

### Step 3: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/automated-resilience-concert
```

You should see the skill files and configuration.

### Step 4: Activate the Skill
To use the skill:
1. Open Bob and select any mode you want to work in
2. Enable the **Skills** button in that mode
3. The `automated-resilience-concert` skill will be available for use within that mode

## 💡 Usage Examples

Once activated, you can ask Bob to help with tasks like:

### Dashboard Development
- *"Create a Concert dashboard with CVE insights and application monitoring"*
- *"Add a certificate lifecycle tracking tab to the dashboard"*
- *"Implement drill-down from applications to build artifacts"*
- *"Create interactive charts for vulnerability severity distribution"*

### API Integration
- *"Create a Concert API client with authentication"*
- *"Add pagination support for fetching large datasets"*
- *"Implement error handling for Concert API requests"*
- *"Add server-side filtering for application search"*

### Vulnerability Management
- *"Build a CVE tracking interface with severity categorization"*
- *"Create charts for risk score distribution"*
- *"Implement filtering for critical and high severity CVEs"*
- *"Add top 10 highest risk CVE visualization"*

### Application Monitoring
- *"Create an application portfolio overview dashboard"*
- *"Implement multi-level drill-down for application CVEs"*
- *"Add build artifact vulnerability tracking"*
- *"Create comparison views for vulnerabilities across builds"*

### Certificate Management
- *"Build a certificate lifecycle monitoring interface"*
- *"Create expiry alerts for certificates expiring soon"*
- *"Add algorithm and key size distribution charts"*
- *"Implement certificate renewal planning dashboard"*

### Deployment
- *"Create automated setup scripts for the Concert dashboard"*
- *"Configure environment variables for Concert credentials"*
- *"Add comprehensive logging and error handling"*
- *"Implement configuration validation"*

## 🎓 What Bob Can Help You Build

With this skill, Bob can assist you in creating:

1. **Complete Dashboards**: Full-featured Concert monitoring dashboards with multiple tabs and visualizations
2. **API Clients**: Robust Python clients for IBM Concert REST API with comprehensive error handling
3. **Custom Integrations**: Tailored solutions for specific Concert use cases
4. **Monitoring Tools**: Specialized tools for CVE tracking, application security, and certificate management
5. **Analytics Solutions**: Data processing and visualization for compliance reporting
6. **Deployment Configurations**: Automated setup scripts and production deployment configurations

## 📋 Prerequisites

To work with this skill effectively, you should have:

- Python 3.8 or higher installed
- Access to an IBM Concert instance
- Valid IBM Concert credentials with API access:
  - Base URL
  - API Key (C_API_KEY format)
  - Instance ID
- Network connectivity to your IBM Concert instance
- Basic understanding of REST APIs (Bob will guide you through the details)

## 🔧 Key Technologies

This skill helps you work with:

- **IBM Concert REST API**: Vulnerability management and compliance platform
- **Dash by Plotly**: Interactive web applications
- **Plotly**: Data visualization and charting
- **IBM Carbon Design System**: Professional UI components
- **Python**: Backend development and API integration
- **pandas**: Data processing and analysis
- **requests**: HTTP client for API integration
- **python-dotenv**: Environment variable management

## 🔍 IBM Concert API Endpoints

The skill helps you work with these IBM Concert REST API endpoints:

### CVE Endpoints
- `GET /core/api/v1/vulnerability/cves` - List all CVEs

### Application Endpoints
- `GET /core/api/v1/applications` - List applications
- `GET /core/api/v1/applications/{name}` - Application details
- `GET /core/api/v1/applications/{name}/vulnerability_details` - Application CVEs
- `GET /core/api/v1/applications/{name}/build_artifacts` - Build artifacts
- `GET /core/api/v1/applications/{name}/build_artifacts/{artifact_id}/cves` - Artifact CVEs

### Certificate Endpoints
- `GET /core/api/v1/certificates` - List certificates
- `GET /core/api/v1/certificates/{id}` - Certificate details
- `GET /core/api/v1/certificate_issuers` - List certificate issuers

## 📊 Data Processing Features

### CVE Severity Calculation

The skill implements severity mapping based on risk scores:

| Risk Score | Severity |
|------------|----------|
| 9.0 - 10.0 | CRITICAL |
| 7.0 - 8.9  | HIGH |
| 4.0 - 6.9  | MEDIUM |
| 0.1 - 3.9  | LOW |
| 0          | INFORMATIONAL |

### Field Mappings

**CVE Fields:**
- CVE ID: `cve` field
- Risk Score: `highest_finding_risk_score`
- Description: `wx_details` or `wx_recommendation`
- Priority: `highest_finding_priority`
- Findings: `total_findings`

**Application Fields:**
- Name: `name`
- Status: `resilience_status`
- Last Updated: `last_updated_on` (UNIX timestamp)
- Owner: `last_updated_by`
- Vulnerabilities: `criticality`

**Certificate Fields:**
- ID: `id`
- Subject: `subject`
- Dates: `validity_start_date`, `validity_end_date` (UNIX timestamps)
- Status: `status`
- Metadata: `metadata` (JSON string)

## 🐛 Troubleshooting

### Skill doesn't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions on the extracted files
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

### Skill is active but Bob doesn't understand Concert requests
1. Be specific in your requests (mention "Concert" or "IBM Concert" explicitly)
2. Reference specific features (e.g., "CVE tracking", "certificate lifecycle")
3. Provide context about what you're trying to build
4. Ask Bob to explain the skill's capabilities if unsure

### Need help with Concert API specifics
1. Ask Bob about specific API endpoints or data structures
2. Request examples of API integration patterns
3. The skill includes knowledge of common API issues and solutions

### Authentication Issues
- **Problem**: "Authentication failed"
  - **Solution**: Verify `C_API_KEY` is correct (without the "C_API_KEY" prefix in configuration)
- **Problem**: "Access forbidden"
  - **Solution**: Verify `INSTANCE_ID` matches your IBM Concert instance

### API Issues
- **Problem**: "No data returned from API"
  - **Solution**: Check API endpoint availability and permissions
- **Problem**: "Request timeout"
  - **Solution**: Increase API timeout or check network connectivity

## 📚 Related Resources

- [IBM Concert Documentation](https://www.ibm.com/docs/en/concert)
- [Parent Directory README](../README.md) - Complete building block documentation
- [Concert Dashboard Implementation](../assets/automate-resilience/README.md) - Full dashboard example
- [Quick Start Guide](../assets/automate-resilience/QUICKSTART.md) - Getting started quickly
- [Dash Documentation](https://dash.plotly.com/)
- [IBM Carbon Design System](https://carbondesignsystem.com/)

## 🎯 Skill Capabilities Summary

| Capability | Description |
|------------|-------------|
| **Dashboard Creation** | Build multi-tab monitoring dashboards with professional UI |
| **API Integration** | Implement robust Concert REST API clients with pagination |
| **CVE Management** | Track and analyze vulnerabilities with severity categorization |
| **Application Monitoring** | Monitor application security with multi-level drill-down |
| **Certificate Lifecycle** | Track certificate expiry and manage renewals proactively |
| **Data Visualization** | Create interactive charts for CVEs, applications, and certificates |
| **Risk Analysis** | Calculate risk scores and identify highest priority issues |
| **Compliance Reporting** | Generate compliance reports and analytics |
| **Production Deployment** | Deploy with automated setup scripts and configuration |
| **Security** | Implement secure authentication and credential management |

## 📊 Performance

Typical response times:

- **Dashboard Generation**: ~10-20 seconds (complete multi-tab dashboard)
- **API Client Creation**: ~5-10 seconds (with authentication and error handling)
- **Data Processing**: ~3-8 seconds (depends on data volume)
- **Visualization**: ~5-15 seconds (interactive charts and tables)
- **Setup Scripts**: ~2-5 seconds (automated configuration)

## 💬 Support

For issues or questions about this skill:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for implementation examples
3. Review the [Concert Dashboard README](../assets/automate-resilience/README.md) for detailed usage
4. Ask Bob directly - the skill includes comprehensive knowledge
5. Refer to IBM Concert documentation for API-specific questions

## 📝 Version Information

- **Skill Version**: 1.0.0
- **Compatible with**: IBM Concert (all versions with REST API support)
- **Last Updated**: 2026-06-22
- **Status**: Production Ready ✅

---

**Note**: This skill is designed to work with IBM Concert. Ensure you have proper access and credentials before starting development.

Made with ❤️ for IBM Concert automation
