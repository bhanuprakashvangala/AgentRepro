# Webhook Receiver & Processor

Express server that validates HMAC signatures, queues events, and processes them asynchronously with `p-queue`.

## Setup
```bash
npm install
export WEBHOOK_SECRET=super-secret-key
npm start
```

## Endpoints
- `POST /webhook` – send JSON body with `X-Signature` header containing `HMAC-SHA256(rawBody, WEBHOOK_SECRET)`.
- `GET /status` – see queue metrics (`pending`, `running`).

## Example signature (Node REPL)
```js
const crypto = require('crypto');
const secret = 'super-secret-key';
const payload = JSON.stringify({ id: 'evt_123', type: 'test' });
const signature = crypto.createHmac('sha256', secret).update(payload).digest('hex');
```
Use that signature in the request header.
