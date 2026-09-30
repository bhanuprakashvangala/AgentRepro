import express from 'express';
import morgan from 'morgan';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';

const TARGET = process.env.TARGET_URL || 'https://httpbin.org';
const PORT = process.env.PORT || 5050;

const app = express();

app.use(cors({ origin: true, credentials: true }));

morgan.token('body', (req) => JSON.stringify(req.body || {}));
app.use(express.json());
app.use(morgan(':method :url :status :res[content-length] - :response-time ms :body'));

app.use(
  '/',
  createProxyMiddleware({
    target: TARGET,
    changeOrigin: true,
    selfHandleResponse: false,
    onProxyReq(proxyReq, req, res) {
      proxyReq.setHeader('X-Proxy-By', 'CustomProxy');
    },
    onProxyRes(proxyRes, req, res) {
      console.log(`Proxy response: ${proxyRes.statusCode} for ${req.method} ${req.url}`);
    }
  })
);

app.listen(PORT, () => {
  console.log(`Proxy server running on http://localhost:${PORT} forwarding to ${TARGET}`);
});
