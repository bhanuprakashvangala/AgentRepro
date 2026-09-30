# File Watcher

CLI utility using `chokidar` to watch directories recursively and emit debounced logs on file events.

## Setup
```bash
npm install
```

## Usage
```bash
node watcher.js --paths ./src ./config --debounce 500 --ignore "**/*.tmp"
```

- `--paths/-p`: one or more directories/files to watch.
- `--debounce/-d`: milliseconds to debounce rapid events (default 300).
- `--ignore/-i`: glob patterns to ignore (defaults to `node_modules` and `.git`).

Console output example:
```
[ADD]    src/newFile.js
[CHANGE] src/app.js
[DELETE] src/oldFile.js
```

Use the callback blocks to trigger additional actions (build, tests, etc.). Debouncing prevents redundant triggers from rapid successive changes.
