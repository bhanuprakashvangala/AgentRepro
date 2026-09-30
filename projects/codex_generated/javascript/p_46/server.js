import http from 'http';
import { WebSocketServer } from 'ws';

const PORT = process.env.WS_PORT || 4000;

const server = http.createServer();
const wss = new WebSocketServer({ server });

function generatePayload() {
  const categories = ['A', 'B', 'C'];
  const category = categories[Math.floor(Math.random() * categories.length)];
  return {
    timestamp: new Date().toLocaleTimeString(),
    value: Number((Math.random() * 100).toFixed(2)),
    category
  };
}

wss.on('connection', (ws) => {
  console.log('Client connected');
  const interval = setInterval(() => {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify(generatePayload()));
    }
  }, 2000);

  ws.on('close', () => {
    clearInterval(interval);
    console.log('Client disconnected');
  });
});

server.listen(PORT, () => {
  console.log(`WebSocket server running on ws://localhost:${PORT}`);
});
