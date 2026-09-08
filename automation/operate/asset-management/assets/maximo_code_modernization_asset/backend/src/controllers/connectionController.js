const axios = require('axios');
const https = require('https');

class ConnectionController {
  /**
   * Test Maximo connection
   */
  async testConnection(req, res) {
    try {
      const { maximoUrl, apiKey, username } = req.body;

      if (!maximoUrl || !apiKey) {
        return res.status(400).json({
          success: false,
          message: 'Maximo URL and API Key are required'
        });
      }

      // Create axios instance for testing
      const axiosInstance = axios.create({
        httpsAgent: new https.Agent({
          rejectUnauthorized: false
        }),
        timeout: 15000
      });

      // Test endpoint - try to fetch a small number of scripts
      const testUrl = `${maximoUrl}/maximo/api/os/MXAPIAUTOSCRIPT?oslc.pageSize=1&oslc.select=autoscript`;
      
      console.log('Testing connection to:', testUrl);

      const response = await axiosInstance.get(testUrl, {
        headers: {
          'apikey': apiKey,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      // Check if we got a valid response
      let scriptsFound = 0;
      if (response.data) {
        if (response.data.member && Array.isArray(response.data.member)) {
          scriptsFound = response.data.member.length;
        } else if (Array.isArray(response.data)) {
          scriptsFound = response.data.length;
        }
      }

      res.json({
        success: true,
        message: 'Connection successful! Maximo instance is reachable.',
        scriptsFound: scriptsFound,
        responseStatus: response.status
      });

    } catch (error) {
      console.error('Connection test failed:', error.message);
      
      let errorMessage = 'Connection failed';
      let statusCode = 500;

      if (error.code === 'ECONNREFUSED') {
        errorMessage = 'Connection refused. Please check the Maximo URL.';
      } else if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
        errorMessage = 'Connection timeout. The server is not responding.';
      } else if (error.response) {
        statusCode = error.response.status;
        if (statusCode === 401) {
          errorMessage = 'Authentication failed. Please check your API key.';
        } else if (statusCode === 403) {
          errorMessage = 'Access forbidden. You may not have permission to access this resource.';
        } else if (statusCode === 404) {
          errorMessage = 'Endpoint not found. Please verify the Maximo URL.';
        } else {
          errorMessage = error.response.data?.message || error.message;
        }
      } else {
        errorMessage = error.message;
      }

      res.status(statusCode).json({
        success: false,
        message: errorMessage,
        error: process.env.NODE_ENV === 'development' ? error.message : undefined
      });
    }
  }
}

module.exports = new ConnectionController();

// Made with Bob