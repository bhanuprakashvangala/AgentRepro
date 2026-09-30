# Markdown Blog Engine

Converts markdown posts (with YAML front matter) into static HTML files with syntax highlighting. Generates an RSS feed.

## Setup
```bash
npm install
```

## Usage
Place markdown files in `posts/` (see `posts/hello-world.md` for reference). Then run:
```bash
npm run build
```

Output:
- `public/*.html` – rendered posts
- `public/index.html` – listing with links
- `public/feed.xml` – RSS feed

Routes assume deployment under `https://example.com`; adjust feed URLs in `build.js` for production.
