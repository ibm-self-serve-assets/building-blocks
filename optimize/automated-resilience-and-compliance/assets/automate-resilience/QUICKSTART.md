# Quick Start Guide

Get the IBM Concert Insights Dashboard up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher installed
- IBM Concert API credentials (Base URL, API Key, Instance ID)

## Step 1: Setup

Choose your platform:

### macOS/Linux
```bash
./setup_and_run.sh
```

### Windows
```cmd
setup_and_run.bat
```

The script will automatically:
- Create a virtual environment
- Install dependencies
- Create `.env` file from template
- Prompt you to configure credentials

## Step 2: Configure Credentials

Edit the `.env` file with your IBM Concert credentials:

```env
CONCERT_BASE_URL=https://your-concert-instance.ibm.com
C_API_KEY=your_api_key_here
INSTANCE_ID=your_instance_id_here
```

**Important**: 
- Remove trailing slash from `CONCERT_BASE_URL`
- Enter only the API key value in `C_API_KEY` (the "C_API_KEY" prefix is added automatically)

## Step 3: Test Connection (Optional)

Verify your API connection before launching the dashboard:

```bash
python test_api_connection.py
```

This will test all three endpoints (CVEs, Applications, Certificates) and display sample data structures.

## Step 4: Launch Dashboard

If you used the setup script, the dashboard should already be running. Otherwise:

```bash
python app.py
```

## Step 5: Access Dashboard

Open your browser to:
```
http://127.0.0.1:8050
```

## Using the Dashboard

### CVE Insights Tab
1. Click "Load CVE Data" button
2. View statistics cards (Total CVEs, Critical, High, Average Risk Score)
3. Explore interactive charts:
   - Severity distribution
   - Risk score histogram
   - Top 10 highest risk CVEs
   - Priority distribution
4. Browse detailed CVE table with sorting and filtering

### Applications Tab
1. Click "Load Applications" button
2. View portfolio overview with analytics:
   - Total applications and vulnerabilities
   - Status distribution
   - Vulnerability ranges
   - Build artifact correlation
3. Click any application row to drill down:
   - View application-specific CVE analytics
   - Explore build artifacts
4. Click any artifact row to view:
   - Artifact-specific CVE details
   - Compare vulnerabilities across builds

### Certificates Tab
1. Click "Load Certificates" button
2. View certificate statistics:
   - Total certificates
   - Valid certificates
   - Expiring soon (30 days)
   - Expired certificates
3. Explore visualizations:
   - Status distribution
   - Expiry timeline
   - Algorithm distribution
   - Key size analysis
   - Top 10 expiring certificates
4. Review certificate table with expiry alerts:
   - Red: Expired or ≤7 days
   - Yellow: 8-30 days
   - Green: Valid

## Troubleshooting

### "Configuration validation failed"
- Ensure all three required variables are set in `.env`
- Check for typos in variable names

### "Authentication failed"
- Verify `C_API_KEY` is correct
- Ensure you entered only the key value (not the "C_API_KEY" prefix)

### "Access forbidden"
- Verify `INSTANCE_ID` matches your IBM Concert instance
- Check with your IBM Concert administrator

### "Module not found"
- Activate virtual environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
- Reinstall dependencies: `pip install -r requirements.txt`

### "Port already in use"
- Change `PORT` in `.env` to a different value (e.g., 8051)
- Or stop the process using port 8050

## Next Steps

- Review [`README.md`](README.md) for detailed documentation
- Check `logs/app.log` for application logs
- Explore the codebase to customize visualizations
- Add new features by extending the modular architecture

## Support

For issues:
1. Check `logs/app.log` for error details
2. Run `python test_api_connection.py` to diagnose API issues
3. Review the [README.md](README.md) troubleshooting section
4. Contact IBM Concert support for API-related issues

## Tips

- **Refresh Data**: Click the load button again to refresh data
- **Filter Tables**: Use the filter boxes above each column
- **Sort Data**: Click column headers to sort
- **Export Data**: Use browser tools to export table data
- **Zoom Charts**: Click and drag on charts to zoom in
- **Reset View**: Double-click charts to reset zoom

Enjoy exploring your IBM Concert data! 🚀