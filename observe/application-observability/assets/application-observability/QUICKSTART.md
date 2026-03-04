# Quick Start Guide - Instana Observability Dashboard

This guide will help you get the Instana Observability Dashboard up and running in minutes.

## Prerequisites

- Python 3.8 or higher installed
- Instana API credentials (base URL and API token)
- Access to the finvault application in Instana

## Installation Steps

### Step 1: Setup

**On macOS/Linux:**
```bash
./scripts/setup.sh
```

**On Windows:**
```cmd
scripts\setup.bat
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` configuration file

### Step 2: Configure

Edit the `.env` file with your Instana credentials:

```bash
# Required Configuration
INSTANA_BASE_URL=https://your-instana-instance.com
INSTANA_API_TOKEN=your_api_token_here
INSTANA_APPLICATION_NAME=finvault
```

**How to get your Instana API token:**
1. Log in to your Instana instance
2. Go to Settings → API Tokens
3. Create a new token with read permissions
4. Copy the token value

### Step 3: Run

**On macOS/Linux:**
```bash
./scripts/run.sh
```

**On Windows:**
```cmd
scripts\run.bat
```

### Step 4: Access

Open your browser and go to:
```
http://localhost:8050
```

## What You'll See

The dashboard displays:

1. **Summary Cards** - Key metrics at a glance
   - Total services
   - Call volume
   - Error rates
   - Latency
   - Health score

2. **Service Health Chart** - Bar chart of service call volumes

3. **Error Rate Chart** - Services with highest error rates

4. **Latency Chart** - Services with highest response times

5. **Service Details Table** - Comprehensive metrics for all services

## Troubleshooting

### "Application not found" error

**Problem:** The dashboard shows "Application 'finvault' not found"

**Solution:**
1. Check that the application name in `.env` matches exactly (case-sensitive)
2. Verify the application exists in your Instana instance
3. Ensure your API token has access to this application

### "Unable to connect" error

**Problem:** Cannot connect to Instana API

**Solution:**
1. Verify `INSTANA_BASE_URL` is correct (include https://)
2. Check your network connection
3. Ensure the API token is valid and not expired
4. Verify firewall settings allow outbound connections

### No data displayed

**Problem:** Dashboard loads but shows empty charts

**Solution:**
1. Ensure the finvault application has recent activity
2. Check that services are reporting to Instana
3. Verify the time window (default is last 1 hour)
4. Click the "Refresh Data" button

### Port already in use

**Problem:** Error message about port 8050 being in use

**Solution:**
Change the port in `.env`:
```bash
APP_PORT=8051
```

## Next Steps

- **Customize**: Edit `.env` to monitor different applications
- **Explore**: Click on charts for interactive features
- **Refresh**: Use the refresh button to get latest data
- **Monitor**: Set up regular monitoring schedules

## Getting Help

- Check the full [README.md](README.md) for detailed documentation
- Review logs in the console for error details
- Ensure all prerequisites are met

## Configuration Options

### Optional Settings

You can customize these in `.env`:

```bash
# Server Configuration
APP_HOST=0.0.0.0          # Server host
APP_PORT=8050             # Server port
DEBUG_MODE=False          # Enable debug mode

# Logging
LOG_LEVEL=INFO            # DEBUG, INFO, WARNING, ERROR

# Data Settings
DEFAULT_TIMEFRAME=3600000 # Time window in milliseconds (1 hour)
REQUEST_TIMEOUT=30        # API request timeout in seconds
MAX_RETRIES=3             # Number of retry attempts
```

## Health Score Interpretation

The health score (0-100) is calculated based on:
- **40%** - Error rate (lower is better)
- **30%** - Latency (lower is better)
- **30%** - Call volume (higher indicates activity)

**Score Ranges:**
- 🟢 **80-100**: Healthy
- 🟡 **60-79**: Warning
- 🟠 **40-59**: Degraded
- 🔴 **0-39**: Critical

---

**Ready to monitor your applications!** 🚀