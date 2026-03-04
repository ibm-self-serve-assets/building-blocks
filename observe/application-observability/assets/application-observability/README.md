# Instana Observability Dashboard

> **A unified dashboard for monitoring application health and performance**  
> *Powered by IBM Instana*

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/dash-2.14.2-green)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Overview

This modular Python Dash application provides comprehensive observability insights for the **finvault** application using IBM Instana. It visualizes service health metrics, error rates, latency trends, and provides real-time monitoring of your application's performance.

### Target Application
- **Primary Application**: `finvault`
- **Configurable**: Easily switch to other applications via `.env` file

---

## ✨ Features

### 🔍 Real-Time Observability

**Service Health Monitoring**
- Real-time service call counts and distribution
- Error rate tracking with trend analysis
- Latency monitoring (response times)
- Composite health scores per service

**Key Metrics**
- 📊 **Service Count**: Total number of services
- 📞 **Call Volume**: Total API calls across all services
- ⚠️ **Error Rate**: Average error percentage
- ⏱️ **Latency**: Average response time
- 💚 **Health Score**: Composite health indicator (0-100)

**Interactive Visualizations**
- Summary cards with key metrics at a glance
- Interactive bar charts for service health
- Error rate analysis by service
- Latency distribution charts
- Detailed service metrics table

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Python 3.8+ with Dash | Web application framework |
| **UI Components** | Dash Bootstrap Components | Modern, responsive UI |
| **Visualization** | Plotly | Interactive charts and graphs |
| **Data Processing** | pandas, numpy | Data manipulation and analysis |
| **API Integration** | requests | HTTP client for Instana REST API |
| **Configuration** | python-dotenv | Environment variable management |
| **Logging** | colorlog | Structured, color-coded logging |

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                          │
│               http://localhost:8050                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Dash Application (app.py)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Dashboard Component                       │  │
│  │  - Summary Cards                                  │  │
│  │  - Service Health Charts                          │  │
│  │  - Error Rate Charts                              │  │
│  │  - Latency Charts                                 │  │
│  │  - Service Details Table                          │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                      │
│  ┌────────────────▼─────────────────────────────────┐  │
│  │     Instana Integration (instana_integration.py) │  │
│  │  - API Client                                     │  │
│  │  - Data Processing                                │  │
│  │  - Metric Aggregation                             │  │
│  └────────────────┬─────────────────────────────────┘  │
└───────────────────┼──────────────────────────────────────┘
                    │
            ┌───────▼────────┐
            │  Instana API   │
            │  - Applications│
            │  - Services    │
            │  - Metrics     │
            │  - Trace Data  │
            └────────────────┘
```

---

## 📋 Prerequisites

### Required
- **Python**: 3.8 or higher
- **Instana Access**: Valid API credentials with read permissions
- **Network**: Access to Instana API endpoints

### System Requirements
- **OS**: Linux, macOS, or Windows
- **Memory**: 500MB+ available RAM
- **Disk**: 100MB+ free space

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Run Setup Script

**Unix/Linux/macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows:**
```cmd
scripts\setup.bat
```

The setup script will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create `.env` file from template

### 3. Configure Environment

Edit the `.env` file with your credentials:

```bash
# Instana Configuration
INSTANA_BASE_URL=https://your-instana-instance.com
INSTANA_API_TOKEN=your_instana_api_token_here
INSTANA_APPLICATION_NAME=finvault

# Application Configuration (optional)
APP_HOST=0.0.0.0
APP_PORT=8050
DEBUG_MODE=False
LOG_LEVEL=INFO
```

### 4. Run the Application

**Unix/Linux/macOS:**
```bash
./scripts/run.sh
```

**Windows:**
```cmd
scripts\run.bat
```

### 5. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8050
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `INSTANA_BASE_URL` | ✅ Yes | - | Instana instance URL |
| `INSTANA_API_TOKEN` | ✅ Yes | - | Instana API token |
| `INSTANA_APPLICATION_NAME` | ✅ Yes | `finvault` | Target application name |
| `APP_HOST` | ❌ No | `0.0.0.0` | Server host address |
| `APP_PORT` | ❌ No | `8050` | Server port |
| `DEBUG_MODE` | ❌ No | `False` | Enable debug mode |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level |
| `REFRESH_INTERVAL` | ❌ No | `300` | Auto-refresh interval (seconds) |
| `DEFAULT_TIMEFRAME` | ❌ No | `3600000` | Default time window (milliseconds) |

### Obtaining Instana API Credentials

1. Log in to your Instana instance
2. Navigate to **Settings → API Tokens**
3. Create a new API token with **read permissions**
4. Copy the token to your `.env` file

---

## 📖 Usage

### Dashboard Overview

The dashboard displays comprehensive observability metrics for your application:

#### Summary Cards
- **Services**: Total number of services monitored
- **Total Calls**: Aggregate API call volume
- **Avg Error Rate**: Average error percentage across services
- **Avg Latency**: Average response time
- **Health Score**: Composite health indicator (0-100)

#### Service Health Chart
- Bar chart showing call volume per service
- Color-coded by health score:
  - 🟢 Green (80-100): Healthy
  - 🟡 Yellow (60-79): Warning
  - 🟠 Orange (40-59): Degraded
  - 🔴 Red (0-39): Critical

#### Error Rate Chart
- Services with highest error rates
- Helps identify problematic services quickly

#### Latency Chart
- Services with highest response times
- Color-coded by latency thresholds:
  - 🟢 < 100ms: Excellent
  - 🟡 100-500ms: Good
  - 🟠 500-1000ms: Slow
  - 🔴 > 1000ms: Critical

#### Service Details Table
- Comprehensive service metrics
- Sortable columns
- Health status badges

### Refreshing Data

Click the **🔄 Refresh Data** button to fetch the latest metrics from Instana.

### Interpreting Health Scores

**Health Score Calculation** (0-100):
- **Error Rate**: 40% weight (lower is better)
- **Latency**: 30% weight (lower is better)
- **Call Volume**: 30% weight (higher indicates activity)

**Health Status**:
- 🟢 **80-100**: Healthy - All systems operational
- 🟡 **60-79**: Warning - Minor issues detected
- 🟠 **40-59**: Degraded - Performance issues
- 🔴 **0-39**: Critical - Immediate attention required

---

## 📁 Project Structure

```
/
├── src/                          # Source code
│   ├── app.py                    # Main application
│   ├── config.py                 # Configuration management
│   ├── utils/                    # Utilities
│   │   ├── logger.py             # Logging
│   │   └── helpers.py            # Helper functions
│   ├── integrations/             # API clients
│   │   └── instana_integration.py
│   ├── components/               # UI components
│   │   └── dashboard.py
│   └── assets/                   # Static files
│       └── custom.css            # Custom styling
├── scripts/                      # Automation scripts
│   ├── setup.sh                  # Unix setup
│   ├── setup.bat                 # Windows setup
│   ├── run.sh                    # Unix run
│   └── run.bat                   # Windows run
├── docs/                         # Documentation
├── tests/                        # Test suite
├── requirements.txt              # Dependencies
├── .env.example                  # Config template
└── README.md                     # This file
```

---

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start

**Problem**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Unix/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### API Connection Errors

**Problem**: "Unable to connect to Instana API"

**Solution**:
1. Verify API credentials in `.env` file
2. Check network connectivity to Instana
3. Ensure API token has correct permissions
4. Review logs in console for details

#### No Data Displayed

**Problem**: Dashboard loads but shows no data

**Solution**:
1. Verify `INSTANA_APPLICATION_NAME` matches actual application name in Instana
2. Check that the application exists and has data
3. Ensure API token has read permissions
4. Check browser console for JavaScript errors

#### Port Already in Use

**Problem**: "Address already in use" error

**Solution**:
```bash
# Change port in .env file
APP_PORT=8051

# Or kill process using port 8050
# Unix/Mac:
lsof -ti:8050 | xargs kill -9

# Windows:
netstat -ano | findstr :8050
taskkill /PID <PID> /F
```

---

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ./scripts/setup.sh
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # Unix/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies:**
   ```bash
   pip install pytest pytest-cov black flake8
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_instana.py
```

### Code Style

This project follows PEP 8 style guidelines:

```bash
# Format code
black src/

# Check style
flake8 src/
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Update documentation as needed
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IBM Instana** - Application Performance Monitoring
- **Plotly Dash** - Interactive web application framework
- **Dash Bootstrap Components** - Modern UI components

---

## 📞 Support

For questions, issues, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: See [docs/](docs/) directory

---

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Real-time service health monitoring
- ✅ Error rate and latency tracking
- ✅ Interactive visualizations
- ✅ Configurable application targeting

### Future Enhancements (v2.0)
- 🔄 Real-time updates via WebSocket
- 📊 Historical data analysis and trending
- 🔔 Email/Slack alerting
- 🎨 Custom dashboard layouts
- 📱 Mobile-responsive design improvements
- 🔐 User authentication
- 📈 Advanced analytics
- 🐳 Docker containerization

---

<div align="center">

**Built with ❤️ using Python, Dash, and IBM Instana**

[⬆ Back to Top](#instana-observability-dashboard)

</div>