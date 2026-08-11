# Application Observability Skills

This directory contains Bob skills for Application Observability using IBM Instana.

## 🎯 Overview

The `application-observability.zip` skill empowers Bob to help you build, deploy, and manage IBM Instana observability dashboards and integrations. This skill provides comprehensive capabilities for creating production-ready monitoring solutions that track service health, incidents, and performance metrics across your application infrastructure.

## 📦 Available Skill

### application-observability

A comprehensive skill for working with IBM Instana, providing capabilities for:

#### 1. 🎨 **Instana Dashboard Development**
Build production-ready Dash applications for monitoring application health through IBM Instana:
- Real-time service health monitoring with composite health scores
- Interactive visualizations with Plotly charts
- Service metrics tables with error rate and latency data
- Auto-refresh capabilities for live monitoring
- Responsive design with Bootstrap UI components

#### 2. 🔌 **IBM Instana API Integration**
Create robust API clients for IBM Instana REST API:
- Token-based authentication with secure credential management
- Application and service metrics retrieval
- Event and incident data fetching
- Support for major endpoints (applications, services, metrics, events, traces)
- Rate limit handling and error management

#### 3. 🏥 **Service Health Monitoring**
Implement comprehensive service health tracking and analysis:
- Composite health score calculation (error rate, latency, call volume)
- Real-time service call count monitoring
- Error rate tracking with trend analysis
- Latency monitoring and response time analysis
- Service availability and uptime tracking

#### 4. 🚨 **Incident & Event Management**
Build interfaces for AI-powered incident response:
- Kubernetes event analysis with detailed insights
- Agent monitoring event tracking and frequency analysis
- Issue and incident lifecycle management
- Change event monitoring and correlation
- Automated root cause analysis

#### 5. 📈 **Performance Analytics**
Track and analyze application performance metrics:
- Latency distribution and percentile analysis
- Call volume trends and traffic patterns
- Error rate analysis and anomaly detection
- Service dependency mapping and visualization
- Performance regression detection across deployments

#### 6. 📊 **Data Processing & Visualization**
Implement sophisticated data processing for observability data:
- Health score calculation with weighted algorithms
- Time-series data processing and aggregation
- Natural language time range parsing ("last 24 hours")
- Interactive chart generation with Plotly
- Export-ready metrics formatting

#### 7. 🤖 **MCP Server Integration**
Deploy and configure the Instana MCP server for AI-powered observability:
- Model Context Protocol server setup and configuration
- Docker containerized deployment
- IBM Cloud Code Engine deployment
- AI assistant integration for natural language observability queries
- Automated event summarization and problem identification

#### 8. 🏗️ **Production-Ready Deployment**
Deploy Instana integrations with enterprise standards:
- Python virtual environment setup
- Automated setup scripts (Unix/Windows)
- Environment variable management for Instana credentials
- Comprehensive logging and error handling
- Configuration validation and health checks

## 🚀 Installation and Setup

### Step 1: Download the Skill
Download the `application-observability.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/application-observability.zip
```

After extraction, you should see an `application-observability` folder in your `.bob/skills` directory.

### Step 3: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/application-observability
```

You should see the skill files and configuration.

### Step 4: Activate the Skill
To use the skill:
1. Open Bob and select any mode you want to work in
2. Enable the **Skills** button in that mode
3. The `application-observability` skill will be available for use within that mode

## 💡 Usage Examples

Once activated, you can ask Bob to help with tasks like:

### Dashboard Development
- *"Create an Instana observability dashboard with service health monitoring"*
- *"Add real-time error rate and latency charts to the dashboard"*
- *"Implement a composite health score visualization for my services"*
- *"Create interactive charts for service call volume trends"*

### API Integration
- *"Create an IBM Instana API client with token authentication"*
- *"Add pagination support for fetching large event datasets from Instana"*
- *"Implement error handling for Instana REST API requests"*
- *"Add rate limiting and retry logic for Instana API calls"*

### Service Health Monitoring
- *"Build a service health monitoring dashboard using Instana metrics"*
- *"Create a composite health score algorithm for my microservices"*
- *"Implement error rate tracking with trend visualization"*
- *"Add latency monitoring with percentile distribution charts"*

### Incident Management
- *"Create an incident response workflow using the Instana MCP server"*
- *"Build a Kubernetes event monitoring interface with Instana"*
- *"Implement automated root cause analysis for application issues"*
- *"Create change event correlation for deployment tracking"*

### MCP Server Setup
- *"Set up the Instana MCP server for IBM Bob integration"*
- *"Configure the MCP server for Docker deployment"*
- *"Deploy the Instana MCP server to IBM Cloud Code Engine"*
- *"Configure natural language time ranges for Instana event queries"*

### Deployment
- *"Create automated setup scripts for the Instana observability dashboard"*
- *"Configure environment variables for Instana API credentials"*
- *"Add comprehensive logging and error handling to the Instana integration"*
- *"Implement configuration validation for Instana connectivity"*

## 🎓 What Bob Can Help You Build

With this skill, Bob can assist you in creating:

1. **Complete Dashboards**: Full-featured Instana monitoring dashboards with real-time service health visualizations
2. **API Clients**: Robust Python clients for IBM Instana REST API with comprehensive error handling
3. **MCP Servers**: Model Context Protocol servers for AI-powered observability automation
4. **Custom Integrations**: Tailored solutions for specific Instana observability use cases
5. **Monitoring Tools**: Specialized tools for service health, incident tracking, and performance analysis
6. **Deployment Configurations**: Automated setup scripts and production deployment configurations

## 📋 Prerequisites

To work with this skill effectively, you should have:

- Python 3.8 or higher installed
- Access to an IBM Instana instance
- Valid IBM Instana API token with read permissions:
  - Instana Base URL
  - Instana API Token
  - (Optional) Application name filter
- Network connectivity to your IBM Instana instance
- Basic understanding of REST APIs (Bob will guide you through the details)

## 🔧 Key Technologies

This skill helps you work with:

- **IBM Instana REST API**: Application performance monitoring and observability platform
- **Dash by Plotly**: Interactive web applications for monitoring dashboards
- **Plotly**: Data visualization and charting for metrics
- **Dash Bootstrap Components**: Professional UI components
- **Python**: Backend development and API integration
- **pandas**: Data processing and metrics analysis
- **requests**: HTTP client for Instana API integration
- **python-dotenv**: Environment variable management
- **Docker**: Container-based MCP server deployment

## 🔍 IBM Instana API Endpoints

The skill helps you work with these IBM Instana REST API endpoints:

### Application Endpoints
- `GET /api/application-monitoring/applications` - List monitored applications
- `GET /api/application-monitoring/metrics/services` - Service metrics data
- `GET /api/application-monitoring/calls/groups` - Call group analysis

### Event Endpoints
- `GET /api/events` - List all events
- `GET /api/events/{eventId}` - Get specific event by ID
- `POST /api/events/batch` - Batch event retrieval

### Incident Endpoints
- `GET /api/incidents` - List all incidents
- `GET /api/issues` - List all issues

### Infrastructure Endpoints
- `GET /api/infrastructure-monitoring/snapshots` - Infrastructure snapshots
- `GET /api/infrastructure-monitoring/metrics` - Infrastructure metrics

## 📊 Health Score Algorithm

The skill implements a composite health scoring algorithm:

| Metric | Weight | Scoring |
|--------|--------|---------|
| Error Rate | 40% | Lower is better |
| Latency | 30% | Lower is better |
| Call Volume | 30% | Higher indicates activity |

### Health Score Interpretation

| Score Range | Status |
|-------------|--------|
| 80 - 100 | 🟢 Healthy |
| 60 - 79 | 🟡 Warning |
| 40 - 59 | 🟠 Degraded |
| 0 - 39 | 🔴 Critical |

## 🐛 Troubleshooting

### Skill doesn't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions on the extracted files
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

### Skill is active but Bob doesn't understand Instana requests
1. Be specific in your requests (mention "Instana" or "IBM Instana" explicitly)
2. Reference specific features (e.g., "service health monitoring", "incident tracking")
3. Provide context about what you're trying to build
4. Ask Bob to explain the skill's capabilities if unsure

### Need help with Instana API specifics
1. Ask Bob about specific API endpoints or data structures
2. Request examples of API integration patterns
3. The skill includes knowledge of common Instana API issues and solutions

### Authentication Issues
- **Problem**: "Authentication failed"
  - **Solution**: Verify the `INSTANA_API_TOKEN` is correct and has read permissions
- **Problem**: "Access forbidden"
  - **Solution**: Confirm the token has access to the required Instana endpoints

### API Issues
- **Problem**: "No data returned from API"
  - **Solution**: Check API endpoint availability and verify `INSTANA_BASE_URL` is correct
- **Problem**: "Request timeout"
  - **Solution**: Increase API timeout or check network connectivity to Instana

## 📚 Related Resources

- [IBM Instana Documentation](https://www.ibm.com/docs/en/instana-observability)
- [IBM Instana REST API Reference](https://instana.github.io/openapi/)
- [Parent Directory README](../README.md) - Complete building block documentation
- [Bob Modes README](../bob-modes/README.md) - Application Observability Bob mode
- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Documentation](https://plotly.com/python/)

## 🎯 Skill Capabilities Summary

| Capability | Description |
|------------|-------------|
| **Dashboard Creation** | Build real-time monitoring dashboards with service health visualizations |
| **API Integration** | Implement robust Instana REST API clients with authentication |
| **Service Health Monitoring** | Track composite health scores across microservices |
| **Incident Management** | Monitor and analyze incidents, issues, and change events |
| **Performance Analytics** | Analyze latency, error rates, and call volume trends |
| **MCP Server Setup** | Deploy Instana MCP server for AI-powered observability |
| **Event Analysis** | Process and summarize Kubernetes and agent monitoring events |
| **Root Cause Analysis** | Automated problem detection and fix suggestions |
| **Production Deployment** | Deploy with automated setup scripts and configuration |
| **CI/CD Integration** | Pre/post-deployment health checks and performance regression detection |

## 📊 Performance

Typical response times:

- **Dashboard Generation**: ~10-20 seconds (complete monitoring dashboard)
- **API Client Creation**: ~5-10 seconds (with authentication and error handling)
- **MCP Server Setup**: ~5-10 seconds (Docker or Code Engine configuration)
- **Data Processing**: ~3-8 seconds (depends on data volume)
- **Visualization**: ~5-15 seconds (interactive charts and tables)
- **Setup Scripts**: ~2-5 seconds (automated configuration)

## 💬 Support

For issues or questions about this skill:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for implementation examples
3. Ask Bob directly — the skill includes comprehensive Instana knowledge
4. Refer to [IBM Instana documentation](https://www.ibm.com/docs/en/instana-observability) for API-specific questions

## 📝 Version Information

- **Skill Version**: 1.0.0
- **Compatible with**: IBM Instana (all versions with REST API support)
- **Last Updated**: 2025-06-22
- **Status**: Production Ready ✅

---

**Note**: This skill is designed to work with IBM Instana. Ensure you have proper access and API token credentials before starting development.

Made with ❤️ for IBM Instana observability automation
