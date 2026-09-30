import express from 'express';
import compression from 'compression';
import path from 'path';
import { fileURLToPath } from 'url';
import mime from 'mime';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 5000;
const distDir = path.join(__dirname, 'dist');

const app = express();
app.use(compression());

app.use((req, res, next) => {
  res.setHeader('Cache-Control', 'public, max-age=31536000');
  next();
});

app.use(express.static(distDir, {
  setHeaders: (res, filePath) => {
    const type = mime.getType(filePath);
    if (type && type.startsWith('text/')) {
      res.setHeader('Cache-Control', 'public, max-age=3600');
    }
  }
}));

app.get('*', (req, res) => {
  res.sendFile(path.join(distDir, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Content optimizer running on http://localhost:${PORT}`);
});
