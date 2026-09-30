const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const morgan = require('morgan');

const app = express();

// Use morgan for request logging
app.use(morgan('dev'));

// Proxy middleware configuration
const proxy = createProxyMiddleware({
    target: 'http://httpbin.org', // Target host
    changeOrigin: true, // for vhosted sites
    onProxyReq: (proxyReq, req, res) => {
        // Add a custom header to the request
        proxyReq.setHeader('X-Special-Proxy-Header', 'foobar');
    },
    onProxyRes: (proxyRes, req, res) => {
        // Manipulate the response headers
        delete proxyRes.headers['x-powered-by'];
    },
    // Enable CORS
    onProxyRes: (proxyRes, req, res) => {
        proxyRes.headers['Access-Control-Allow-Origin'] = '*';
    }
});

app.use('/', proxy);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Proxy server is running on port ${PORT}`);
});
