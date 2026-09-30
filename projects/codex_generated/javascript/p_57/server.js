import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import crypto from 'crypto';
import { PQueue } from 'p-queue';

const app = express();
const PORT = process.env.PORT || 3000;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'change-me';
const queue = new PQueue({ concurrency: 2 });

app.use(bodyParser.json({ verify: rawBodySaver }));

function rawBodySaver(req, res, buf) {
  req.rawBody = buf;
}

function verifySignature(req) {
  const signature = req.get('X-Signature');
  if (!signature) return false;
  const computed = crypto.createHmac('sha256', WEBHOOK_SECRET).update(req.rawBody).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(computed));
}

app.post('/webhook', (req, res) => {
  if (!verifySignature(req)) {
    return res.status(401).json({ message: 'Invalid signature' });
  }

  const event = req.body;
  queue.add(() => processEvent(event)).catch((error) => {
    console.error('Failed to process event:', error);
  });
  return res.status(202).json({ message: 'Accepted' });
});

async function processEvent(event) {
  console.log('Processing event', event.id || 'unknown');
  await new Promise((resolve) => setTimeout(resolve, 1000));
  console.log('Processed event type:', event.type);
}

app.get('/status', (req, res) => {
  res.json({ pending: queue.size, running: queue.pending });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Webhook server listening on port ${PORT}`);
});
