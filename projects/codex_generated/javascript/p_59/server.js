import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import logger from './logger.js';

const app = express();
const PORT = process.env.PORT || 5000;

app.use(bodyParser.json());

app.post('/logs', (req, res) => {
  const { level = 'info', message, meta = {}, source = 'unknown' } = req.body || {};
  if (!message) {
    return res.status(400).json({ message: '`message` is required' });
  }
  const payload = { source, ...meta };
  logger.log(level, message, payload);
  return res.status(202).json({ status: 'accepted' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  logger.info(`Log aggregator listening on port ${PORT}`);
});
