const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const Queue = require('bull');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'your-webhook-secret-key';
const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';

// Create webhook event queue
const webhookQueue = new Queue('webhook-events', REDIS_URL, {
  redis: {
    maxRetriesPerRequest: null,
    enableReadyCheck: false
  }
});

// Middleware to parse JSON with raw body for signature verification
app.use(bodyParser.json({
  verify: (req, res, buf) => {
    req.rawBody = buf.toString('utf8');
  }
}));

/**
 * Verify webhook signature using HMAC SHA256
 * @param {string} payload - Raw request body
 * @param {string} signature - Signature from request header
 * @param {string} secret - Webhook secret key
 * @returns {boolean} - True if signature is valid
 */
function verifySignature(payload, signature, secret) {
  if (!signature) {
    return false;
  }

  // Create HMAC hash
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(payload);
  const digest = 'sha256=' + hmac.digest('hex');

  // Compare signatures using timing-safe comparison
  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(digest)
    );
  } catch (error) {
    return false;
  }
}

/**
 * Middleware to validate webhook signatures
 */
function validateWebhookSignature(req, res, next) {
  const signature = req.headers['x-webhook-signature'] || req.headers['x-hub-signature-256'];

  if (!signature) {
    return res.status(401).json({
      success: false,
      error: 'Missing webhook signature'
    });
  }

  const isValid = verifySignature(req.rawBody, signature, WEBHOOK_SECRET);

  if (!isValid) {
    return res.status(401).json({
      success: false,
      error: 'Invalid webhook signature'
    });
  }

  next();
}

/**
 * Webhook receiver endpoint
 */
app.post('/webhook', validateWebhookSignature, async (req, res) => {
  try {
    const event = req.body;
    const eventType = req.headers['x-event-type'] || event.type || 'unknown';

    console.log(`Received webhook event: ${eventType}`);

    // Add event to processing queue
    const job = await webhookQueue.add({
      eventType,
      payload: event,
      receivedAt: new Date().toISOString(),
      headers: {
        'x-event-type': req.headers['x-event-type'],
        'x-request-id': req.headers['x-request-id']
      }
    }, {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000
      },
      removeOnComplete: 100,
      removeOnFail: false
    });

    console.log(`Event queued with job ID: ${job.id}`);

    // Respond immediately to webhook sender
    res.status(200).json({
      success: true,
      message: 'Webhook received and queued for processing',
      jobId: job.id
    });
  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

/**
 * Health check endpoint
 */
app.get('/health', async (req, res) => {
  try {
    const queueHealth = await webhookQueue.isReady();
    res.status(200).json({
      status: 'healthy',
      queue: queueHealth ? 'connected' : 'disconnected',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});

/**
 * Get queue status endpoint
 */
app.get('/queue/status', async (req, res) => {
  try {
    const waiting = await webhookQueue.getWaitingCount();
    const active = await webhookQueue.getActiveCount();
    const completed = await webhookQueue.getCompletedCount();
    const failed = await webhookQueue.getFailedCount();

    res.status(200).json({
      queue: {
        waiting,
        active,
        completed,
        failed,
        total: waiting + active
      }
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

/**
 * Process webhook events from queue
 */
webhookQueue.process(async (job) => {
  const { eventType, payload, receivedAt } = job.data;

  console.log(`Processing job ${job.id} - Event type: ${eventType}`);

  try {
    // Simulate processing based on event type
    await processWebhookEvent(eventType, payload);

    console.log(`Successfully processed job ${job.id}`);

    return {
      success: true,
      processedAt: new Date().toISOString(),
      eventType
    };
  } catch (error) {
    console.error(`Failed to process job ${job.id}:`, error);
    throw error;
  }
});

/**
 * Process different webhook event types
 * @param {string} eventType - Type of webhook event
 * @param {object} payload - Event payload
 */
async function processWebhookEvent(eventType, payload) {
  // Add your custom event processing logic here

  switch (eventType) {
    case 'user.created':
      await handleUserCreated(payload);
      break;

    case 'order.completed':
      await handleOrderCompleted(payload);
      break;

    case 'payment.succeeded':
      await handlePaymentSucceeded(payload);
      break;

    case 'subscription.cancelled':
      await handleSubscriptionCancelled(payload);
      break;

    default:
      console.log(`Unhandled event type: ${eventType}`);
      await handleGenericEvent(eventType, payload);
  }
}

// Event handlers
async function handleUserCreated(payload) {
  console.log('Processing user.created event:', payload.user?.id);
  // Add your logic: send welcome email, create user profile, etc.
  await simulateAsyncWork(1000);
}

async function handleOrderCompleted(payload) {
  console.log('Processing order.completed event:', payload.order?.id);
  // Add your logic: update inventory, send confirmation, etc.
  await simulateAsyncWork(1500);
}

async function handlePaymentSucceeded(payload) {
  console.log('Processing payment.succeeded event:', payload.payment?.id);
  // Add your logic: update payment status, trigger fulfillment, etc.
  await simulateAsyncWork(800);
}

async function handleSubscriptionCancelled(payload) {
  console.log('Processing subscription.cancelled event:', payload.subscription?.id);
  // Add your logic: update subscription status, send confirmation, etc.
  await simulateAsyncWork(500);
}

async function handleGenericEvent(eventType, payload) {
  console.log(`Processing generic event: ${eventType}`);
  // Default handler for unknown event types
  await simulateAsyncWork(500);
}

// Helper function to simulate async work
function simulateAsyncWork(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Queue event listeners
webhookQueue.on('completed', (job, result) => {
  console.log(`Job ${job.id} completed:`, result);
});

webhookQueue.on('failed', (job, err) => {
  console.error(`Job ${job.id} failed:`, err.message);
});

webhookQueue.on('error', (error) => {
  console.error('Queue error:', error);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server...');
  await webhookQueue.close();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, closing server...');
  await webhookQueue.close();
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  console.log(`Webhook server running on port ${PORT}`);
  console.log(`Webhook endpoint: http://localhost:${PORT}/webhook`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Queue status: http://localhost:${PORT}/queue/status`);
});
