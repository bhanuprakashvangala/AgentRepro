import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import YAMLFront from 'yaml-front-matter';
import { marked } from 'marked';
import hljs from 'highlight.js';
import RSS from 'rss';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const postsDir = path.join(__dirname, 'posts');
const publicDir = path.join(__dirname, 'public');
const feedPath = path.join(publicDir, 'feed.xml');
const indexPath = path.join(publicDir, 'index.html');

await fs.mkdir(publicDir, { recursive: true });

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  }
});

async function parseMarkdown(filePath) {
  const raw = await fs.readFile(filePath, 'utf-8');
  const parsed = YAMLFront.loadFront(raw);
  const content = parsed.__content || '';
  const html = marked.parse(content);
  const slug = path.basename(filePath, path.extname(filePath));
  return {
    metadata: {
      title: parsed.title || slug,
      date: parsed.date ? new Date(parsed.date) : new Date(),
      description: parsed.description || '',
      tags: parsed.tags || [],
      slug
    },
    html
  };
}

async function buildPosts() {
  const files = await fs.readdir(postsDir);
  const posts = [];
  for (const file of files) {
    if (!file.endsWith('.md') && !file.endsWith('.markdown')) continue;
    const filePath = path.join(postsDir, file);
    try {
      const { metadata, html } = await parseMarkdown(filePath);
      const outputPath = path.join(publicDir, `${metadata.slug}.html`);
      await fs.writeFile(outputPath, wrapWithLayout(metadata.title, html));
      posts.push({ metadata, html });
      console.log(`Built ${outputPath}`);
    } catch (error) {
      console.error(`Failed to build ${file}:`, error.message);
    }
  }
  return posts.sort((a, b) => b.metadata.date - a.metadata.date);
}

function wrapWithLayout(title, bodyHtml) {
  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css">
    <style>
      body { font-family: system-ui, sans-serif; max-width: 768px; margin: 3rem auto; padding: 0 1.5rem; line-height: 1.6; }
      pre { background: #1e293b; padding: 1.25rem; border-radius: 12px; overflow-x: auto; }
    </style>
  </head>
  <body>
    <main>${bodyHtml}</main>
    <p><a href="/index.html">Back to index</a></p>
  </body>
</html>`;
}

function buildIndex(posts) {
  const listItems = posts
    .map(
      ({ metadata }) => `<li>
        <a href="${metadata.slug}.html">${metadata.title}</a>
        <small>${metadata.date.toISOString().split('T')[0]}</small>
        <p>${metadata.description}</p>
      </li>`
    )
    .join('\n');

  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Blog Index</title>
    <style>
      body { font-family: system-ui, sans-serif; max-width: 768px; margin: 3rem auto; padding: 0 1.5rem; }
      li { margin-bottom: 1.5rem; }
      small { color: #64748b; }
    </style>
  </head>
  <body>
    <h1>Blog Posts</h1>
    <ul>${listItems}</ul>
    <p><a href="/feed.xml">RSS Feed</a></p>
  </body>
</html>`;
}

function generateFeed(posts) {
  const feed = new RSS({
    title: 'Markdown Blog',
    description: 'Static blog generated from markdown files',
    site_url: 'https://example.com',
    feed_url: 'https://example.com/feed.xml',
    language: 'en'
  });

  posts.forEach(({ metadata, html }) => {
    feed.item({
      title: metadata.title,
      guid: metadata.slug,
      url: `https://example.com/${metadata.slug}.html`,
      date: metadata.date,
      description: metadata.description,
      custom_elements: [{ 'content:encoded': html }]
    });
  });

  return feed.xml({ indent: true });
}

const posts = await buildPosts();
await fs.writeFile(indexPath, buildIndex(posts));
await fs.writeFile(feedPath, generateFeed(posts));
console.log('Generated index and RSS feed.');
