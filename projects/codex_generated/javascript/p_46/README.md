# Real-time Data Visualization Dashboard

Vite + React dashboard displaying live metrics using Chart.js (via `react-chartjs-2`). A simple WebSocket server (`server.js`) streams random data for demo purposes.

## Setup
```bash
npm install
```

Start the WebSocket server:
```bash
npm run server
```

Start the dashboard in another terminal:
```bash
npm run dev
```
Visit http://localhost:5173. Ensure `VITE_WS_URL` (optional) matches WebSocket endpoint (default `ws://localhost:4000`).

## Features
- Three responsive charts: line (time series), bar (category counts), pie (category share).
- Real-time updates via WebSocket; charts retain last 20 data points.
- Responsive layout with light/dark awareness.

Customize by replacing `server.js` streaming logic with real data sources.
