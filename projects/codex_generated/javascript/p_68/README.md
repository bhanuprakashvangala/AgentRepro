# Content Delivery Optimizer

Builds optimized static assets (minified CSS/JS, compressed images) and serves them through Express with compression and caching headers.

## Setup
```bash
npm install
npm run build
npm start
```
Visit `http://localhost:5000`.

## Features
- `build.js` minifies CSS/JS, optimizes HTML, and compresses images via Sharp.
- `server.js` serves from `dist/` with gzip (`compression`) and long-lived caching headers (shorter for text assets).
- `CACHE_CONTROL` logic ensures efficient content delivery.

Customize source files under `src/` and rerun `npm run build`.
