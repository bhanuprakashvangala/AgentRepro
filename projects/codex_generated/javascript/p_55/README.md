# Task Runner CLI

Command-line tool using Commander.js with progress indicators from `cli-progress` and `ora`.

## Setup
```bash
npm install
npm link  # optional to use globally as `tasker`
```

## Commands
- `tasker build --steps 10`
- `tasker deploy --target production`
- `tasker backup ./src`
- `tasker clean`

Errors are formatted with detailed messages and non-zero exit codes.
