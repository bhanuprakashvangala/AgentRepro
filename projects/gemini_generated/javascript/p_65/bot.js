require('dotenv').config();
const { TwitterApi } = require('twitter-api-v2');
const cron = require('node-cron');

const client = new TwitterApi({
    appKey: process.env.TWITTER_API_KEY,
    appSecret: process.env.TWITTER_API_SECRET,
    accessToken: process.env.TWITTER_ACCESS_TOKEN,
    accessSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
});

const postTweet = async () => {
    try {
        // Upload media
        const mediaId = await client.v1.uploadMedia('./image.jpg');

        // Post tweet with media
        await client.v2.tweet('Hello, Twitter! This is a scheduled tweet with an image.', {
            media: {
                media_ids: [mediaId]
            }
        });
        console.log('Tweet posted successfully');
    } catch (error) {
        console.error('Error posting tweet:', error);
    }
};

// Schedule a tweet to be posted every day at 10:00 AM
cron.schedule('0 10 * * *', () => {
    console.log('Running scheduled tweet job');
    postTweet();
});

console.log('Twitter bot started. Scheduled to post a tweet every day at 10:00 AM.');
