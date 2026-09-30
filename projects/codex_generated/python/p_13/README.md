# Twitter Hashtag Responder Bot

Monitors specified hashtags in real time using Tweepy, filters tweets by language/user, and auto-replies with a configurable template.

## Setup

1. Create a Twitter developer app and generate the following credentials:
   - `TWITTER_BEARER_TOKEN`
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_SECRET`

2. Export them in your environment (example for macOS/Linux):

```bash
export TWITTER_BEARER_TOKEN="..."
export TWITTER_API_KEY="..."
export TWITTER_API_SECRET="..."
export TWITTER_ACCESS_TOKEN="..."
export TWITTER_ACCESS_SECRET="..."
```

3. Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the bot in dry-run mode first to verify filtering:

```bash
python bot.py --hashtags python,fastapi --languages en --dry-run
```

When ready to send replies, omit `--dry-run` and optionally customize the response template:

```bash
python bot.py \
  --hashtags python,fastapi \
  --languages en \
  --ignore-users spammer123 \
  --reply-template "Hey @{username}, thanks for using #Python!"
```

- `--hashtags`: Comma-separated hashtags to monitor (do not include `#`).
- `--languages`: Restrict tweets to specific language codes (case-insensitive). Leave blank for all languages.
- `--ignore-users`: Comma-separated usernames to exclude from replies.
- `--reply-template`: Text for replies. Use `{username}` placeholder. The bot replies to the original tweet.
- `--dry-run`: Log actions without posting replies.

### Notes
- The script clears existing filtered-stream rules before adding new ones for your hashtags.
- Rate limits and connection errors are handled with simple backoff logging.
- Keep your credentials secure and consider adding additional business logic before deploying to production.
