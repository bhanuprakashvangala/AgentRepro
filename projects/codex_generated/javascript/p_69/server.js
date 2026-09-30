import 'dotenv/config';
import express from 'express';
import axios from 'axios';
import { MongoClient } from 'mongodb';

const PORT = process.env.PORT || 8080;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/health_db';
const EXTERNAL_SERVICE_URL = process.env.EXTERNAL_SERVICE_URL || 'https://httpbin.org/get';

const app = express();

const mongoClient = new MongoClient(MONGO_URI);
async function checkDatabase() {
  try {
    if (!mongoClient.topology || !mongoClient.topology.isConnected()) {
      await mongoClient.connect();
    }
    await mongoClient.db().command({ ping: 1 });
    return { status: 'up' };
  } catch (error) {
    return { status: 'down', error: error.message };
  }
}

async function checkExternalService() {
  try {
    await axios.get(EXTERNAL_SERVICE_URL, { timeout: 3000 });
    return { status: 'up' };
  } catch (error) {
    return { status: 'down', error: error.message };
  }
}

app.get('/health', async (req, res) => {
  const start = Date.now();
  const [dbStatus, extStatus] = await Promise.all([checkDatabase(), checkExternalService()]);

  const health = {
    status: 'up',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    database: dbStatus,
    externalService: extStatus,
    responseTimeMs: Date.now() - start
  };

  if (dbStatus.status === 'down' || extStatus.status === 'down') {
    health.status = 'down';
    return res.status(503).json(health);
  }

  return res.json(health);
});

app.listen(PORT, () => {
  console.log(`Health check service on http://localhost:${PORT}`);
});
