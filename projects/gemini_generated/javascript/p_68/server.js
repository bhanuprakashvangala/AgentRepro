const express = require('express');
const compression = require('compression');
const minify = require('minify');
const imagemin = require('imagemin');
const imageminJpegtran = require('imagemin-jpegtran');
const path = require('path');

const app = express();

// Compression middleware
app.use(compression());

// Caching headers
app.use((req, res, next) => {
    res.set('Cache-Control', 'public, max-age=31536000'); // 1 year
    next();
});

// Minify CSS and JS
app.use('*.css', async (req, res, next) => {
    try {
        const minified = await minify(path.join(__dirname, 'public', req.originalUrl));
        res.set('Content-Type', 'text/css');
        res.send(minified);
    } catch (e) {
        next();
    }
});

app.use('*.js', async (req, res, next) => {
    try {
        const minified = await minify(path.join(__dirname, 'public', req.originalUrl));
        res.set('Content-Type', 'application/javascript');
        res.send(minified);
    } catch (e) {
        next();
    }
});

// Optimize images
app.use('*.jpg', async (req, res, next) => {
    try {
        const buffer = await imagemin([path.join(__dirname, 'public', req.originalUrl)], {
            plugins: [
                imageminJpegtran()
            ]
        });
        res.set('Content-Type', 'image/jpeg');
        res.send(buffer[0].data);
    } catch (e) {
        next();
    }
});

// Serve static files
app.use(express.static('public'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
