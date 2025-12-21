# Getting Started with Flywise App

A modern flight booking application built with React and Tailwind CSS, now featuring comprehensive emissions tracking powered by IBM Envizi Emissions API.

## Variable Reference

### Server-Side

These are used by `server.js` (the proxy server):

| Variable | Purpose | Example |
|----------|---------|---------|
| `ENVIZI_API_KEY` | API key for authentication | `PHXEz1t3r4...` |
| `ENVIZI_TENANT_ID` | Your tenant ID | `a8cea08c-...` |
| `ENVIZI_ORGANIZATION_ID` | Your organization ID | `8306d85d-...` |
| `ENVIZI_API_URL` | Emissions API base URL | `https://api.ibm.com/ghgemissions/run/v3/carbon` |
| `ENVIZI_AUTH_URL` | Authentication API URL | `https://api.ibm.com/saascore/run/authentication-retrieve/api-key` |
| `ENVIZI_CLIENT_ID` | Client ID for emissions API | `ghgemissions-{TENANT_ID}` |
| `ENVIZI_AUTH_CLIENT_ID` | Client ID for auth API | `saascore-{TENANT_ID}` |
| `ENVIZI_FACTOR_ID_ECONOMY` | Emissions factor ID for economy class | `168943` |

### Frontend Check Only (REACT_APP_ prefix)

These are used by `src/services/emissionsService.js` to check if API is configured:

| Variable | Purpose | Value |
|----------|---------|-------|
| `REACT_APP_ENVIZI_API_KEY` | Frontend check flag | `configured` |
| `REACT_APP_ENVIZI_TENANT_ID` | Frontend check flag | `configured` |
| `REACT_APP_ENVIZI_ORGANIZATION_ID` | Frontend check flag | `configured` |
| `REACT_APP_ENVIZI_API_URL` | Frontend check flag | `configured` |

**Note**: The frontend variables should just be set to `"configured"` - they don't need the actual credential values.

## Available Scripts

```bash
npm run start:all
```

This will start:
- **Proxy server** on `http://localhost:3001`
- **React app** on `http://localhost:3000`

Note: The IBM Envizi API doesn't allow direct browser requests from localhost due to CORS restrictions. Hence, a proxy server runs locally to forward requests to the Envizi API, bypassing CORS restrictions.


## Verify It's Working

1. **Check proxy server** - You should see:
   ```
   ✓ Proxy server running on http://localhost:3001
   ✓ Flywise app should run on http://localhost:3000
   ✓ API proxy endpoint: http://localhost:3001/api/emissions/calculate
   ```

2. **Check Flywise app** - Orange warning banner should appear if API key is not configured

3. **Test emissions calculation**:
   - Search for a flight (e.g., LAX to JFK)
   - Blue loading indicator should appear
   - Flights should display with emissions data

4. **Check proxy server logs**:

You should see:
```
📡 Making request to Envizi API:
   URL: https://api.ibm.com/ghgemissions/run/v3/carbon/transportation-and-distribution?value=2548&unit=mi&factorId=168943
   Method: GET
   Distance: 4100 km (2548 mi)
   Class: Economy
   Passengers: 1
   Factor ID: 168943

✅ Success! Emissions calculated:
   Per trip: 409.29 kg CO2e
   For 1 passenger(s): 409.29 kg CO2e
```




