import React, { useState, useEffect } from 'react';
import FlightSearch from './components/FlightSearch';
import FlightList from './components/FlightList';
import BookingForm from './components/BookingForm';
import { calculateEmissions, getSustainabilityRating, calculateCarbonOffsetCost, isApiConfigured } from './services/emissionsService';

// Sample flight data with emissions
const generateFlights = async (searchData) => {
  const airlines = ['Delta', 'United', 'American', 'Southwest', 'JetBlue'];
  const aircraftTypes = ['Boeing 737', 'Airbus A320', 'Boeing 787', 'Airbus A350', 'Boeing 777'];
  const flights = [];

  // Calculate emissions for each flight
  const emissionsPromises = [];

  for (let i = 0; i < 5; i++) {
    const basePrice = Math.floor(Math.random() * 300) + 200;
    const departHour = Math.floor(Math.random() * 12) + 6;
    const duration = Math.floor(Math.random() * 3) + 2;
    const arrivalHour = (departHour + duration) % 24;
    const flightClass = 'Economy';

    // Calculate emissions for this route
    const emissionsPromise = calculateEmissions(
      searchData.from,
      searchData.to,
      flightClass,
      1 // per passenger
    );

    emissionsPromises.push(emissionsPromise);

    flights.push({
      id: i + 1,
      airline: airlines[i % airlines.length],
      flightNumber: `${airlines[i % airlines.length].substring(0, 2).toUpperCase()}${Math.floor(Math.random() * 9000) + 1000}`,
      aircraft: aircraftTypes[i % aircraftTypes.length],
      from: searchData.from,
      to: searchData.to,
      departureTime: `${departHour.toString().padStart(2, '0')}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`,
      arrivalTime: `${arrivalHour.toString().padStart(2, '0')}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`,
      duration: `${duration}h ${Math.floor(Math.random() * 60)}m`,
      stops: Math.random() > 0.5 ? 'Nonstop' : '1 Stop',
      price: basePrice,
      baggage: '1 Carry-on, 1 Checked bag',
      class: flightClass
    });
  }

  // Wait for all emissions calculations
  const emissionsResults = await Promise.all(emissionsPromises);

  // Add emissions data to flights with some variation
  flights.forEach((flight, index) => {
    const baseEmissions = emissionsResults[index];
    // Add some variation based on aircraft efficiency and stops
    const variation = flight.stops === 'Nonstop' ? 1.0 : 1.15; // Non-stop flights are more efficient
    const aircraftEfficiency = 0.9 + Math.random() * 0.2; // 0.9-1.1 efficiency factor

    const adjustedCO2 = baseEmissions.co2PerPassenger * variation * aircraftEfficiency;
    const totalCO2 = adjustedCO2 * searchData.passengers;

    flight.emissions = {
      co2PerPassenger: Math.round(adjustedCO2 * 100) / 100,
      co2Total: Math.round(totalCO2 * 100) / 100,
      distance: baseEmissions.distance,
      rating: getSustainabilityRating(adjustedCO2, baseEmissions.distance),
      offsetCost: calculateCarbonOffsetCost(totalCO2)
    };
  });

  // Sort by price by default
  return flights.sort((a, b) => a.price - b.price);
};

function App() {
  const [searchData, setSearchData] = useState(null);
  const [flights, setFlights] = useState([]);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [bookingConfirmed, setBookingConfirmed] = useState(false);
  const [bookingDetails, setBookingDetails] = useState(null);
  const [apiConfigured, setApiConfigured] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if API is configured on mount
    setApiConfigured(isApiConfigured());
  }, []);

  const handleSearch = async (data) => {
    setSearchData(data);
    setFlights([]); // Clear previous flights while loading
    setError(null);
    setLoading(true);

    try {
      const newFlights = await generateFlights(data);
      setFlights(newFlights);
      setSelectedFlight(null);
      setBookingConfirmed(false);
    } catch (err) {
      setError(err.message);
      console.error('Error generating flights:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectFlight = (flight) => {
    setSelectedFlight(flight);
  };

  const handleCancelBooking = () => {
    setSelectedFlight(null);
  };

  const handleConfirmBooking = (details) => {
    setBookingDetails(details);
    setBookingConfirmed(true);
    setSelectedFlight(null);
  };

  const handleNewSearch = () => {
    setSearchData(null);
    setFlights([]);
    setSelectedFlight(null);
    setBookingConfirmed(false);
    setBookingDetails(null);
  };

  return (
    <div className="min-h-screen bg-cover bg-center bg-no-repeat relative" style={{ backgroundImage: 'url(/sail.jpg)' }}>
      <div className="min-h-screen bg-black bg-opacity-40">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-12">
            <div className="flex items-center justify-center mb-0">
              <img
                src="/flywise.png"
                alt="Flywise"
                className="h-16 md:h-20 w-auto mr-2"
              />
              <h1 className="text-4xl md:text-5xl font-bold text-white">
                Flywise
              </h1>
            </div>
            <p className="text-white text-lg font-light">Your Greener Way to Fly</p>
          </header>

          {/* API Configuration Warning */}
          {!apiConfigured && (
            <div className="max-w-4xl mx-auto mb-6 bg-orange-100 border-l-4 border-orange-500 text-orange-800 p-4 rounded">
              <div className="flex items-start">
                <svg className="w-6 h-6 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <h3 className="font-semibold mb-1">Envizi API Key Required</h3>
                  <p className="text-sm mb-2">
                    The emissions tracking feature requires an IBM Envizi API key to be configured.
                  </p>
                  <div className="text-sm space-y-1">
                    <p><strong>To configure:</strong></p>
                    <ol className="list-decimal ml-5 space-y-1">
                      <li>Create a <code className="bg-orange-200 px-1">.env</code> file in the project root</li>
                      <li>Add: <code className="bg-orange-200 px-1">REACT_APP_ENVIZI_API_KEY=your_api_key</code></li>
                      <li>Restart the development server</li>
                    </ol>
                    <p className="mt-2">
                      <strong>Don't have an API key?</strong> Sign up at:{' '}
                      <a
                        href="https://www.ibm.com/account/reg/us-en/signup?formid=urx-53999"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline hover:text-orange-900"
                      >
                        IBM Envizi API Portal
                      </a>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="max-w-4xl mx-auto mb-6 bg-red-100 border-l-4 border-red-500 text-red-800 p-4 rounded">
              <div className="flex items-start">
                <svg className="w-6 h-6 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <div>
                  <h3 className="font-semibold mb-1">Error</h3>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Loading Indicator */}
          {loading && (
            <div className="max-w-4xl mx-auto mb-6 bg-blue-100 border-l-4 border-blue-500 text-blue-800 p-4 rounded">
              <div className="flex items-center">
                <svg className="animate-spin h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Calculating emissions using Envizi API...</span>
              </div>
            </div>
          )}

        {bookingConfirmed ? (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <div className="mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
                  <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-3xl font-bold text-gray-800 mb-2">Booking Confirmed!</h2>
                <p className="text-gray-600">Your flight has been successfully booked.</p>
              </div>

              <div className="bg-gray-50 rounded-lg p-6 mb-6 text-left">
                <h3 className="font-semibold text-gray-800 mb-4">Booking Details</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Confirmation Number:</span>
                    <span className="font-semibold">BK{Math.floor(Math.random() * 1000000)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Passenger:</span>
                    <span className="font-semibold">{bookingDetails.passenger.firstName} {bookingDetails.passenger.lastName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Flight:</span>
                    <span className="font-semibold">{bookingDetails.flight.airline} {bookingDetails.flight.flightNumber}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Route:</span>
                    <span className="font-semibold">{bookingDetails.flight.from} → {bookingDetails.flight.to}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Date:</span>
                    <span className="font-semibold">{bookingDetails.searchData.departDate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Email:</span>
                    <span className="font-semibold">{bookingDetails.passenger.email}</span>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-6">
                A confirmation email has been sent to {bookingDetails.passenger.email}
              </p>

              <button
                onClick={handleNewSearch}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition duration-200"
              >
                Book Another Flight
              </button>
            </div>
          </div>
        ) : (
          <div className="max-w-6xl mx-auto">
            {!selectedFlight && <FlightSearch onSearch={handleSearch} />}

            {selectedFlight ? (
              <BookingForm
                flight={selectedFlight}
                searchData={searchData}
                onConfirm={handleConfirmBooking}
                onCancel={handleCancelBooking}
              />
            ) : (
              <FlightList
                flights={flights}
                searchData={searchData}
                onSelectFlight={handleSelectFlight}
              />
            )}
          </div>
        )}

        <footer className="text-center mt-12 text-white">
          <p className="text-sm">Built with IBM Building Blocks!</p>
        </footer>
        </div>
      </div>
    </div>
  );
}

export default App;
