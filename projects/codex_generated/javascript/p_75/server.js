import 'dotenv/config';
import express from 'express';
import morgan from 'morgan';
import { createProxyServer } from 'http-proxy';

const API_KEY = process.env.API_KEY || 'dev-key';
const PORT = process.env.PORT || 8080;

let serviceConfig;
if (process.env.SERVICES_CONFIG) {
  try {
    serviceConfig = JSON.parse(process.env.SERVICES_CONFIG);
  } catch (error) {
    console.error('Invalid SERVICES_CONFIG JSON. Falling back to defaults.');
  }
}

if (!serviceConfig) {
  serviceConfig = {
    users: ['http://localhost:4001'],
    orders: ['http://localhost:4002']
  };
}

const counters = Object.fromEntries(Object.keys(serviceConfig).map((key) => [key, 0]));

function getTarget(service) {
  const targets = serviceConfig[service];
  if (!targets || targets.length === 0) {
    return null;
  }
  const index = counters[service] % targets.length;
  counters[service] = counters[service] + 1;
  return targets[index];
}

const proxy = createProxyServer({});
proxy.on('error', (err, req, res) => {
  console.error('Proxy error:', err.message);
  if (!res.headersSent) {
    res.writeHead(502, { 'Content-Type': 'application/json' });
  }
  res.end(JSON.stringify({ message: 'Bad gateway', error: err.message }));
});

const app = express();
app.use(express.json());
app.use(morgan('combined'));

app.use((req, res, next) => {
  if (req.path === '/health') {
    return next();
  }
  const key = req.get('x-api-key');
  if (key !== API_KEY) {
    return res.status(401).json({ message: 'Invalid API key' });
  }
  next();
});

function createRoute(service) {
  return (req, res, next) => {
    const target = getTarget(service);
    if (!target) {
      return res.status(502).json({ message: `No upstream targets for service ${service}` });
    }
    const originalUrl = req.originalUrl;
    req.url = originalUrl.replace(new RegExp('^/' + service), '') || '/';
    proxy.web(req, res, { target, changeOrigin: true });
  };
}

Object.keys(serviceConfig).forEach((service) => {
  app.use(`/${service}`, createRoute(service));
});

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    services: Object.fromEntries(
      Object.entries(serviceConfig).map(([name, targets]) => [name, { targets, nextIndex: counters[name] % targets.length }])
    )
  });
});

app.listen(PORT, () => {
  console.log(`API gateway listening on http://localhost:${PORT}`);
  console.log('Configured services:', serviceConfig);
});
