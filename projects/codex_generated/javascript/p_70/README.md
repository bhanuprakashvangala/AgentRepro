# IP Geolocation Service

Express API leveraging `geoip-lite` to resolve location data from IP addresses with in-memory caching.

## Setup
```bash
npm install
npm start
```
Environment options: `PORT`, `CACHE_TTL_SECONDS` (default 3600).

## Endpoint
`GET /geolocate?ip=8.8.8.8`
Returns:
```json
{
  "ip": "8.8.8.8",
  "city": "Mountain View",
  "country": "US",
  "coordinates": { "latitude": 37.386, "longitude": -122.0838 },
  "source": "lookup"
}
```
Subsequent requests within TTL return `source: "cache"`.

`GET /` provides status.
