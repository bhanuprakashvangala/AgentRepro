# Currency Converter API

Express service fetching live exchange rates and caching responses for a configurable TTL. Uses [exchangerate.host](https://exchangerate.host) by default.

## Setup
```bash
npm install
npm start
```
Environment variables (optional):
```
PORT=4000
BASE_CURRENCY=USD
CACHE_TTL_SECONDS=300
RATES_API=https://api.exchangerate.host/latest
```

## Endpoints
- `GET /convert?from=USD&to=EUR&amount=100`
- `GET /rates?base=USD`
- `GET /` (status)

Responses include cached rate data; cache invalidated after TTL. Adjust `RATES_API` if using a different provider (must return `rates` object).
