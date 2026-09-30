# Proxy Server with Logging

Express proxy leveraging `http-proxy-middleware`. Logs requests/responses with `morgan`, handles CORS, and manipulates headers.

## Setup
```bash
npm install
TARGET_URL=https://httpbin.org npm start
```
Default target is `https://httpbin.org`, listening on `PORT` 5050.

## Features
- Full request logging (`method`, `url`, `status`, duration, JSON body).
- Adds `X-Proxy-By` header to outbound requests.
- Logs proxy responses.
- CORS enabled for all origins.

Send requests to `http://localhost:5050/...` and they will be proxied to the target.
