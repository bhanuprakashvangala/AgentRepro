const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// Microservice configurations
const services = {
    users: [
        'http://localhost:3001',
        'http://localhost:3002'
    ],
    products: [
        'http://localhost:3003'
    ]
};

// Simple round-robin load balancer
const loadBalancer = (serviceName) => {
    let i = 0;
    return (req, res, next) => {
        const serviceInstances = services[serviceName];
        if (!serviceInstances || serviceInstances.length === 0) {
            return res.status(503).send('Service unavailable');
        }
        const target = serviceInstances[i];
        i = (i + 1) % serviceInstances.length;
        createProxyMiddleware({ target, changeOrigin: true })(req, res, next);
    };
};

// Authentication middleware (simple example)
const authenticate = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    if (authHeader === 'Bearer mysecrettoken') {
        next();
    } else {
        res.status(401).send('Unauthorized');
    }
};

// Routes
app.use('/users', authenticate, loadBalancer('users'));
app.use('/products', authenticate, loadBalancer('products'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`API Gateway is running on port ${PORT}`);
});
