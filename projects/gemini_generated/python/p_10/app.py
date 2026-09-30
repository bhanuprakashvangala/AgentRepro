from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import random
from threading import Thread, Event

app = Flask(__name__)
# Use a secret key for session management
app.config['SECRET_KEY'] = 'your-secret-key-here' 
# Use eventlet as the async mode for production-level performance
socketio = SocketIO(app, async_mode='eventlet')

# --- Background Thread for Data Simulation ---
thread = Thread()
thread_stop_event = Event()

def data_generator():
    """
    Generates random data and emits it to clients every second.
    This function runs in a background thread.
    """
    print("Starting data generator thread...")
    while not thread_stop_event.is_set():
        # Simulate generating a new data point
        data_point = {
            "time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "value": round(random.random() * 100, 2)
        }
        print(f"Broadcasting data: {data_point}")
        # Broadcast the update to all connected clients
        socketio.emit('update_data', data_point, namespace='/test')
        socketio.sleep(1) # Use socketio.sleep for compatibility

# --- Flask Routes ---
@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

# --- SocketIO Event Handlers ---
@socketio.on('connect', namespace='/test')
def handle_connect():
    """Handle a new client connection."""
    global thread
    print("Client connected")

    # Start the background thread only if it is not already running
    if not thread.is_alive():
        print("Starting background thread...")
        thread = socketio.start_background_task(data_generator)

@socketio.on('disconnect', namespace='/test')
def handle_disconnect():
    """Handle a client disconnection."""
    print("Client disconnected")

if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    # Use socketio.run() to start the server with WebSocket support
    # eventlet is a recommended production server for Flask-SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
