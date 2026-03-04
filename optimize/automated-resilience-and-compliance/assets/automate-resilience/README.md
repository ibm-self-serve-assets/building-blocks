# IBM Concert Insights Dashboard

A comprehensive Python Dash application for visualizing and managing IBM Concert data, including vulnerability management (CVEs), application monitoring, and certificate lifecycle tracking.

## Features

### 🔒 CVE Insights
- **Comprehensive CVE Analytics**: View all vulnerabilities with severity-based categorization
- **Interactive Visualizations**:
  - Severity distribution pie chart
  - Risk score histogram
  - Top 10 highest risk CVEs
  - Priority distribution analysis
- **Detailed CVE Table**: Sortable, filterable table with severity-based color coding
- **Statistics Dashboard**: Total CVEs, critical count, high severity count, average risk score

### 📱 Application Insights
- **Portfolio Overview**:
  - Total applications and vulnerabilities
  - Application status distribution
  - Vulnerability distribution analysis
  - Build artifact correlation
  - Top 10 applications by vulnerability count
- **Multi-Level Drill-Down**:
  1. Select application → View application-specific CVE analytics
  2. View build artifacts → Select artifact for detailed CVE analysis
  3. Compare vulnerabilities across different builds
- **Application CVE Analytics**:
  - Severity distribution charts
  - Risk score histograms
  - Top 10 highest risk CVEs per application
  - Priority-based filtering
- **Build Artifact Tracking**:
  - Artifact-level vulnerability analysis
  - CVE comparison across builds
  - Build-specific remediation insights

### 🔐 Certificate Insights
- **Certificate Lifecycle Management**:
  - Valid, expired, and expiring certificates tracking
  - Expiry timeline visualization
  - Algorithm and key size distribution
- **Expiry Alerts**:
  - Critical: ≤7 days until expiry
  - Warning: 8-30 days until expiry
  - Info: 31-90 days until expiry
- **Certificate Analytics**:
  - Status distribution
  - Top 10 certificates expiring soon
  - Algorithm usage patterns
  - Key size analysis

## Architecture

```
concert-insights-dashboard/
├── api/                    # IBM Concert API client
│   ├── __init__.py
│   └── concert_api.py     # ConcertAPIClient with authentication
├── ui/                     # Dashboard UI components
│   ├── __init__.py
│   ├── cves_tab.py        # CVE insights tab
│   ├── applications_tab.py # Applications insights tab
│   └── certificates_tab.py # Certificates insights tab
├── utils/                  # Data processing utilities
│   ├── __init__.py
│   └── data_processor.py  # DataProcessor class
├── logs/                   # Application logs
├── app.py                  # Main application entry point
├── config.py              # Configuration and logging setup
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── setup_and_run.sh      # Unix/macOS/Linux setup script
└── setup_and_run.bat     # Windows setup script
```

## Prerequisites

- Python 3.8 or higher
- IBM Concert instance with API access
- IBM Concert API credentials:
  - Base URL
  - API Key (C_API_KEY format)
  - Instance ID

## Quick Start

### Option 1: Automated Setup (Recommended)

#### Unix/macOS/Linux:
```bash
./setup_and_run.sh
```

#### Windows:
```cmd
setup_and_run.bat
```

The setup script will:
1. Create a virtual environment
2. Install all dependencies
3. Create `.env` file from template
4. Validate configuration
5. Launch the dashboard

### Option 2: Manual Setup

1. **Clone or download the repository**

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate.bat  # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your IBM Concert credentials
```

5. **Run the application**:
```bash
python app.py
```

6. **Access the dashboard**:
Open your browser to `http://127.0.0.1:8050`

## Configuration

Edit the `.env` file with your IBM Concert credentials:

```env
# IBM Concert API Configuration
CONCERT_BASE_URL=https://your-concert-instance.ibm.com
C_API_KEY=your_api_key_here
INSTANCE_ID=your_instance_id_here

# Application Configuration
DEBUG_MODE=False
HOST=127.0.0.1
PORT=8050

# API Configuration
API_TIMEOUT=30
API_PAGE_LIMIT=100
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CONCERT_BASE_URL` | IBM Concert instance URL (without trailing slash) | Required |
| `C_API_KEY` | IBM Concert API key (literal "C_API_KEY" prefix added automatically) | Required |
| `INSTANCE_ID` | IBM Concert instance identifier | Required |
| `DEBUG_MODE` | Enable debug mode (True/False) | False |
| `HOST` | Dashboard host address | 127.0.0.1 |
| `PORT` | Dashboard port number | 8050 |
| `API_TIMEOUT` | API request timeout in seconds | 30 |
| `API_PAGE_LIMIT` | Maximum items per API request | 100 |

## IBM Concert API Endpoints

The dashboard integrates with the following IBM Concert REST API endpoints:

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

## Authentication

The dashboard uses IBM Concert's authentication format:

```python
headers = {
    'authorization': 'C_API_KEY {your_api_key}',  # Literal "C_API_KEY" prefix
    'InstanceID': '{your_instance_id}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
```

**Important**: The `C_API_KEY` prefix is literal and required by the IBM Concert API.

## Data Processing

### CVE Severity Calculation

CVE severity is derived from the `highest_finding_risk_score`:

| Risk Score | Severity |
|------------|----------|
| 9.0 - 10.0 | CRITICAL |
| 7.0 - 8.9  | HIGH |
| 4.0 - 6.9  | MEDIUM |
| 0.1 - 3.9  | LOW |
| 0          | INFORMATIONAL |

### Field Mappings

The dashboard handles actual IBM Concert API field structures:

**CVE Fields**:
- CVE ID: `cve` field
- Risk Score: `highest_finding_risk_score`
- Description: `wx_details` or `wx_recommendation`
- Priority: `highest_finding_priority`
- Findings: `total_findings`

**Application Fields**:
- Name: `name`
- Status: `resilience_status`
- Last Updated: `last_updated_on` (UNIX timestamp)
- Owner: `last_updated_by`
- Vulnerabilities: `criticality`

**Certificate Fields**:
- ID: `id`
- Subject: `subject`
- Dates: `validity_start_date`, `validity_end_date` (UNIX timestamps)
- Status: `status`
- Metadata: `metadata` (JSON string)

## Logging

Application logs are stored in `logs/app.log` with the following information:
- Timestamp
- Logger name
- Log level (DEBUG, INFO, WARNING, ERROR)
- Message

Logs include:
- API requests and responses
- Data processing operations
- Error messages with stack traces
- Configuration validation

## Error Handling

The dashboard implements comprehensive error handling:

| Error Code | Message | Action |
|------------|---------|--------|
| 401 | Authentication failed | Check C_API_KEY |
| 403 | Access forbidden | Check INSTANCE_ID |
| 404 | Resource not found | Verify endpoint and parameters |
| Timeout | Request timeout | Check network and API_TIMEOUT |
| Connection | Network error | Verify CONCERT_BASE_URL |

