// ============================================================================
// server.js - WebSocket chat server with room support
// ============================================================================
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static('public'));

// Store room information
const rooms = new Map();

// Helper function to get room info
function getRoomInfo(roomName) {
  if (!rooms.has(roomName)) {
    rooms.set(roomName, {
      users: new Map(),
      messageCount: 0
    });
  }
  return rooms.get(roomName);
}

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log(`New client connected: ${socket.id}`);

  let currentUser = null;
  let currentRoom = null;

  // Handle user joining a room
  socket.on('join-room', ({ username, room }) => {
    // Leave previous room if any
    if (currentRoom) {
      socket.leave(currentRoom);
      const prevRoomInfo = getRoomInfo(currentRoom);
      prevRoomInfo.users.delete(socket.id);

      // Notify previous room
      io.to(currentRoom).emit('user-left', {
        username: currentUser,
        timestamp: new Date().toISOString(),
        usersInRoom: Array.from(prevRoomInfo.users.values())
      });
    }

    // Join new room
    currentUser = username;
    currentRoom = room;
    socket.join(room);

    const roomInfo = getRoomInfo(room);
    roomInfo.users.set(socket.id, username);

    console.log(`${username} joined room: ${room}`);

    // Send join confirmation to user
    socket.emit('joined-room', {
      room: room,
      username: username,
      usersInRoom: Array.from(roomInfo.users.values())
    });

    // Notify room members
    socket.to(room).emit('user-joined', {
      username: username,
      timestamp: new Date().toISOString(),
      usersInRoom: Array.from(roomInfo.users.values())
    });
  });

  // Handle chat messages
  socket.on('send-message', ({ message, room }) => {
    if (!currentRoom || currentRoom !== room) {
      socket.emit('error', { message: 'You are not in this room' });
      return;
    }

    const roomInfo = getRoomInfo(room);
    roomInfo.messageCount++;

    const messageData = {
      id: `${room}-${roomInfo.messageCount}`,
      username: currentUser,
      message: message,
      timestamp: new Date().toISOString(),
      room: room
    };

    // Broadcast to all users in the room (including sender)
    io.to(room).emit('receive-message', messageData);

    console.log(`Message in ${room} from ${currentUser}: ${message}`);
  });

  // Handle typing indicator
  socket.on('typing', ({ room, isTyping }) => {
    if (currentRoom === room) {
      socket.to(room).emit('user-typing', {
        username: currentUser,
        isTyping: isTyping
      });
    }
  });

  // Handle disconnect
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);

    if (currentRoom && currentUser) {
      const roomInfo = getRoomInfo(currentRoom);
      roomInfo.users.delete(socket.id);

      // Notify room members
      io.to(currentRoom).emit('user-left', {
        username: currentUser,
        timestamp: new Date().toISOString(),
        usersInRoom: Array.from(roomInfo.users.values())
      });

      // Clean up empty rooms
      if (roomInfo.users.size === 0) {
        rooms.delete(currentRoom);
        console.log(`Room ${currentRoom} deleted (empty)`);
      }
    }
  });

  // Handle manual leave room
  socket.on('leave-room', () => {
    if (currentRoom && currentUser) {
      const roomInfo = getRoomInfo(currentRoom);
      roomInfo.users.delete(socket.id);

      socket.to(currentRoom).emit('user-left', {
        username: currentUser,
        timestamp: new Date().toISOString(),
        usersInRoom: Array.from(roomInfo.users.values())
      });

      socket.leave(currentRoom);
      console.log(`${currentUser} left room: ${currentRoom}`);

      currentRoom = null;
      currentUser = null;
    }
  });

  // Get available rooms
  socket.on('get-rooms', () => {
    const roomList = Array.from(rooms.entries()).map(([name, info]) => ({
      name: name,
      userCount: info.users.size,
      users: Array.from(info.users.values())
    }));
    socket.emit('rooms-list', roomList);
  });
});

// API endpoint to get server stats
app.get('/api/stats', (req, res) => {
  const stats = {
    totalRooms: rooms.size,
    totalUsers: Array.from(rooms.values()).reduce((sum, room) => sum + room.users.size, 0),
    rooms: Array.from(rooms.entries()).map(([name, info]) => ({
      name: name,
      userCount: info.users.size,
      messageCount: info.messageCount
    }))
  };
  res.json(stats);
});

server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`WebSocket server ready for connections`);
});
