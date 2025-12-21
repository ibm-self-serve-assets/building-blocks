# Flight Booking System - with Emissions Tracking

A modern flight booking application built with React and Tailwind CSS, now featuring comprehensive emissions tracking powered by IBM Envizi Emissions API.

## Features

- Real-time CO₂ emissions calculations for each flight
- Sustainability ratings (Excellent, Good, Average, High)
- Carbon offset cost calculations
- Visual indicators with color-coded sustainability badges
- Sort flights by lowest emissions to make sustainable travel choices

For detailed information about the emissions feature, see [EMISSIONS_FEATURE.md](./EMISSIONS_FEATURE.md)


## How to Use

1. **Search for Flights**:
   - Select trip type (Round Trip or One Way)
   - Enter departure and arrival cities
   - Choose travel dates
   - Select number of passengers
   - Click "Search Flights"

2. **Select a Flight**:
   - Browse through the available flights
   - Compare prices, timings, airlines, and emissions
   - View sustainability ratings and carbon footprint for each option
   - Sort by "Lowest Emissions" to find the most sustainable option
   - Check carbon offset costs
   - Click "Select Flight" on your preferred option

3. **Complete Booking**: (Optional)
   - Fill in passenger information
   - Enter payment details
   - Review the total price
   - Click "Confirm Booking"

4. **Confirmation**: (Optional)
   - View your booking confirmation
   - Note the confirmation number
   - Start a new search if needed

## Technologies Used

- **IBM Envizi Emissions API** - Real-time CO₂ emissions calculations
- **React** - JavaScript library for building user interfaces
- **ExpressJS** - Server proxy

## Project Structure

```
booking
├── Dockerfile
├── Dockerfile.codeengine
├── README.md
├── env.example                      # Environment variables template
├── nginx.conf
├── nginx.conf.template
├── public/
├── server.js
├── src
│   ├── App.css                       # Custom styles
│   ├── App.js                        # Main application component
│   ├── components
│   │   ├── AirportAutocomplete.js.   # Airport search autocomplete
│   │   ├── BookingForm.js            # Booking and payment form
│   │   ├── FlightList.js             # Flight results with emissions display
│   │   └── FlightSearch.js           # Search form component
│   ├── data
│   │   └── airports.js               # US airports database with coordinates
│   ├── index.css                     # CSS imports
│   ├── index.js
│   ├── logo.svg
│   ├── services
│   │   └── emissionsService.js       # Emissions API integration & calculations
│   └── setupTests.js
└── package.json
```


