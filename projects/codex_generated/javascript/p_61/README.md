# Bull Job Queue Demo

Uses [Bull](https://github.com/OptimalBits/bull) with Redis to enqueue jobs and process them asynchronously with retries and progress events.

## Setup
Ensure Redis is running (default `redis://127.0.0.1:6379`). Optionally set `REDIS_URL` env.

```bash
npm install
```

## Enqueue Jobs
```bash
npm run producer
```

## Run Worker
```bash
npm run worker
```

Console outputs show progress (`job.progress()`), completion results, and retries for failures. Customize job processors in `worker.js` and add additional queue listeners as needed for monitoring.
