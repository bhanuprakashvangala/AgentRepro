# Real-time Notification System

Socket.io + Express server storing notifications (in-memory for demo) with read/unread tracking.

## Setup
```bash
npm install
npm start
```
Server runs on `http://localhost:4000`. Socket.io endpoint at same origin.

## API
- `POST /api/notify` – body `{ userId, type, message, meta? }` to push notification; broadcasts via Socket.io to room `userId`.
- `GET /api/notifications/:userId` – list notifications.
- `POST /api/notifications/:userId/read` – body `{ ids: [] }` to mark as read.

## Socket.io Events
- Client emits `register` with `userId` to join room.
- Server emits `notifications:init` with current list.
- `notification` event fired on new notification.
- `notifications:updated` when read/unread status changes.

Replace in-memory store with persistent DB (Mongo/Postgres) for production use.
