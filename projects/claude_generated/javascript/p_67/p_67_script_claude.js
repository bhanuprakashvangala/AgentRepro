const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');

const PORT = process.env.PORT || 8080;

// Create WebSocket server
const wss = new WebSocket.Server({ port: PORT });

// Store connected clients and rooms
const clients = new Map(); // userId -> { ws, username, room }
const rooms = new Map();   // roomName -> Set of userIds

console.log(`WebSocket Chat Server running on port ${PORT}`);

// Broadcast message to all users in a room
function broadcastToRoom(roomName, message, excludeUserId = null) {
  const roomUsers = rooms.get(roomName);
  if (!roomUsers) return;

  roomUsers.forEach(userId => {
    if (userId !== excludeUserId) {
      const client = clients.get(userId);
      if (client && client.ws.readyState === WebSocket.OPEN) {
        client.ws.send(JSON.stringify(message));
      }
    }
  });
}

// Send user list to all users in a room
function sendUserList(roomName) {
  const roomUsers = rooms.get(roomName);
  if (!roomUsers) return;

  const usernames = Array.from(roomUsers).map(userId => {
    const client = clients.get(userId);
    return client ? client.username : null;
  }).filter(Boolean);

  broadcastToRoom(roomName, {
    type: 'userList',
    users: usernames,
    room: roomName
  });
}

// Handle new connections
wss.on('connection', (ws) => {
  const userId = uuidv4();
  let username = null;
  let currentRoom = null;

  console.log(`New connection: ${userId}`);

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    userId: userId,
    message: 'Connected to chat server'
  }));

  // Handle incoming messages
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);

      switch (message.type) {
        case 'join':
          // Set username and join room
          username = message.username || `User_${userId.substring(0, 8)}`;
          currentRoom = message.room || 'general';

          // Store client info
          clients.set(userId, { ws, username, room: currentRoom });

          // Add user to room
          if (!rooms.has(currentRoom)) {
            rooms.set(currentRoom, new Set());
          }
          rooms.get(currentRoom).add(userId);

          console.log(`${username} joined room: ${currentRoom}`);

          // Notify others in the room
          broadcastToRoom(currentRoom, {
            type: 'join',
            username: username,
            message: `${username} joined the room`,
            timestamp: new Date().toISOString()
          }, userId);

          // Send confirmation to user
          ws.send(JSON.stringify({
            type: 'joined',
            room: currentRoom,
            username: username
          }));

          // Send updated user list
          sendUserList(currentRoom);
          break;

        case 'message':
          if (!currentRoom || !username) {
            ws.send(JSON.stringify({
              type: 'error',
              message: 'Please join a room first'
            }));
            return;
          }

          // Broadcast message to room
          broadcastToRoom(currentRoom, {
            type: 'message',
            username: username,
            content: message.content,
            timestamp: new Date().toISOString()
          });

          console.log(`[${currentRoom}] ${username}: ${message.content}`);
          break;

        case 'leave':
          if (currentRoom) {
            // Remove user from room
            rooms.get(currentRoom)?.delete(userId);

            // Notify others
            broadcastToRoom(currentRoom, {
              type: 'leave',
              username: username,
              message: `${username} left the room`,
              timestamp: new Date().toISOString()
            });

            // Send updated user list
            sendUserList(currentRoom);

            // Clean up empty room
            if (rooms.get(currentRoom)?.size === 0) {
              rooms.delete(currentRoom);
            }

            console.log(`${username} left room: ${currentRoom}`);
            currentRoom = null;
          }
          break;

        case 'getRooms':
          ws.send(JSON.stringify({
            type: 'roomList',
            rooms: Array.from(rooms.keys()).map(roomName => ({
              name: roomName,
              users: rooms.get(roomName).size
            }))
          }));
          break;

        default:
          ws.send(JSON.stringify({
            type: 'error',
            message: 'Unknown message type'
          }));
      }
    } catch (error) {
      console.error('Error processing message:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format'
      }));
    }
  });

  // Handle connection close
  ws.on('close', () => {
    console.log(`Connection closed: ${userId}`);

    if (currentRoom && username) {
      // Remove from room
      rooms.get(currentRoom)?.delete(userId);

      // Notify others
      broadcastToRoom(currentRoom, {
        type: 'leave',
        username: username,
        message: `${username} disconnected`,
        timestamp: new Date().toISOString()
      });

      // Send updated user list
      sendUserList(currentRoom);

      // Clean up empty room
      if (rooms.get(currentRoom)?.size === 0) {
        rooms.delete(currentRoom);
      }
    }

    // Remove from clients
    clients.delete(userId);
  });

  // Handle errors
  ws.on('error', (error) => {
    console.error(`WebSocket error for ${userId}:`, error);
  });

  // Heartbeat
  ws.isAlive = true;
  ws.on('pong', () => {
    ws.isAlive = true;
  });
});

// Heartbeat interval
const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) {
      return ws.terminate();
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

// Cleanup on server close
wss.on('close', () => {
  clearInterval(interval);
});

console.log('\nServer started. Connect using WebSocket client.');
console.log('Message format examples:');
console.log('  Join: {"type":"join","username":"Alice","room":"general"}');
console.log('  Send: {"type":"message","content":"Hello everyone!"}');
console.log('  Leave: {"type":"leave"}');
