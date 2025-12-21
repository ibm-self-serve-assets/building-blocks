import React from 'react';

const FlightCard = ({ flight, onSelect }) => {
  const getSustainabilityColor = (rating) => {
    const colors = {
      green: 'bg-green-100 text-green-800 border-green-300',
      lime: 'bg-lime-100 text-lime-800 border-lime-300',
      yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      orange: 'bg-orange-100 text-orange-800 border-orange-300'
    };
    return colors[rating] || colors.yellow;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition duration-200 border-l-4" style={{ borderLeftColor: flight.emissions?.rating.color === 'green' ? '#10b981' : flight.emissions?.rating.color === 'lime' ? '#84cc16' : flight.emissions?.rating.color === 'yellow' ? '#eab308' : '#f97316' }}>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div className="flex-1 mb-4 md:mb-0">
          <div className="flex items-center mb-3">
            <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
              {flight.airline}
            </div>
            <span className="ml-3 text-gray-500 text-sm">Flight {flight.flightNumber}</span>
          </div>

          <div className="flex items-center gap-8">
            <div>
              <div className="text-2xl font-bold text-gray-800">{flight.departureTime}</div>
              <div className="text-gray-600">{flight.from}</div>
            </div>

            <div className="flex-1 flex flex-col items-center">
              <div className="text-gray-500 text-sm mb-1">{flight.duration}</div>
              <div className="w-full h-px bg-gray-300 relative">
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                  </svg>
                </div>
              </div>
              <div className="text-gray-500 text-sm mt-1">{flight.stops}</div>
            </div>

            <div>
              <div className="text-2xl font-bold text-gray-800">{flight.arrivalTime}</div>
              <div className="text-gray-600">{flight.to}</div>
            </div>
          </div>
        </div>

        <div className="md:ml-8 flex flex-col items-start md:items-end">
          <div className="text-3xl font-bold text-blue-600 mb-2">
            ${flight.price}
          </div>
          <div className="text-gray-500 text-sm mb-3">per person</div>
          <button
            onClick={() => onSelect(flight)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition duration-200"
          >
            Select Flight
          </button>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {flight.baggage}
          </span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {flight.class}
          </span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
            </svg>
            {flight.aircraft}
          </span>
        </div>

        {flight.emissions && (
          <div className={`mt-3 p-3 rounded-lg border ${getSustainabilityColor(flight.emissions.rating.color)}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">{flight.emissions.rating.icon}</span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{flight.emissions.rating.rating} Sustainability</span>
                    <span className="text-xs opacity-75">• {flight.emissions.rating.description}</span>
                  </div>
                  <div className="text-sm mt-1">
                    <span className="font-medium">{flight.emissions.co2PerPassenger} kg CO₂</span>
                    <span className="opacity-75"> per passenger • {flight.emissions.distance} km</span>
                  </div>
                </div>
              </div>
              <div className="text-right text-xs">
                <div className="opacity-75">Carbon offset</div>
                <div className="font-semibold">${flight.emissions.offsetCost}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const FlightList = ({ flights, searchData, onSelectFlight }) => {
  const [sortBy, setSortBy] = React.useState('price');

  if (!flights || flights.length === 0) {
    return null;
  }

  const sortedFlights = [...flights].sort((a, b) => {
    switch (sortBy) {
      case 'price':
        return a.price - b.price;
      case 'emissions':
        return a.emissions.co2PerPassenger - b.emissions.co2PerPassenger;
      case 'duration':
        return a.duration.localeCompare(b.duration);
      default:
        return 0;
    }
  });

  return (
    <div className="mb-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          Available Flights ({flights.length})
        </h2>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600 font-medium">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="price">Price</option>
            <option value="emissions">Lowest Emissions</option>
            <option value="duration">Duration</option>
          </select>
        </div>
      </div>

      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-gray-700">
          <span className="font-semibold">{searchData.from}</span>
          {' → '}
          <span className="font-semibold">{searchData.to}</span>
          {' • '}
          <span>{searchData.departDate}</span>
          {searchData.tripType === 'round-trip' && (
            <span> - {searchData.returnDate}</span>
          )}
          {' • '}
          <span>{searchData.passengers} passenger{searchData.passengers > 1 ? 's' : ''}</span>
        </p>
      </div>

      {sortedFlights.map(flight => (
        <FlightCard
          key={flight.id}
          flight={flight}
          onSelect={onSelectFlight}
        />
      ))}
    </div>
  );
};

export default FlightList;
