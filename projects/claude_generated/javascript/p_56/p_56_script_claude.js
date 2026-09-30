import fs from 'fs';
import path from 'path';
import { marked } from 'marked';
import hljs from 'highlight.js';
import RSS from 'rss';

// Configure marked with highlight.js
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (err) {
        console.error('Highlighting error:', err);
      }
    }
    return hljs.highlightAuto(code).value;
  },
  langPrefix: 'hljs language-',
  breaks: false,
  gfm: true
});

class BlogEngine {
  constructor(config = {}) {
    this.postsDir = config.postsDir || './posts';
    this.outputDir = config.outputDir || './output';
    this.siteUrl = config.siteUrl || 'https://example.com';
    this.siteTitle = config.siteTitle || 'My Blog';
    this.siteDescription = config.siteDescription || 'A blog powered by Markdown';
    this.posts = [];
  }

  // Parse markdown file with frontmatter
  parseMarkdownFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const frontmatterRegex = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
    const match = content.match(frontmatterRegex);

    let metadata = {};
    let markdown = content;

    if (match) {
      const frontmatter = match[1];
      markdown = match[2];

      // Parse frontmatter (simple YAML-like parsing)
      frontmatter.split('\n').forEach(line => {
        const [key, ...valueParts] = line.split(':');
        if (key && valueParts.length) {
          metadata[key.trim()] = valueParts.join(':').trim();
        }
      });
    }

    return { metadata, markdown };
  }

  // Generate HTML template
  generateHTML(title, content, styles = '') {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #0d1117;
            color: #c9d1d9;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #58a6ff;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        a {
            color: #58a6ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        pre {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
        }
        code {
            background: #161b22;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre code {
            background: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #58a6ff;
            padding-left: 16px;
            color: #8b949e;
            margin: 0;
        }
        .post-meta {
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        .back-link {
            margin-bottom: 20px;
            display: inline-block;
        }
        .post-list {
            list-style: none;
            padding: 0;
        }
        .post-list li {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #30363d;
        }
        .post-list li:last-child {
            border-bottom: none;
        }
        ${styles}
    </style>
</head>
<body>
    ${content}
</body>
</html>`;
  }

  // Build all posts
  build() {
    // Create output directory
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }

    // Create posts directory if it doesn't exist
    if (!fs.existsSync(this.postsDir)) {
      fs.mkdirSync(this.postsDir, { recursive: true });
      console.log(`Created posts directory at ${this.postsDir}`);
      console.log('Add your markdown files to this directory and run again.');
      return;
    }

    // Read all markdown files
    const files = fs.readdirSync(this.postsDir)
      .filter(file => file.endsWith('.md'));

    if (files.length === 0) {
      console.log('No markdown files found in posts directory.');
      return;
    }

    // Process each post
    files.forEach(file => {
      const filePath = path.join(this.postsDir, file);
      const { metadata, markdown } = this.parseMarkdownFile(filePath);

      const html = marked(markdown);
      const slug = file.replace('.md', '');
      const title = metadata.title || slug;
      const date = metadata.date || new Date().toISOString().split('T')[0];
      const author = metadata.author || 'Anonymous';
      const description = metadata.description || '';

      const postHTML = this.generateHTML(
        title,
        `
        <a href="../index.html" class="back-link">← Back to Home</a>
        <article>
            <h1>${title}</h1>
            <div class="post-meta">
                <span>Published: ${date}</span>
                ${author ? ` | <span>Author: ${author}</span>` : ''}
            </div>
            ${html}
        </article>
        `
      );

      const outputPath = path.join(this.outputDir, `${slug}.html`);
      fs.writeFileSync(outputPath, postHTML);

      this.posts.push({
        title,
        slug,
        date,
        author,
        description,
        url: `${this.siteUrl}/${slug}.html`
      });

      console.log(`✓ Generated: ${slug}.html`);
    });

    // Sort posts by date (newest first)
    this.posts.sort((a, b) => new Date(b.date) - new Date(a.date));

    // Generate index page
    this.generateIndex();

    // Generate RSS feed
    this.generateRSS();

    console.log('\n✓ Build complete!');
    console.log(`  Posts: ${this.posts.length}`);
    console.log(`  Output: ${this.outputDir}/`);
  }

  // Generate index page
  generateIndex() {
    const postList = this.posts.map(post => `
      <li>
        <h2><a href="${post.slug}.html">${post.title}</a></h2>
        <div class="post-meta">
          <span>${post.date}</span>
          ${post.author ? ` | <span>${post.author}</span>` : ''}
        </div>
        ${post.description ? `<p>${post.description}</p>` : ''}
      </li>
    `).join('');

    const indexHTML = this.generateHTML(
      this.siteTitle,
      `
      <header>
        <h1>${this.siteTitle}</h1>
        <p>${this.siteDescription}</p>
        <p><a href="feed.xml">RSS Feed</a></p>
      </header>
      <main>
        <ul class="post-list">
          ${postList || '<li>No posts yet.</li>'}
        </ul>
      </main>
      `
    );

    fs.writeFileSync(path.join(this.outputDir, 'index.html'), indexHTML);
    console.log('✓ Generated: index.html');
  }

  // Generate RSS feed
  generateRSS() {
    const feed = new RSS({
      title: this.siteTitle,
      description: this.siteDescription,
      feed_url: `${this.siteUrl}/feed.xml`,
      site_url: this.siteUrl,
      language: 'en',
      pubDate: new Date()
    });

    this.posts.forEach(post => {
      feed.item({
        title: post.title,
        description: post.description,
        url: post.url,
        date: post.date,
        author: post.author
      });
    });

    const xml = feed.xml({ indent: true });
    fs.writeFileSync(path.join(this.outputDir, 'feed.xml'), xml);
    console.log('✓ Generated: feed.xml');
  }
}

// Run the blog engine
const blog = new BlogEngine({
  postsDir: './posts',
  outputDir: './output',
  siteUrl: 'https://example.com',
  siteTitle: 'My Markdown Blog',
  siteDescription: 'A blog with syntax highlighting'
});

blog.build();
