import React, { useState } from 'react';
import AirportAutocomplete from './AirportAutocomplete';

const FlightSearch = ({ onSearch }) => {
  const [searchData, setSearchData] = useState({
    from: '',
    to: '',
    departDate: '',
    returnDate: '',
    passengers: 1,
    tripType: 'round-trip'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSearchData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(searchData);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Search Flights</h2>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <div className="flex gap-4 mb-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="tripType"
                value="round-trip"
                checked={searchData.tripType === 'round-trip'}
                onChange={handleChange}
                className="mr-2"
              />
              <span className="text-gray-700">Round Trip</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="tripType"
                value="one-way"
                checked={searchData.tripType === 'one-way'}
                onChange={handleChange}
                className="mr-2"
              />
              <span className="text-gray-700">One Way</span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              From
            </label>
            <AirportAutocomplete
              name="from"
              value={searchData.from}
              onChange={handleChange}
              placeholder="Search city or airport code"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              To
            </label>
            <AirportAutocomplete
              name="to"
              value={searchData.to}
              onChange={handleChange}
              placeholder="Search city or airport code"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Departure Date
            </label>
            <input
              type="date"
              name="departDate"
              value={searchData.departDate}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {searchData.tripType === 'round-trip' && (
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Return Date
              </label>
              <input
                type="date"
                name="returnDate"
                value={searchData.returnDate}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required={searchData.tripType === 'round-trip'}
              />
            </div>
          )}

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Passengers
            </label>
            <select
              name="passengers"
              value={searchData.passengers}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {[1, 2, 3, 4, 5, 6].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex justify-center">
          <button
            type="submit"
            className="w-1/4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
          >
            Search Flights
          </button>
        </div>
      </form>
    </div>
  );
};

export default FlightSearch;
