const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const mongoose = require('mongoose');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// MongoDB Connection
const MONGO_URI = 'mongodb://localhost:27017/notification_system';
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Failed to connect to MongoDB', err));

// Notification Schema
const notificationSchema = new mongoose.Schema({
    type: String,
    message: String,
    isRead: {
        type: Boolean,
        default: false
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

const Notification = mongoose.model('Notification', notificationSchema);

app.use(express.static('public'));

io.on('connection', (socket) => {
    console.log('A user connected');

    // Send existing notifications
    Notification.find({}).sort({ createdAt: -1 }).limit(10).then(notifications => {
        socket.emit('notifications', notifications);
    });

    // Handle marking a notification as read
    socket.on('markAsRead', async (notificationId) => {
        try {
            await Notification.findByIdAndUpdate(notificationId, { isRead: true });
            const notifications = await Notification.find({}).sort({ createdAt: -1 }).limit(10);
            io.emit('notifications', notifications);
        } catch (err) {
            console.error(err);
        }
    });

    socket.on('disconnect', () => {
        console.log('User disconnected');
    });
});

// Function to create a new notification
const createNotification = async (type, message) => {
    const notification = new Notification({ type, message });
    await notification.save();
    const notifications = await Notification.find({}).sort({ createdAt: -1 }).limit(10);
    io.emit('notifications', notifications);
};

// Simulate creating new notifications every 10 seconds
setInterval(() => {
    const notificationTypes = ['info', 'warning', 'error'];
    const randomType = notificationTypes[Math.floor(Math.random() * notificationTypes.length)];
    createNotification(randomType, `This is a ${randomType} notification.`);
}, 10000);

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
