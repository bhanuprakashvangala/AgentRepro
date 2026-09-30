from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import time
from threading import Thread, Event
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Thread control
thread = None
thread_stop_event = Event()

# Store recent data for new clients
data_history = {
    'timestamps': [],
    'cpu_usage': [],
    'memory_usage': [],
    'network_traffic': []
}
MAX_HISTORY = 50

def generate_random_data():
    """Simulate real-time system metrics"""
    return {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'cpu_usage': random.uniform(20, 90),
        'memory_usage': random.uniform(30, 85),
        'network_traffic': random.uniform(10, 100),
        'active_users': random.randint(5, 50)
    }

def background_thread():
    """Background thread that generates and broadcasts data"""
    print("Background thread started")
    while not thread_stop_event.is_set():
        data = generate_random_data()

        # Update history
        data_history['timestamps'].append(data['timestamp'])
        data_history['cpu_usage'].append(data['cpu_usage'])
        data_history['memory_usage'].append(data['memory_usage'])
        data_history['network_traffic'].append(data['network_traffic'])

        # Keep only last MAX_HISTORY items
        if len(data_history['timestamps']) > MAX_HISTORY:
            data_history['timestamps'].pop(0)
            data_history['cpu_usage'].pop(0)
            data_history['memory_usage'].pop(0)
            data_history['network_traffic'].pop(0)

        # Broadcast to all connected clients
        socketio.emit('update_data', data, namespace='/dashboard')
        socketio.sleep(1)  # Update every second

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/dashboard')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {id}')
    global thread

    # Start background thread if not already running
    if thread is None or not thread.is_alive():
        thread_stop_event.clear()
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()

    # Send historical data to new client
    emit('initial_data', data_history)

@socketio.on('disconnect', namespace='/dashboard')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('request_data', namespace='/dashboard')
def handle_data_request():
    """Handle manual data request from client"""
    data = generate_random_data()
    emit('update_data', data)

if __name__ == '__main__':
    print("Starting Real-Time Dashboard Server...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
