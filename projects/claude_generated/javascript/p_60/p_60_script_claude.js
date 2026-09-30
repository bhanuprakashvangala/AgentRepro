const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const cors = require('cors');
const path = require('path');
const NotificationService = require('./services/NotificationService');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Initialize notification service
const notificationService = new NotificationService();

// Store connected users
const connectedUsers = new Map();

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);

  // User authentication/registration
  socket.on('register', (userId) => {
    connectedUsers.set(userId, socket.id);
    socket.userId = userId;
    console.log(`User ${userId} registered with socket ${socket.id}`);

    // Send unread notifications count
    const unreadCount = notificationService.getUnreadCount(userId);
    socket.emit('unread_count', unreadCount);
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    if (socket.userId) {
      connectedUsers.delete(socket.userId);
      console.log(`User ${socket.userId} disconnected`);
    }
  });

  // Mark notification as read
  socket.on('mark_as_read', (notificationId) => {
    try {
      notificationService.markAsRead(notificationId);
      socket.emit('notification_updated', { notificationId, read: true });

      // Send updated unread count
      if (socket.userId) {
        const unreadCount = notificationService.getUnreadCount(socket.userId);
        socket.emit('unread_count', unreadCount);
      }
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });

  // Mark all notifications as read
  socket.on('mark_all_as_read', () => {
    if (socket.userId) {
      try {
        notificationService.markAllAsRead(socket.userId);
        socket.emit('all_notifications_read');
        socket.emit('unread_count', 0);
      } catch (error) {
        socket.emit('error', { message: error.message });
      }
    }
  });
});

// REST API Endpoints

// Get all notifications for a user
app.get('/api/notifications/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    const { limit = 50, offset = 0 } = req.query;

    const notifications = notificationService.getNotifications(
      userId,
      parseInt(limit),
      parseInt(offset)
    );

    res.json({
      success: true,
      data: notifications,
      count: notifications.length
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get unread notifications
app.get('/api/notifications/:userId/unread', (req, res) => {
  try {
    const { userId } = req.params;
    const notifications = notificationService.getUnreadNotifications(userId);

    res.json({
      success: true,
      data: notifications,
      count: notifications.length
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Create a new notification
app.post('/api/notifications', (req, res) => {
  try {
    const { userId, type, title, message, metadata } = req.body;

    if (!userId || !type || !title || !message) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: userId, type, title, message'
      });
    }

    const notification = notificationService.createNotification(
      userId,
      type,
      title,
      message,
      metadata
    );

    // Send real-time notification via Socket.io
    const socketId = connectedUsers.get(userId);
    if (socketId) {
      io.to(socketId).emit('new_notification', notification);

      // Update unread count
      const unreadCount = notificationService.getUnreadCount(userId);
      io.to(socketId).emit('unread_count', unreadCount);
    }

    res.json({
      success: true,
      data: notification
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Delete a notification
app.delete('/api/notifications/:notificationId', (req, res) => {
  try {
    const { notificationId } = req.params;
    notificationService.deleteNotification(notificationId);

    res.json({
      success: true,
      message: 'Notification deleted'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get notification statistics
app.get('/api/notifications/:userId/stats', (req, res) => {
  try {
    const { userId } = req.params;
    const stats = notificationService.getStats(userId);

    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`WebSocket server ready for connections`);
});
