const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const PORT = process.env.PORT || 4000;

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

app.get('/', (req, res) => {
  res.json({ status: 'Chat server running' });
});

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('joinRoom', ({ room, username }) => {
    socket.join(room);
    socket.data.username = username;
    socket.data.room = room;
    console.log(`${username} joined room ${room}`);

    socket.to(room).emit('systemMessage', `${username} joined the room.`);
    socket.emit('systemMessage', `Welcome to room ${room}!`);
  });

  socket.on('leaveRoom', () => {
    const { room, username } = socket.data;
    if (room) {
      socket.leave(room);
      socket.to(room).emit('systemMessage', `${username} left the room.`);
      socket.data.room = null;
    }
  });

  socket.on('chatMessage', ({ message }) => {
    const { room, username } = socket.data;
    if (!room) {
      return socket.emit('systemMessage', 'You must join a room first.');
    }
    io.to(room).emit('chatMessage', {
      username,
      message,
      timestamp: new Date().toISOString()
    });
  });

  socket.on('disconnect', () => {
    const { room, username } = socket.data;
    if (room) {
      socket.to(room).emit('systemMessage', `${username || 'A user'} disconnected.`);
    }
    console.log('Client disconnected:', socket.id);
  });
});

server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
