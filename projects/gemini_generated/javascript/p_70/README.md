# Geolocation Service

This project is a geolocation service that uses IP addresses to lookup location data, built with Express, geoip-lite, and Node-Cache.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Make a GET request to the `/geocode` endpoint with an optional `ip` query parameter.

    **Example:**

    ```
    http://localhost:3000/geocode?ip=8.8.8.8
    ```

    If no `ip` parameter is provided, the service will use the IP address of the client making the request.

### Caching

The geolocation results are cached for 1 hour to reduce the number of lookups.
