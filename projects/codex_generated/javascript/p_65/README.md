# Twitter Scheduled Bot

Tweets messages (with optional media) on a cron schedule using Twitter API v2 and `node-cron`.

## Setup
```bash
npm install
```
Set environment variables (or `.env` file):
```
TWITTER_APP_KEY=...
TWITTER_APP_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
TWEET_CRON=*/30 * * * *
```
Optionally set `TZ` for timezone.

## Usage
Populate `schedule.json` with entries:
```
[
  { "text": "Automated tweet", "mediaPath": "media/sample-image.jpg" }
]
```
Then run:
```bash
npm start
```

Ensure media files exist if referenced. The bot logs rate-limit information if API quotas are exceeded.
