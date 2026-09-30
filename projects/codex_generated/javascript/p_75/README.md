# API Gateway with Load Balancing

Express-based gateway forwarding requests to microservices with round-robin load balancing and API key auth.

## Setup
```bash
npm install
API_KEY=dev-key \
SERVICES_CONFIG='{"users":["http://localhost:4001","http://localhost:4003"],"orders":["http://localhost:4002"]}' \
npm start
```

`SERVICES_CONFIG` is a JSON object mapping route prefixes to arrays of target URLs. Requests to `/users/*` are proxied to the configured users service instances, `/orders/*` to orders, etc.

## Authentication
All proxied requests (excluding `/health`) require header `x-api-key` matching `API_KEY`.

## Load Balancing
Targets rotate per request using round-robin logic. Failed proxies respond with HTTP 502.

## Endpoints
- `GET /health` – returns configured services and next target index.
- `/users/...`, `/orders/...` – proxied through to upstream services.

Adjust the JSON config and API key as needed for your environment.
