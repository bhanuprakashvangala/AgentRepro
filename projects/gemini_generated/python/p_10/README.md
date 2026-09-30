# Real-Time Dashboard with Flask-SocketIO

This project is a real-time web dashboard that displays live-updating data using Flask-SocketIO for WebSocket communication and Plotly.js for charting.

## Features

- **Flask Backend**: A simple Flask server to serve the dashboard.
- **WebSocket Integration**: Uses `Flask-SocketIO` to push data from the server to the client in real-time.
- **Live Charting**: A `Plotly.js` chart on the frontend that updates dynamically as new data arrives.
- **Background Data Simulation**: A background thread on the server simulates a continuous stream of new data.
- **Multi-Client Support**: Updates are broadcast to all connected clients, allowing multiple users to view the same live dashboard simultaneously.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

4.  **View the Dashboard:**
    - Open your web browser and navigate to `http://127.0.0.1:5000`.
    - You should see a chart that begins to update every second with new data points.
    - To see the multi-client broadcast in action, open the same address in another browser tab or window. Both charts will update in sync.

## How It Works

- The Flask server runs a background thread (`data_generator` in `app.py`) that simulates a data source, emitting a `update_data` event every second.
- The `index.html` page uses the `socket.io.js` client library to connect to the server.
- When the client receives an `update_data` event, it uses the `Plotly.extendTraces` function to efficiently add the new data point to the live chart.
