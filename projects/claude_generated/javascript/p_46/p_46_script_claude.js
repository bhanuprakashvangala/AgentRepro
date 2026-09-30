const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Serve static files
app.use(express.static('public'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Store connected clients
const clients = new Set();

wss.on('connection', (ws) => {
  console.log('Client connected');
  clients.add(ws);

  ws.on('close', () => {
    console.log('Client disconnected');
    clients.delete(ws);
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    clients.delete(ws);
  });
});

// Generate random data for different chart types
function generateLineData() {
  return {
    type: 'line',
    timestamp: new Date().toLocaleTimeString(),
    values: {
      cpu: Math.random() * 100,
      memory: Math.random() * 100,
      disk: Math.random() * 100
    }
  };
}

function generateBarData() {
  return {
    type: 'bar',
    timestamp: Date.now(),
    values: [
      { label: 'Product A', value: Math.floor(Math.random() * 1000) },
      { label: 'Product B', value: Math.floor(Math.random() * 1000) },
      { label: 'Product C', value: Math.floor(Math.random() * 1000) },
      { label: 'Product D', value: Math.floor(Math.random() * 1000) }
    ]
  };
}

function generatePieData() {
  return {
    type: 'pie',
    timestamp: Date.now(),
    values: [
      { label: 'Desktop', value: Math.floor(Math.random() * 100) + 50 },
      { label: 'Mobile', value: Math.floor(Math.random() * 100) + 50 },
      { label: 'Tablet', value: Math.floor(Math.random() * 100) + 50 }
    ]
  };
}

// Broadcast data to all connected clients
function broadcast(data) {
  const message = JSON.stringify(data);
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

// Send real-time updates
setInterval(() => {
  broadcast(generateLineData());
}, 1000);

setInterval(() => {
  broadcast(generateBarData());
}, 3000);

setInterval(() => {
  broadcast(generatePieData());
}, 5000);

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
