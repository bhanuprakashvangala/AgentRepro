const express = require('express');
const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const chokidar = require('chokidar');
const WebSocket = require('ws');

const app = express();
const server = require('http').createServer(app);
const wss = new WebSocket.Server({ server });

const markdownFile = path.join(__dirname, 'document.md');

// Custom CSS for the markdown preview
const customCss = `
    body {
        font-family: sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    pre {
        background-color: #f4f4f4;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    code {
        font-family: monospace;
    }
`;

// Function to render markdown to HTML
const renderMarkdown = () => {
    const markdownContent = fs.readFileSync(markdownFile, 'utf8');
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Markdown Preview</title>
            <style>${customCss}</style>
        </head>
        <body>
            ${marked(markdownContent)}
            <script>
                const ws = new WebSocket('ws://localhost:3000');
                ws.onmessage = (event) => {
                    if (event.data === 'reload') {
                        location.reload();
                    }
                };
            </script>
        </body>
        </html>
    `;
};

// Serve the markdown preview
app.get('/', (req, res) => {
    res.send(renderMarkdown());
});

// Watch for changes in the markdown file
chokidar.watch(markdownFile).on('change', () => {
    console.log('Markdown file changed. Reloading clients...');
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send('reload');
        }
    });
});

// WebSocket for live reload
wss.on('connection', ws => {
    console.log('WebSocket client connected');
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
