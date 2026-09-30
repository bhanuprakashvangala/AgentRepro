const winston = require('winston');
require('winston-daily-rotate-file');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        // Console transport
        new winston.transports.Console(),

        // File transport with daily rotation
        new winston.transports.DailyRotateFile({
            filename: 'logs/application-%DATE%.log',
            datePattern: 'YYYY-MM-DD-HH',
            zippedArchive: true,
            maxSize: '20m',
            maxFiles: '14d'
        }),

        // HTTP transport (example)
        new winston.transports.Http({
            host: 'localhost',
            port: 8080,
            path: '/logs'
        })
    ]
});

// Example usage
logger.info('This is an informational message.');
logger.warn('This is a warning message.');
logger.error('This is an error message.');

console.log('Logs have been generated.');

// Example of a simple server to receive HTTP logs
const http = require('http');
const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/logs') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            console.log('Received log via HTTP:', body);
            res.writeHead(200, { 'Content-Type': 'text/plain' });
            res.end('Log received');
        });
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

server.listen(8080, () => {
    console.log('HTTP log receiver listening on port 8080');
});
