# Markdown Preview Server

Live-reloading Markdown previewer built with Node.js, Express, marked, and chokidar. Point it at the bundled `content` directory (or supply your own) and watch the browser refresh whenever you save changes.

## Features
- Renders Markdown to HTML server-side using `marked`
- Watches all `.md` files in `content/` via `chokidar`
- Streams change notifications to the browser with Server-Sent Events for instant refresh
- Includes a polished sidebar, file picker, and custom typography styling

## Prerequisites
- Node.js 18 or newer (for native ECMAScript module support and `fs/promises`)

## Install & Run
```bash
cd 1-GPT/p_73
npm install
npm start
```

Then open http://localhost:3000 in your browser. The server watches the `content` directory relative to the project root.

## Usage
- Edit any `.md` file in `content/` (e.g., `content/example.md`)
- The server converts Markdown to HTML with `marked`
- The browser updates automatically thanks to SSE/live reload
- Add additional markdown files to `content/`; they appear in the sidebar list without restarting

You can override the port or default file when starting the server:
```bash
PORT=5000 MARKDOWN_FILE=notes.md npm start
```

## Stop
Press `Ctrl+C` in the terminal to stop the server.
