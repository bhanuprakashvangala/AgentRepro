const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const hljs = require('highlight.js');
const RSS = require('rss');

const postsDir = path.join(__dirname, 'posts');
const publicDir = path.join(__dirname, 'public');

// Configure marked
marked.setOptions({
    highlight: function (code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    }
});

// Create public directory if it doesn't exist
if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir);
}

// Read posts
const posts = fs.readdirSync(postsDir).map(file => {
    const filePath = path.join(postsDir, file);
    const content = fs.readFileSync(filePath, 'utf8');
    const [_, frontmatter, markdown] = content.split('---');
    const { title, date } = JSON.parse(frontmatter.replace(/\n/g, ' ').replace(/(\w+):/g, '"$1":'));

    return {
        file,
        title,
        date,
        html: marked(markdown)
    };
});

// Generate HTML files
posts.forEach(post => {
    const postHtml = "
        <!DOCTYPE html>
        <html>
        <head>
            <title>${post.title}</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
        </head>
        <body>
            <h1>${post.title}</h1>
            <p>${post.date}</p>
            ${post.html}
        </body>
        </html>
    ";
    fs.writeFileSync(path.join(publicDir, `${post.file.replace('.md', '.html')}`), postHtml);
});

// Generate RSS feed
const feed = new RSS({
    title: 'My Blog',
    feed_url: 'http://example.com/rss.xml',
    site_url: 'http://example.com'
});

posts.forEach(post => {
    feed.item({
        title: post.title,
        description: post.html,
        url: `http://example.com/${post.file.replace('.md', '.html')}`,
        date: post.date
    });
});

const xml = feed.xml({ indent: true });
fs.writeFileSync(path.join(publicDir, 'rss.xml'), xml);

console.log('Blog built successfully!');
