// Proxy server for Envizi API to avoid CORS issues
const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for React app
app.use(cors());
app.use(express.json());

// Token cache
let cachedToken = null;
let tokenExpiration = null;

/**
 * Generate a new bearer token using API key
 * @returns {Promise<string>} Bearer token
 */
async function getBearerToken() {
  // Check if we have a valid cached token
  if (cachedToken && tokenExpiration && Date.now() < tokenExpiration) {
    console.log('✓ Using cached bearer token');
    return cachedToken;
  }

  console.log('🔑 Generating new bearer token...');

  const apiKey = process.env.ENVIZI_API_KEY;
  const tenantId = process.env.ENVIZI_TENANT_ID;
  const orgId = process.env.ENVIZI_ORGANIZATION_ID;
  const authUrl = process.env.ENVIZI_AUTH_URL;

  if (!apiKey || !tenantId || !orgId) {
    throw new Error('Missing required environment variables for authentication');
  }

  // Construct auth client ID: "saascore-" + TENANT_ID
  const authClientId = `saascore-${tenantId}`;

  const authEndpoint = `${authUrl}?orgId=${orgId}`;

  try {
    const response = await fetch(authEndpoint, {
      method: 'GET',
      headers: {
        'X-Api-Key': apiKey,
        'X-IBM-Client-Id': authClientId,
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Auth API error ${response.status}: ${errorText}`);
    }

    // The API returns the JWT token directly as plain text, not JSON
    const token = await response.text();

    if (!token || token.length < 20) {
      throw new Error('Invalid or empty token received from authentication API');
    }

    // Validate that it looks like a JWT token (should start with "eyJ")
    if (!token.startsWith('eyJ')) {
      throw new Error(`Unexpected token format received: ${token.substring(0, 50)}...`);
    }

    // Cache the token
    cachedToken = token.trim();

    // JWT tokens typically expire in 1-2 hours
    // We'll refresh after 55 minutes to be safe
    const expiresInSeconds = 3600; // 1 hour
    tokenExpiration = Date.now() + ((expiresInSeconds - 300) * 1000); // Refresh 5 min early

    console.log(`✅ Bearer token generated successfully`);
    console.log(`   Token: ${token.substring(0, 20)}...`);
    console.log(`   Will refresh in: ${Math.round((expiresInSeconds - 300) / 60)} minutes`);

    return cachedToken;

  } catch (error) {
    console.error(' Failed to generate bearer token:', error.message);
    throw error;
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Proxy endpoint for emissions calculation
app.post('/api/emissions/calculate', async (req, res) => {
  try {
    const { fromCode, toCode, flightClass, passengers, distance } = req.body;

    // Get API credentials from environment
    const apiUrl = process.env.ENVIZI_API_URL;
    const clientId = process.env.ENVIZI_CLIENT_ID;

    if (!apiUrl || !clientId) {
      return res.status(500).json({
        error: 'API configuration missing',
        message: 'ENVIZI_API_URL and ENVIZI_CLIENT_ID are required'
      });
    }

    // Get or generate bearer token
    let bearerToken;
    try {
      bearerToken = await getBearerToken();
    } catch (error) {
      return res.status(500).json({
        error: 'Authentication failed',
        message: error.message
      });
    }

    // Determine factor ID based on flight class
    const factorId = process.env.ENVIZI_FACTOR_ID_ECONOMY || '168943';

    // Convert distance to miles (API expects miles)
    const distanceInMiles = Math.round(distance * 0.621371);

    // Build URL with query parameters
    const fullUrl = `${apiUrl}/transportation-and-distribution?value=${distanceInMiles}&unit=mi&factorId=${factorId}`;

    console.log(`\n📡 Making request to Envizi API:`);
    console.log(`   URL: ${fullUrl}`);
    console.log(`   Method: GET`);
    console.log(`   Distance: ${distance} km (${distanceInMiles} mi)`);
    console.log(`   Class: ${flightClass}`);
    console.log(`   Passengers: ${passengers}`);
    console.log(`   Factor ID: ${factorId}`);

    // Make GET request to Envizi API
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'X-IBM-Client-Id': clientId,
        'Authorization': `Bearer ${bearerToken}`
      }
    });

    // Check if request was successful
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`\n Envizi API Error ${response.status}:`);
      console.error(`   Response: ${errorText}`);

      if (response.status === 404) {
        console.error(`\n404 Error - Endpoint not found!`);
        console.error(`   The URL might be incorrect: ${fullUrl}`);
        console.error(`   Check your .env file and IBM API documentation\n`);
      }

      if (response.status === 401 || response.status === 403) {
        console.error(`\n Authentication Error!`);
        console.error(`   Clearing cached token and will retry on next request\n`);
        // Clear cached token so it regenerates on next request
        cachedToken = null;
        tokenExpiration = null;
      }

      return res.status(response.status).json({
        error: 'Envizi API error',
        status: response.status,
        message: errorText,
        endpoint: fullUrl
      });
    }

    // Parse the response
    const data = await response.json();

    // API returns emissions for single trip, multiply by number of passengers
    const totalCO2e = data.totalCO2e * passengers;

    console.log(`✅ Success! Emissions calculated:`);
    console.log(`   Per trip: ${data.totalCO2e} kg CO2e`);
    console.log(`   For ${passengers} passenger(s): ${totalCO2e} kg CO2e\n`);

    // Return response in format expected by frontend
    res.json({
      totalCO2e: totalCO2e,
      perPassenger: data.totalCO2e,
      CO2: data.CO2,
      CH4: data.CH4,
      N2O: data.N2O,
      indirectCO2e: data.indirectCO2e,
      unit: data.unit,
      description: data.description,
      transactionId: data.transactionId
    });

  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({
      error: 'Proxy server error',
      message: error.message
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`✓ Proxy server running on http://localhost:${PORT}`);
  console.log(`✓ React app should run on http://localhost:3000`);
  console.log(`✓ API proxy endpoint: http://localhost:${PORT}/api/emissions/calculate`);
  console.log(`✓ Bearer tokens will be generated automatically as needed`);
});
