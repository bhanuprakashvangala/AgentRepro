import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { nanoid } from 'nanoid';

const PORT = process.env.PORT || 4000;
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

app.use(cors());
app.use(express.json());

const notifications = new Map();

function ensureUser(userId) {
  if (!notifications.has(userId)) {
    notifications.set(userId, []);
  }
  return notifications.get(userId);
}

app.post('/api/notify', (req, res) => {
  const { userId, type, message, meta } = req.body || {};
  if (!userId || !type || !message) {
    return res.status(400).json({ message: '`userId`, `type`, and `message` are required' });
  }
  const entry = {
    id: nanoid(10),
    type,
    message,
    meta: meta || {},
    read: false,
    createdAt: new Date().toISOString()
  };
  const userNotifications = ensureUser(userId);
  userNotifications.unshift(entry);
  io.to(userId).emit('notification', entry);
  return res.status(201).json(entry);
});

app.get('/api/notifications/:userId', (req, res) => {
  const entries = ensureUser(req.params.userId);
  res.json(entries);
});

app.post('/api/notifications/:userId/read', (req, res) => {
  const { ids } = req.body || {};
  if (!Array.isArray(ids)) {
    return res.status(400).json({ message: '`ids` array required' });
  }
  const entries = ensureUser(req.params.userId);
  entries.forEach((notif) => {
    if (ids.includes(notif.id)) {
      notif.read = true;
    }
  });
  io.to(req.params.userId).emit('notifications:updated', entries);
  res.json({ updated: ids.length });
});

io.on('connection', (socket) => {
  socket.on('register', (userId) => {
    if (!userId) return;
    socket.join(userId);
    const entries = ensureUser(userId);
    socket.emit('notifications:init', entries);
  });

  socket.on('disconnect', () => {
    // Handles automatic cleanup by Socket.io
  });
});

app.get('/', (req, res) => {
  res.json({ status: 'Notification server running' });
});

server.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
