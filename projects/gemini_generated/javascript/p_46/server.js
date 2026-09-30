const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static('public'));

io.on('connection', (socket) => {
    console.log('A user connected');

    const sendData = setInterval(() => {
        const data = {
            lineData: Math.random() * 100,
            barData: Math.floor(Math.random() * 100) + 1,
            pieData: [
                Math.random() * 100,
                Math.random() * 100,
                Math.random() * 100
            ]
        };
        socket.emit('data', data);
    }, 1000);

    socket.on('disconnect', () => {
        console.log('User disconnected');
        clearInterval(sendData);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
