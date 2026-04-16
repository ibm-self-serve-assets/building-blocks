# Concert Security Dashboard

A comprehensive Python Dash application for monitoring and analyzing security insights from IBM Concert API, featuring Application Security, Vulnerabilities, Software Composition Analysis, Certificate Management, and System Health monitoring.

## Features

### 🛡️ Application Security Overview
- **Enterprise-wide Metrics**: Total applications, vulnerability counts, critical/high severity tracking
- **Visual Analytics**: 
  - Top 10 vulnerable applications (stacked bar chart)
  - Severity distribution (donut chart)
- **Real Vulnerability Data**: Fetches actual CVE data from Concert API
- **Risk Assessment**: Automatic risk level calculation based on vulnerability counts

### 🔍 Application Vulnerabilities (Drill-Through Analysis)
- **Application Selection**: Dropdown to select specific applications
- **Build Artifacts**: View all build artifacts for selected application
- **CVE Drill-Down**: Interactive "View CVEs" buttons to explore vulnerabilities
- **Detailed CVE Analysis**:
  - Severity distribution charts
  - Top 15 CVEs by risk score
  - Comprehensive CVE table with risk scores, priorities, and CVSS scores

### 📦 Software Composition Analysis
- **Package Metrics**: Total packages, high vulnerability count, back-level packages, denied licenses
- **Package Risk Distribution**: Visual breakdown of package issues
- **Top Vulnerable Packages**: Bar chart of packages with most vulnerabilities
- **Interactive CVE Exploration**: Click "View CVEs" to see package-specific vulnerabilities
- **CVE Tracking Status**: Shows which CVEs are tracked in Concert database
- **External Links**: Direct links to National Vulnerability Database (NVD)

### 🔐 Certificate Management
- **Certificate Inventory**: Complete list of SSL/TLS certificates
- **Expiration Tracking**: Automatic calculation of days until expiry
- **Status Monitoring**: Visual indicators for valid, expiring soon, and expired certificates
- **Certificate Metrics**: Total certificates, expiring soon (30 days), expired count
- **Expiry Distribution Chart**: Pie chart showing certificate status breakdown

### 💚 System Health
- **API Health Check**: Real-time Concert API connectivity status
- **Performance Metrics**: 
  - Total requests
  - Error count and rate
  - Average response time
- **Cache Statistics**: Cache size, file count, and management
- **Configuration Display**: Current settings and environment variables
- **Cache Management**: One-click cache clearing

## Architecture

### Resilient Design
- **Connection Pooling**: Efficient HTTP connection management
- **Retry Logic**: Exponential backoff for transient failures (3 retries)
- **Rate Limiting**: Token bucket algorithm (100 requests/minute)
- **Error Handling**: Comprehensive exception handling with fallbacks
- **Caching**: Multi-level caching with configurable TTLs
- **Graceful Degradation**: Fallback to cached data on API failures

### Technology Stack
- **Framework**: Python Dash with Bootstrap components
- **Visualization**: Plotly for interactive charts
- **Data Processing**: Pandas for efficient data manipulation
- **API Client**: Requests with session pooling
- **Caching**: Pickle-based persistent cache
- **Configuration**: python-dotenv for environment management

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Access to IBM Concert API

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd /path/to/project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   The `.env` file is already configured with your Concert API credentials:
   ```env
   CONCERT_BASE_URL=https://90076.us-south-8.concert.saas.ibm.com
   C_API_KEY=your_api_key_here
   InstanceID=your_instance_id_here
   ```

4. **Run the dashboard**
   ```bash
   python run_dashboard.py
   ```

5. **Access the dashboard**
   
   Open your browser and navigate to:
   ```
   http://localhost:8050
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CONCERT_BASE_URL` | Concert API base URL | Required |
| `C_API_KEY` | Concert API key | Required |
| `InstanceID` | Concert instance ID | Required |
| `APP_PORT` | Dashboard port | 8050 |
| `APP_HOST` | Dashboard host | 0.0.0.0 |
| `DEBUG_MODE` | Enable debug mode | False |
| `CACHE_ENABLED` | Enable caching | True |
| `CACHE_DIR` | Cache directory | .cache |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_FILE` | Log file path | app.log |
| `REFRESH_INTERVAL` | Auto-refresh interval (seconds) | 60 |
| `CONCERT_APPLICATION_NAME` | Filter to specific application | (empty) |

### Caching Strategy

| Endpoint | TTL | Rationale |
|----------|-----|-----------|
| Applications | 5 minutes | Frequently changing |
| Application Details | 10 minutes | Moderate change frequency |
| Vulnerabilities | 30 minutes | Relatively stable |
| Build Artifacts | 20 minutes | Moderate change frequency |
| Software Packages | 30 minutes | Infrequent changes |
| Certificates | 1 hour | Rarely change |
| Certificate Issuers | 4 hours | Very stable |

## Usage Guide

### Application Security Tab
1. View enterprise-wide security metrics at the top
2. Analyze the top 10 vulnerable applications chart
3. Review the severity distribution donut chart
4. Scroll down to see the detailed application table

### Application Vulnerabilities Tab
1. Select an application from the dropdown
2. Review application details and metadata
3. Browse build artifacts in the table
4. Click "View CVEs" on any artifact to see its vulnerabilities
5. Analyze CVE severity distribution and risk scores
6. Click the X button to close CVE details

### Software Composition Tab
1. Review package metrics at the top
2. Analyze package risk distribution chart
3. View top vulnerable packages bar chart
4. Scroll to the package table
5. Click "View CVEs" to see package-specific vulnerabilities
6. Review CVE tracking status (tracked vs not tracked)
7. Click "View on NVD" to see full CVE details

### Certificate Management Tab
1. View certificate metrics (total, expiring soon, expired)
2. Analyze certificate status distribution chart
3. Review certificate inventory table
4. Check expiration dates and status badges

### System Health Tab
1. Check API health status (healthy/unhealthy)
2. Review API performance metrics
3. View cache statistics
4. Check system configuration
5. Click "Clear Cache" to refresh all cached data

## API Integration

### Concert API Endpoints Used

1. **Applications**
   - `GET /core/api/v1/applications` - List all applications
   - `GET /core/api/v1/applications/{id}` - Get application details
   - `GET /core/api/v1/applications/{id}/vulnerability_details` - Get vulnerabilities
   - `GET /core/api/v1/applications/{id}/build_artifacts` - Get build artifacts
   - `GET /core/api/v1/applications/{id}/build_artifacts/{artifact_id}/cves` - Get artifact CVEs

2. **Software Composition**
   - `GET /core/api/v1/software_composition/packages` - List packages
   - `GET /core/api/v1/software_composition/package_highlights` - Get statistics
   - `GET /core/api/v1/software_composition/packages/{id}` - Get package details

3. **Certificates**
   - `GET /core/api/v1/certificates` - List certificates
   - `GET /core/api/v1/certificates/{id}` - Get certificate details
   - `GET /core/api/v1/certificate_issuers` - Get issuer statistics

### Error Handling

The dashboard implements comprehensive error handling:

- **Network Errors**: Retry with exponential backoff (1s, 2s, 4s)
- **Rate Limiting (429)**: Respect Retry-After header
- **Server Errors (5xx)**: Retry up to 3 times
- **Client Errors (4xx)**: Log and display user-friendly message
- **Timeouts**: 5s connect, 30s read timeout
- **Fallback**: Use cached data when API is unavailable

## Performance Optimization

### Data Fetching
- **Batch Processing**: Fetch data for multiple applications in parallel
- **Pagination**: Limit results to prevent memory issues
- **Selective Loading**: Only fetch data when tab is active
- **Lazy Loading**: Load CVE details only when requested

### Caching
- **Persistent Cache**: Pickle-based file cache survives restarts
- **TTL Management**: Different TTLs based on data volatility
- **Cache Invalidation**: Manual cache clearing available
- **Memory Efficient**: Stores only necessary data

### UI Optimization
- **Responsive Design**: Bootstrap grid system for all screen sizes
- **Progressive Loading**: Show metrics first, then charts, then tables
- **Interactive Charts**: Plotly for smooth, interactive visualizations
- **Efficient Rendering**: Dash callbacks prevent unnecessary re-renders

## Troubleshooting

### Dashboard won't start
- Check that all environment variables are set in `.env`
- Verify Python version is 3.8 or higher
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8050 is already in use

### No data displayed
- Verify Concert API credentials are correct
- Check network connectivity to Concert API
- Review logs in `app.log` for error messages
- Try clearing cache using the System Health tab

### Slow performance
- Check network latency to Concert API
- Review cache statistics in System Health tab
- Consider increasing cache TTLs in `src/services/data_service.py`
- Limit number of applications processed (currently 20)

### API errors
- Check API key expiration
- Verify instance ID is correct
- Review rate limiting settings
- Check Concert API status

## Project Structure

```
.
├── .env                          # Environment configuration
├── requirements.txt              # Python dependencies
├── run_dashboard.py             # Main entry point
├── src/
│   ├── __init__.py
│   ├── dashboard.py             # Main dashboard application
│   ├── api/
│   │   ├── __init__.py
│   │   └── concert_client.py    # Resilient API client
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache_manager.py     # Cache management
│   │   └── data_service.py      # Data access layer
│   └── ui/
│       ├── __init__.py
│       ├── tab_layouts.py       # Tab layout definitions
│       ├── dashboard_callbacks.py # Interactive callbacks
│       ├── chart_helpers.py     # Chart creation functions
│       └── table_helpers.py     # Table and component helpers
└── .cache/                      # Cache directory (auto-created)
```

## Security Considerations

- **Credentials**: Never commit `.env` file to version control
- **API Keys**: Rotate API keys regularly
- **HTTPS**: Always use HTTPS for Concert API connections
- **Input Validation**: All user inputs are validated
- **Error Messages**: Sensitive information not exposed in errors
- **Audit Logging**: All API requests are logged

## Maintenance

### Regular Tasks
- **Monitor Logs**: Review `app.log` for errors and warnings
- **Clear Cache**: Periodically clear cache to ensure fresh data
- **Update Dependencies**: Keep Python packages up to date
- **API Key Rotation**: Rotate Concert API keys as per policy
- **Performance Review**: Monitor API metrics in System Health tab

### Updating the Dashboard
1. Pull latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Clear cache: Use System Health tab or delete `.cache` directory
4. Restart dashboard: `python run_dashboard.py`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `app.log`
3. Verify Concert API connectivity
4. Check environment configuration

## License

This dashboard is built for IBM Concert API integration and follows IBM security and compliance standards.

---

**Built with ❤️ using Python Dash and IBM Concert API**
