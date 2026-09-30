import 'dotenv/config';
import cron from 'node-cron';
import { readFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { TwitterApi, ETwitterApiError } from 'twitter-api-v2';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const client = new TwitterApi({
  appKey: process.env.TWITTER_APP_KEY,
  appSecret: process.env.TWITTER_APP_SECRET,
  accessToken: process.env.TWITTER_ACCESS_TOKEN,
  accessSecret: process.env.TWITTER_ACCESS_SECRET
});

const rwClient = client.readWrite;

if (!process.env.TWEET_CRON) {
  console.error('TWEET_CRON cron expression is required');
  process.exit(1);
}

async function sendTweet({ text, mediaPath }) {
  try {
    let mediaId;
    if (mediaPath) {
      const absolutePath = path.isAbsolute(mediaPath) ? mediaPath : path.join(__dirname, mediaPath);
      const fileData = await readFile(absolutePath);
      mediaId = await rwClient.v1.uploadMedia(fileData, { type: 'image' });
    }
    const payload = mediaId ? { text, media: { media_ids: [mediaId] } } : { text };
    const tweet = await rwClient.v2.tweet(payload);
    console.log(`Tweet posted: https://twitter.com/i/web/status/${tweet.data.id}`);
  } catch (error) {
    if (error instanceof ETwitterApiError) {
      console.error('Twitter API error:', error.message, error.code, error.data);
      if (error.rateLimitError) {
        console.error(`Rate limit hit. Reset at ${new Date(error.rateLimit.reset * 1000).toISOString()}`);
      }
    } else {
      console.error('Unexpected error:', error);
    }
  }
}

function loadSchedule() {
  try {
    const filePath = path.join(__dirname, 'schedule.json');
    const raw = new URL('file://' + filePath);
    return JSON.parse(readFile(new URL(raw), 'utf-8'));
  } catch (error) {
    console.warn('schedule.json not found or invalid. Using fallback tweet.');
    return [{ text: 'Hello world! #MyBot' }];
  }
}

async function dispatchTweet() {
  const schedule = await loadSchedule();
  const item = schedule[Math.floor(Math.random() * schedule.length)];
  await sendTweet(item);
}

cron.schedule(process.env.TWEET_CRON, () => {
  dispatchTweet().catch((error) => console.error('Dispatch failed:', error));
});

console.log('Twitter bot scheduled with cron:', process.env.TWEET_CRON);
