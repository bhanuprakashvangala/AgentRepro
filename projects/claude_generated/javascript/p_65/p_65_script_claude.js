import { TwitterApi } from 'twitter-api-v2';
import cron from 'node-cron';
import { readFileSync } from 'fs';
import dotenv from 'dotenv';

dotenv.config();

// Initialize Twitter client
const client = new TwitterApi({
  appKey: process.env.TWITTER_API_KEY,
  appSecret: process.env.TWITTER_API_SECRET,
  accessToken: process.env.TWITTER_ACCESS_TOKEN,
  accessSecret: process.env.TWITTER_ACCESS_SECRET,
});

const rwClient = client.readWrite;

// Rate limit handler with exponential backoff
class RateLimitHandler {
  constructor() {
    this.retryAfter = null;
    this.retryCount = 0;
    this.maxRetries = 3;
  }

  async executeWithRetry(fn, context = 'API call') {
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        // Check if we're in a rate limit cooldown
        if (this.retryAfter && Date.now() < this.retryAfter) {
          const waitTime = this.retryAfter - Date.now();
          console.log(`⏳ Rate limited. Waiting ${Math.ceil(waitTime / 1000)}s before ${context}...`);
          await this.sleep(waitTime);
        }

        const result = await fn();
        this.retryCount = 0; // Reset on success
        this.retryAfter = null;
        return result;

      } catch (error) {
        if (error.code === 429 || error.rateLimit) {
          // Rate limit hit
          const resetTime = error.rateLimit?.reset
            ? error.rateLimit.reset * 1000
            : Date.now() + (Math.pow(2, attempt) * 60000); // Exponential backoff: 1min, 2min, 4min

          this.retryAfter = resetTime;
          const waitTime = resetTime - Date.now();

          console.error(`❌ Rate limit exceeded for ${context}`);
          console.log(`   Limit: ${error.rateLimit?.limit || 'unknown'}`);
          console.log(`   Remaining: ${error.rateLimit?.remaining || 0}`);
          console.log(`   Reset: ${new Date(resetTime).toLocaleString()}`);

          if (attempt < this.maxRetries) {
            console.log(`   Retry attempt ${attempt + 1}/${this.maxRetries} in ${Math.ceil(waitTime / 1000)}s...`);
            await this.sleep(waitTime);
            continue;
          } else {
            throw new Error(`Max retries (${this.maxRetries}) exceeded for ${context}`);
          }
        } else {
          // Non-rate-limit error
          throw error;
        }
      }
    }
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

const rateLimitHandler = new RateLimitHandler();

// Tweet with text only
async function postTweet(text) {
  try {
    const result = await rateLimitHandler.executeWithRetry(
      async () => await rwClient.v2.tweet(text),
      'posting tweet'
    );

    console.log('✅ Tweet posted successfully!');
    console.log(`   Tweet ID: ${result.data.id}`);
    console.log(`   Text: ${result.data.text}`);
    return result;
  } catch (error) {
    console.error('❌ Failed to post tweet:', error.message);
    if (error.data) {
      console.error('   Details:', JSON.stringify(error.data, null, 2));
    }
    throw error;
  }
}

// Tweet with media (images)
async function postTweetWithMedia(text, mediaPath) {
  try {
    console.log(`📤 Uploading media: ${mediaPath}`);

    // Upload media
    const mediaId = await rateLimitHandler.executeWithRetry(
      async () => {
        const mediaBuffer = readFileSync(mediaPath);
        return await rwClient.v1.uploadMedia(mediaBuffer, {
          mimeType: 'image/jpeg' // Supports: image/jpeg, image/png, image/gif, image/webp
        });
      },
      'uploading media'
    );

    console.log(`✅ Media uploaded. Media ID: ${mediaId}`);

    // Post tweet with media
    const result = await rateLimitHandler.executeWithRetry(
      async () => await rwClient.v2.tweet({
        text: text,
        media: { media_ids: [mediaId] }
      }),
      'posting tweet with media'
    );

    console.log('✅ Tweet with media posted successfully!');
    console.log(`   Tweet ID: ${result.data.id}`);
    console.log(`   Text: ${result.data.text}`);
    return result;
  } catch (error) {
    console.error('❌ Failed to post tweet with media:', error.message);
    if (error.data) {
      console.error('   Details:', JSON.stringify(error.data, null, 2));
    }
    throw error;
  }
}

// Tweet with multiple images (up to 4)
async function postTweetWithMultipleMedia(text, mediaPaths) {
  try {
    console.log(`📤 Uploading ${mediaPaths.length} media files...`);

    // Upload all media files
    const mediaIds = [];
    for (const mediaPath of mediaPaths.slice(0, 4)) { // Twitter allows max 4 images
      const mediaId = await rateLimitHandler.executeWithRetry(
        async () => {
          const mediaBuffer = readFileSync(mediaPath);
          return await rwClient.v1.uploadMedia(mediaBuffer, {
            mimeType: 'image/jpeg'
          });
        },
        `uploading media: ${mediaPath}`
      );
      mediaIds.push(mediaId);
      console.log(`✅ Uploaded: ${mediaPath} (ID: ${mediaId})`);
    }

    // Post tweet with all media
    const result = await rateLimitHandler.executeWithRetry(
      async () => await rwClient.v2.tweet({
        text: text,
        media: { media_ids: mediaIds }
      }),
      'posting tweet with multiple media'
    );

    console.log('✅ Tweet with multiple media posted successfully!');
    console.log(`   Tweet ID: ${result.data.id}`);
    console.log(`   Text: ${result.data.text}`);
    console.log(`   Media count: ${mediaIds.length}`);
    return result;
  } catch (error) {
    console.error('❌ Failed to post tweet with multiple media:', error.message);
    if (error.data) {
      console.error('   Details:', JSON.stringify(error.data, null, 2));
    }
    throw error;
  }
}

// Schedule Configuration
const scheduledTweets = [
  {
    schedule: '0 9 * * *', // Every day at 9:00 AM
    content: {
      text: '🌅 Good morning! Starting the day with positive vibes! #GoodMorning',
      type: 'text'
    }
  },
  {
    schedule: '0 12 * * *', // Every day at 12:00 PM
    content: {
      text: '🍕 Lunch time! What\'s everyone having today?',
      type: 'text'
    }
  },
  {
    schedule: '0 18 * * *', // Every day at 6:00 PM
    content: {
      text: '🌆 Evening update with an image!',
      type: 'media',
      mediaPath: './images/evening.jpg' // Make sure this file exists
    }
  },
  {
    schedule: '0 21 * * 1', // Every Monday at 9:00 PM
    content: {
      text: '📊 Weekly recap with multiple images!',
      type: 'multiple-media',
      mediaPaths: ['./images/img1.jpg', './images/img2.jpg'] // Make sure these exist
    }
  },
  {
    schedule: '*/5 * * * *', // Every 5 minutes (for testing)
    content: {
      text: `🤖 Automated tweet at ${new Date().toLocaleString()}`,
      type: 'text'
    },
    enabled: false // Set to true to enable this test schedule
  }
];

// Initialize scheduled tasks
function initializeScheduler() {
  console.log('🚀 Twitter Bot Scheduler Started!');
  console.log('⏰ Configured schedules:\n');

  scheduledTweets.forEach((tweet, index) => {
    // Skip if explicitly disabled
    if (tweet.enabled === false) {
      console.log(`⏭️  Schedule ${index + 1}: ${tweet.schedule} - DISABLED`);
      return;
    }

    console.log(`✓ Schedule ${index + 1}: ${tweet.schedule}`);
    console.log(`  Type: ${tweet.content.type}`);
    console.log(`  Text: ${tweet.content.text.substring(0, 50)}...`);
    console.log('');

    // Create cron job
    cron.schedule(tweet.schedule, async () => {
      console.log(`\n⏰ [${new Date().toLocaleString()}] Triggered scheduled tweet`);

      try {
        if (tweet.content.type === 'text') {
          await postTweet(tweet.content.text);
        } else if (tweet.content.type === 'media') {
          await postTweetWithMedia(tweet.content.text, tweet.content.mediaPath);
        } else if (tweet.content.type === 'multiple-media') {
          await postTweetWithMultipleMedia(tweet.content.text, tweet.content.mediaPaths);
        }
      } catch (error) {
        console.error('❌ Scheduled tweet failed:', error.message);
      }
    });
  });

  console.log('✅ All schedules initialized. Bot is now running...\n');
}

// Verify credentials on startup
async function verifyCredentials() {
  try {
    console.log('🔐 Verifying Twitter API credentials...');
    const user = await rwClient.v2.me();
    console.log(`✅ Authenticated as: @${user.data.username} (${user.data.name})`);
    console.log(`   User ID: ${user.data.id}\n`);
    return true;
  } catch (error) {
    console.error('❌ Authentication failed:', error.message);
    console.error('   Please check your credentials in .env file\n');
    return false;
  }
}

// Main execution
async function main() {
  const isAuthenticated = await verifyCredentials();

  if (!isAuthenticated) {
    console.error('⚠️  Bot cannot start without valid credentials.');
    process.exit(1);
  }

  initializeScheduler();

  // Keep the process running
  process.on('SIGINT', () => {
    console.log('\n\n👋 Shutting down bot gracefully...');
    process.exit(0);
  });
}

// Start the bot
main().catch(error => {
  console.error('💥 Fatal error:', error);
  process.exit(1);
});

// Export functions for external use
export { postTweet, postTweetWithMedia, postTweetWithMultipleMedia };
