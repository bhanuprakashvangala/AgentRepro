require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');

const app = express();

// In-memory queue for webhook events
const eventQueue = [];

// Middleware to verify the webhook signature
const verifySignature = (req, res, next) => {
    const signature = req.headers['x-hub-signature-256'];
    if (!signature) {
        return res.status(400).send('Signature required');
    }

    const hmac = crypto.createHmac('sha256', process.env.WEBHOOK_SECRET);
    const digest = 'sha256=' + hmac.update(req.rawBody).digest('hex');

    if (!crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(signature))) {
        return res.status(401).send('Invalid signature');
    }

    next();
};

app.use(bodyParser.json({
    verify: (req, res, buf) => {
        req.rawBody = buf.toString();
    }
}));

// Webhook receiver endpoint
app.post('/webhook', verifySignature, (req, res) => {
    const event = req.body;
    console.log('Received webhook event:', event);

    // Add the event to the queue for processing
    eventQueue.push(event);

    res.status(202).send('Event received');
});

// Asynchronous event processor
const processEvents = () => {
    setInterval(() => {
        if (eventQueue.length > 0) {
            const event = eventQueue.shift();
            console.log('Processing event:', event);
            // Add your event processing logic here
        }
    }, 5000); // Process an event every 5 seconds
};

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
    processEvents();
});
