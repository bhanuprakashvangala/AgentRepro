# WebSocket Chat Server

Socket.io chat backend with room support and join/leave events. Messages are broadcast only to members within the same room.

## Setup
```bash
npm install
npm start
```
Server listens on `http://localhost:4000` (set `PORT` env to override).

## Socket Events
- `joinRoom` `{ room, username }`
- `leaveRoom`
- `chatMessage` `{ message }`
- `systemMessage` (server -> clients)
- `chatMessage` (server -> clients)

Example client (browser console):
```js
const socket = io('http://localhost:4000');
socket.emit('joinRoom', { room: 'general', username: 'Alice' });
socket.on('chatMessage', (msg) => console.log(msg));
```

Leverages Express for HTTP health endpoint and CORS settings.
