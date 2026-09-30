# Twitter Bot Template

This project is a template for a Twitter bot that monitors hashtags and auto-responds to relevant tweets using the `tweepy` library.

## ⚠️ Important: API Keys Required for Live Mode

To connect to Twitter's live service, you need your own set of API keys from the Twitter Developer Portal. This script **cannot work in live mode** without them.

For demonstration and reproducibility, this script runs in a **mock mode** by default. It simulates receiving tweets and shows the bot's logic in the console without needing any keys.

## Features

- **Real-time Monitoring**: Uses the Twitter v2 filtered stream API to monitor tweets containing specific hashtags.
- **Tweet Filtering**: Includes logic to ignore retweets and filter by language.
- **Auto-response**: Posts a reply to tweets that match the criteria.
- **Mock Mode**: A built-in simulation that runs without API keys, making the script's logic fully testable and reproducible.

## How to Use

### 1. Run in Mock Mode (Default)

This is the recommended way to start. It requires no setup.

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    ```bash
    python twitter_bot.py
    ```

You will see output in your console every few seconds, showing the bot processing simulated tweets and printing its intended replies.

### 2. Run in Live Mode

Only do this after you have obtained your own Twitter Developer API keys.

1.  **Get API Keys**: Apply for a developer account and generate your keys at the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard).

2.  **Edit the Script**: Open `twitter_bot.py` and fill in your credentials in the configuration section:
    ```python
    BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"
    API_KEY = "YOUR_API_KEY_HERE"
    API_SECRET = "YOUR_API_SECRET_HERE"
    ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
    ACCESS_TOKEN_SECRET = "YOUR_ACCESS_TOKEN_SECRET_HERE"
    ```

3.  **Switch to Live Mode**: In the same script, change the `USE_MOCK_STREAM` flag to `False`:
    ```python
    USE_MOCK_STREAM = False
    ```

4.  **Run the script:**
    ```bash
    python twitter_bot.py
    ```

The bot will now connect to the live Twitter stream and begin processing real tweets.
