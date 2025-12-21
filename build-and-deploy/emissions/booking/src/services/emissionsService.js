// Envizi Emissions API Service
// API Documentation: https://developer.ibm.com/apis/catalog/ghgemissions--ibm-envizi-emissions-api

// IBM Envizi API credentials from environment
// Note: These are checked on the frontend to determine if API is configured,
// but actual values are only used server-side in the proxy
const ENVIZI_API_KEY = process.env.REACT_APP_ENVIZI_API_KEY; // Keep REACT_APP_ for frontend check
const ENVIZI_TENANT_ID = process.env.REACT_APP_ENVIZI_TENANT_ID;
const ENVIZI_ORGANIZATION_ID = process.env.REACT_APP_ENVIZI_ORGANIZATION_ID;
const ENVIZI_API_URL = process.env.REACT_APP_ENVIZI_API_URL;

// Airport coordinates for distance calculation
const AIRPORT_COORDINATES = {
  'ATL': { lat: 33.6407, lon: -84.4277 },
  'LAX': { lat: 33.9416, lon: -118.4085 },
  'ORD': { lat: 41.9742, lon: -87.9073 },
  'DFW': { lat: 32.8998, lon: -97.0403 },
  'DEN': { lat: 39.8561, lon: -104.6737 },
  'JFK': { lat: 40.6413, lon: -73.7781 },
  'SFO': { lat: 37.6213, lon: -122.3790 },
  'SEA': { lat: 47.4502, lon: -122.3088 },
  'LAS': { lat: 36.0840, lon: -115.1537 },
  'MCO': { lat: 28.4312, lon: -81.3081 },
  'EWR': { lat: 40.6895, lon: -74.1745 },
  'PHX': { lat: 33.4346, lon: -112.0080 },
  'IAH': { lat: 29.9902, lon: -95.3368 },
  'MIA': { lat: 25.7959, lon: -80.2870 },
  'CLT': { lat: 35.2144, lon: -80.9473 },
  'BOS': { lat: 42.3656, lon: -71.0096 },
  'MSP': { lat: 44.8848, lon: -93.2223 },
  'DTW': { lat: 42.2162, lon: -83.3554 },
  'FLL': { lat: 26.0742, lon: -80.1506 },
  'LGA': { lat: 40.7769, lon: -73.8740 },
  'PHL': { lat: 39.8729, lon: -75.2437 },
  'SAN': { lat: 32.7336, lon: -117.1897 },
  'DCA': { lat: 38.8512, lon: -77.0402 },
  'IAD': { lat: 38.9531, lon: -77.4565 },
  'TPA': { lat: 27.9772, lon: -82.5332 },
  'PDX': { lat: 45.5898, lon: -122.5951 },
  'STL': { lat: 38.7499, lon: -90.3695 },
  'BWI': { lat: 39.1774, lon: -76.6684 },
  'MDW': { lat: 41.7868, lon: -87.7522 },
  'BNA': { lat: 36.1263, lon: -86.6774 },
  'AUS': { lat: 30.1975, lon: -97.6664 },
  'HNL': { lat: 21.3187, lon: -157.9225 },
  'DAL': { lat: 32.8470, lon: -96.8517 },
  'SJC': { lat: 37.3626, lon: -121.9290 },
  'OAK': { lat: 37.7126, lon: -122.2197 },
  'MCI': { lat: 39.2976, lon: -94.7139 },
  'SLC': { lat: 40.7899, lon: -111.9791 },
  'RDU': { lat: 35.8801, lon: -78.7880 },
  'SNA': { lat: 33.6762, lon: -117.8681 },
  'SAT': { lat: 29.5337, lon: -98.4698 }
};

/**
 * Calculate distance between two airports using Haversine formula
 * @param {string} fromCode - Origin airport code
 * @param {string} toCode - Destination airport code
 * @returns {number} Distance in kilometers
 */
export const calculateDistance = (fromCode, toCode) => {
  // Extract airport codes from formatted strings like "San Francisco, CA (SFO)"
  const extractCode = (str) => {
    const match = str.match(/\(([A-Z]{3})\)/);
    return match ? match[1] : str;
  };

  const from = extractCode(fromCode);
  const to = extractCode(toCode);

  const coord1 = AIRPORT_COORDINATES[from];
  const coord2 = AIRPORT_COORDINATES[to];

  if (!coord1 || !coord2) {
    // Default distance if coordinates not found
    return 1000;
  }

  const R = 6371; // Earth's radius in kilometers
  const dLat = toRadians(coord2.lat - coord1.lat);
  const dLon = toRadians(coord2.lon - coord1.lon);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(coord1.lat)) *
    Math.cos(toRadians(coord2.lat)) *
    Math.sin(dLon / 2) *
    Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return Math.round(distance);
};

const toRadians = (degrees) => {
  return degrees * (Math.PI / 180);
};

/**
 * Check if Envizi API is configured
 * @returns {boolean} True if API key and required credentials are configured
 */
export const isApiConfigured = () => {
  return !!(
    ENVIZI_API_KEY &&
    ENVIZI_TENANT_ID &&
    ENVIZI_ORGANIZATION_ID &&
    ENVIZI_API_URL &&
    ENVIZI_API_KEY.length >= 5  // Just check it's not empty
  );
};

/**
 * Calculate emissions using Envizi API
 * @param {string} fromCode - Origin airport code
 * @param {string} toCode - Destination airport code
 * @param {string} flightClass - Flight class (Economy, Business, First)
 * @param {number} passengers - Number of passengers
 * @returns {Promise<Object>} Emissions data
 * @throws {Error} If API key is not configured or API call fails
 */
export const calculateEmissions = async (fromCode, toCode, flightClass = 'Economy', passengers = 1) => {
  // Check if API credentials are configured
  if (!isApiConfigured()) {
    throw new Error(
      'Envizi API credentials are not configured. ' +
      'Please set the required environment variables in your .env file. ' +
      'See .env file for configuration details.'
    );
  }

  const distance = calculateDistance(fromCode, toCode);

  try {
    // Use local proxy server to avoid CORS issues
    const PROXY_URL = process.env.REACT_APP_PROXY_URL || 'http://localhost:3001';

    const response = await fetch(`${PROXY_URL}/api/emissions/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        fromCode: fromCode,
        toCode: toCode,
        flightClass: flightClass,
        passengers: passengers,
        distance: distance
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      // Check for authentication errors
      if (response.status === 401 || response.status === 403) {
        throw new Error(
          'Authentication error: Unable to authenticate with Envizi API. ' +
          'Please check your API key and credentials in the .env file. ' +
          'The proxy server will automatically retry with a new token.'
        );
      }

      throw new Error(`API error: ${response.status} - ${errorData.message || errorData.error || response.statusText}`);
    }

    const data = await response.json();

    // Handle new response format from proxy
    // data.totalCO2e = total for all passengers
    // data.perPassenger = per passenger CO2e
    const co2Total = data.totalCO2e || data.co2 || 0;
    const co2PerPassenger = data.perPassenger || (co2Total / passengers);

    return {
      co2: co2Total,
      co2PerPassenger: co2PerPassenger,
      distance: distance,
      source: 'envizi-api',
      // Include additional emissions data if available
      CO2: data.CO2,
      CH4: data.CH4,
      N2O: data.N2O,
      indirectCO2e: data.indirectCO2e,
      description: data.description,
      transactionId: data.transactionId
    };
  } catch (error) {
    // Re-throw API configuration errors
    if (error.message.includes('Envizi API credentials') || error.message.includes('Authentication error')) {
      throw error;
    }

    // Handle network errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error(
        'Network error: Unable to connect to proxy server. ' +
        'Please ensure: (1) The proxy server is running (npm run start:proxy), ' +
        '(2) Your internet connection is active, ' +
        '(3) The API endpoint URL is correct in your .env file.'
      );
    }

    throw new Error(`Failed to calculate emissions: ${error.message}`);
  }
};

/**
 * Get sustainability rating based on emissions
 * @param {number} co2 - CO2 emissions in kg
 * @param {number} distance - Distance in km
 * @returns {Object} Rating information
 */
export const getSustainabilityRating = (co2, distance) => {
  const emissionsPerKm = co2 / distance;

  if (emissionsPerKm < 0.12) {
    return {
      rating: 'Excellent',
      color: 'green',
      icon: '🌱',
      description: 'Very low emissions'
    };
  } else if (emissionsPerKm < 0.18) {
    return {
      rating: 'Good',
      color: 'lime',
      icon: '✓',
      description: 'Below average emissions'
    };
  } else if (emissionsPerKm < 0.25) {
    return {
      rating: 'Average',
      color: 'yellow',
      icon: '●',
      description: 'Average emissions'
    };
  } else {
    return {
      rating: 'High',
      color: 'orange',
      icon: '⚠',
      description: 'Above average emissions'
    };
  }
};

/**
 * Calculate carbon offset cost
 * @param {number} co2 - CO2 emissions in kg
 * @returns {number} Cost in USD
 */
export const calculateCarbonOffsetCost = (co2) => {
  // Average carbon offset price: $15-25 per tonne of CO2
  const pricePerTonne = 20;
  const tonnes = co2 / 1000;
  return Math.round(tonnes * pricePerTonne * 100) / 100;
};
