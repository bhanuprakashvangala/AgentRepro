# Twitter Bot

This project is a Twitter bot that posts scheduled tweets with images.

## Requirements

- Node.js
- npm
- A Twitter developer account with API v2 access.

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Create a `.env` file in the root directory and add your Twitter API credentials:

    ```
    TWITTER_API_KEY=YOUR_API_KEY
    TWITTER_API_SECRET=YOUR_API_SECRET
    TWITTER_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
    TWITTER_ACCESS_TOKEN_SECRET=YOUR_ACCESS_TOKEN_SECRET
    ```

3.  Place an image named `image.jpg` in the root directory.

## Usage

1.  Start the bot:

    ```bash
    npm start
    ```

2.  The bot will post a tweet with the image every day at 10:00 AM.
