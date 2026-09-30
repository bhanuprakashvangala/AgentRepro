# Real-time WebSocket Dashboard

This project builds a FastAPI-powered WebSocket backend with a Plotly.js front-end chart. Multiple clients can connect simultaneously, receive synchronized updates, and visualize live data streams in real time.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/` in your browser. Each connected client will see the same rolling Plotly graph, refreshed every second. The app broadcasts synthetic demo points to all clients; adjust `data_producer()` in `main.py` to hook in real data sources. The WebSocket endpoint is available at `/ws` for custom integrations.

> **Note:** The bundled HTML loads Plotly from the official CDN. Ensure outbound network access is allowed when viewing the dashboard.
