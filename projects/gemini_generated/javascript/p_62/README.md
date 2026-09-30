# Currency Converter API

This project is a currency converter API with live rates, built with Express, Axios, and Node-Cache.

## Requirements

- Node.js
- npm
- An API key from [exchangerate-api.com](https://www.exchangerate-api.com)

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Create a `.env` file in the root directory and add your API key:

    ```
    API_KEY=YOUR_EXCHANGERATE_API_KEY
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Make a GET request to the `/convert` endpoint with the following query parameters:

    -   `from`: The currency to convert from (e.g., `USD`).
    -   `to`: The currency to convert to (e.g., `EUR`).
    -   `amount`: The amount to convert.

    **Example:**

    ```
    http://localhost:3000/convert?from=USD&to=EUR&amount=100
    ```

### Caching

The exchange rates are cached for 1 hour to reduce the number of API calls.
