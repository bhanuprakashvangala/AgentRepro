const fs = require('fs');
const path = require('path');

const express = require('express');
const chokidar = require('chokidar');
const { marked } = require('marked');

const app = express();
const port = process.env.PORT || 3000;
const rootDir = __dirname;
const contentDir = path.resolve(rootDir, 'content');
const defaultFile = process.env.MARKDOWN_FILE
  ? path.resolve(contentDir, process.env.MARKDOWN_FILE)
  : path.resolve(contentDir, 'example.md');

const clients = new Set();

function ensureContentDir() {
  if (!fs.existsSync(contentDir)) {
    throw new Error(`Content directory not found: ${contentDir}`);
  }
  if (!fs.existsSync(defaultFile)) {
    throw new Error(`Default markdown file not found: ${defaultFile}`);
  }
}

function safeResolveMarkdown(fileName) {
  const resolved = path.resolve(contentDir, fileName);
  if (!resolved.startsWith(contentDir)) {
    throw new Error('Invalid markdown file path');
  }
  return resolved;
}

async function renderMarkdown(filePath) {
  const data = await fs.promises.readFile(filePath, 'utf8');
  return marked.parse(data);
}

app.use(express.static(path.join(rootDir, 'public')));

app.get('/api/files', async (_req, res) => {
  try {
    const entries = await fs.promises.readdir(contentDir);
    const files = entries.filter((name) => name.toLowerCase().endsWith('.md')).sort();
    res.json({ files });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/render', async (req, res) => {
  try {
    const requested = req.query.file || path.relative(contentDir, defaultFile);
    const filePath = safeResolveMarkdown(requested);
    const html = await renderMarkdown(filePath);
    res.json({ html, file: path.relative(contentDir, filePath) });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  res.write('retry: 1000\n\n');

  clients.add(res);
  req.on('close', () => {
    clients.delete(res);
  });
});

function broadcastReload(changedFile) {
  const payload = JSON.stringify({ file: path.relative(contentDir, changedFile) });
  for (const client of clients) {
    client.write(`data: ${payload}\n\n`);
  }
}

function startWatcher() {
  const watcher = chokidar.watch('**/*.md', {
    cwd: contentDir,
    ignoreInitial: false,
  });

  watcher.on('change', (file) => {
    console.log(`Markdown updated: ${file}`);
    broadcastReload(path.resolve(contentDir, file));
  });

  watcher.on('add', (file) => {
    console.log(`Markdown added: ${file}`);
    broadcastReload(path.resolve(contentDir, file));
  });

  watcher.on('unlink', (file) => {
    console.log(`Markdown removed: ${file}`);
    broadcastReload(path.resolve(contentDir, file));
  });
}

async function start() {
  ensureContentDir();
  startWatcher();
  app.listen(port, () => {
    console.log(`Markdown preview server running at http://localhost:${port}`);
    console.log(`Watching directory: ${contentDir}`);
  });
}

start().catch((err) => {
  console.error(err);
  process.exit(1);
});
