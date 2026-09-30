"""
Twitter Bot - Hashtag Monitor and Auto-Responder
Monitors specified hashtags in real-time and responds to tweets based on filters.
"""

import tweepy
import time
import logging
from typing import List, Optional
import os
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TwitterBot:
    """Twitter bot for monitoring hashtags and auto-responding to tweets."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        bearer_token: str
    ):
        """
        Initialize the Twitter bot with API credentials.

        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
            bearer_token: Twitter bearer token
        """
        try:
            # Authenticate using OAuth 1.0a for posting
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_token_secret
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)

            # Authenticate using OAuth 2.0 Bearer Token for v2 endpoints
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )

            # Verify credentials
            user = self.api_v1.verify_credentials()
            logger.info(f"Authentication successful. Bot: @{user.screen_name}")
            self.bot_id = user.id_str

            # Track responded tweets to avoid duplicates
            self.responded_tweets = set()
            self.load_responded_tweets()

        except tweepy.TweepyException as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def load_responded_tweets(self):
        """Load previously responded tweet IDs from file."""
        try:
            if os.path.exists('responded_tweets.json'):
                with open('responded_tweets.json', 'r') as f:
                    data = json.load(f)
                    self.responded_tweets = set(data)
                logger.info(f"Loaded {len(self.responded_tweets)} responded tweet IDs")
        except Exception as e:
            logger.error(f"Error loading responded tweets: {e}")

    def save_responded_tweets(self):
        """Save responded tweet IDs to file."""
        try:
            with open('responded_tweets.json', 'w') as f:
                json.dump(list(self.responded_tweets), f)
        except Exception as e:
            logger.error(f"Error saving responded tweets: {e}")

    def filter_tweet(
        self,
        tweet,
        languages: Optional[List[str]] = None,
        min_followers: int = 0,
        exclude_retweets: bool = True,
        exclude_replies: bool = False
    ) -> bool:
        """
        Filter tweets based on specified criteria.

        Args:
            tweet: Tweet object to filter
            languages: List of language codes (e.g., ['en', 'es'])
            min_followers: Minimum follower count required
            exclude_retweets: Whether to exclude retweets
            exclude_replies: Whether to exclude replies

        Returns:
            True if tweet passes all filters, False otherwise
        """
        try:
            # Check if already responded
            if tweet.id in self.responded_tweets:
                return False

            # Don't respond to own tweets
            if str(tweet.author_id) == self.bot_id:
                return False

            # Language filter
            if languages and hasattr(tweet, 'lang') and tweet.lang not in languages:
                logger.debug(f"Tweet {tweet.id} filtered: language {tweet.lang}")
                return False

            # Retweet filter
            if exclude_retweets and tweet.text.startswith('RT @'):
                logger.debug(f"Tweet {tweet.id} filtered: retweet")
                return False

            # Reply filter
            if exclude_replies and tweet.in_reply_to_user_id:
                logger.debug(f"Tweet {tweet.id} filtered: reply")
                return False

            # Follower count filter (requires user data)
            if min_followers > 0:
                # Note: Would need to fetch user data separately for follower count
                pass

            return True

        except Exception as e:
            logger.error(f"Error filtering tweet: {e}")
            return False

    def generate_response(self, tweet, keyword: str) -> str:
        """
        Generate a response based on the tweet content.

        Args:
            tweet: Tweet object
            keyword: The hashtag/keyword that triggered the response

        Returns:
            Response text
        """
        # Customize these responses based on your use case
        responses = {
            'default': [
                f"Thanks for sharing about {keyword}! 🤖",
                f"Interesting thoughts on {keyword}! 💭",
                f"Great to see discussion about {keyword}! 👍",
            ],
            'python': [
                "Love seeing Python content! 🐍 Check out our resources!",
                "Python is awesome! 🐍 Happy coding!",
            ],
            'coding': [
                "Keep coding! 💻 The community is here to help!",
                "Great coding content! 💪 Keep it up!",
            ]
        }

        # Simple keyword-based response selection
        keyword_lower = keyword.lower().replace('#', '')

        if keyword_lower in responses:
            import random
            return random.choice(responses[keyword_lower])
        else:
            import random
            return random.choice(responses['default'])

    def reply_to_tweet(self, tweet_id: str, reply_text: str, tweet_author: str) -> bool:
        """
        Reply to a specific tweet.

        Args:
            tweet_id: ID of the tweet to reply to
            reply_text: Text of the reply
            tweet_author: Username of the tweet author

        Returns:
            True if successful, False otherwise
        """
        try:
            # Include @mention of original author
            full_reply = f"@{tweet_author} {reply_text}"

            # Post reply using v2 API
            response = self.client.create_tweet(
                text=full_reply,
                in_reply_to_tweet_id=tweet_id
            )

            logger.info(f"Replied to tweet {tweet_id}: {reply_text}")

            # Add to responded tweets
            self.responded_tweets.add(int(tweet_id))
            self.save_responded_tweets()

            return True

        except tweepy.TweepyException as e:
            logger.error(f"Error replying to tweet {tweet_id}: {e}")
            return False

    def monitor_hashtags(
        self,
        hashtags: List[str],
        languages: Optional[List[str]] = ['en'],
        min_followers: int = 0,
        exclude_retweets: bool = True,
        exclude_replies: bool = False,
        max_tweets_per_run: int = 10,
        check_interval: int = 60
    ):
        """
        Monitor specified hashtags and respond to tweets.

        Args:
            hashtags: List of hashtags to monitor (without # symbol)
            languages: List of language codes to filter
            min_followers: Minimum follower count filter
            exclude_retweets: Whether to exclude retweets
            exclude_replies: Whether to exclude replies
            max_tweets_per_run: Maximum tweets to process per check
            check_interval: Seconds to wait between checks
        """
        logger.info(f"Starting to monitor hashtags: {hashtags}")
        logger.info(f"Filters - Languages: {languages}, Min followers: {min_followers}")

        try:
            while True:
                for hashtag in hashtags:
                    try:
                        # Ensure hashtag has # prefix
                        if not hashtag.startswith('#'):
                            hashtag = f'#{hashtag}'

                        logger.info(f"Checking {hashtag}...")

                        # Search for recent tweets with the hashtag
                        tweets = self.client.search_recent_tweets(
                            query=f"{hashtag} -is:retweet" if exclude_retweets else hashtag,
                            max_results=min(100, max_tweets_per_run),
                            tweet_fields=['author_id', 'created_at', 'lang', 'in_reply_to_user_id'],
                            expansions=['author_id'],
                            user_fields=['username', 'public_metrics']
                        )

                        if not tweets.data:
                            logger.info(f"No new tweets found for {hashtag}")
                            continue

                        # Create username lookup
                        users = {user.id: user for user in tweets.includes.get('users', [])}

                        processed_count = 0

                        for tweet in tweets.data:
                            # Apply filters
                            if not self.filter_tweet(
                                tweet,
                                languages=languages,
                                min_followers=min_followers,
                                exclude_retweets=exclude_retweets,
                                exclude_replies=exclude_replies
                            ):
                                continue

                            # Get author username
                            author = users.get(tweet.author_id)
                            if not author:
                                continue

                            # Check follower count if specified
                            if min_followers > 0:
                                follower_count = author.public_metrics.get('followers_count', 0)
                                if follower_count < min_followers:
                                    logger.debug(f"Tweet {tweet.id} filtered: only {follower_count} followers")
                                    continue

                            # Generate and post response
                            response_text = self.generate_response(tweet, hashtag)

                            logger.info(f"Tweet: {tweet.text[:50]}...")
                            logger.info(f"Author: @{author.username} ({author.public_metrics.get('followers_count', 0)} followers)")

                            # Reply to tweet
                            if self.reply_to_tweet(str(tweet.id), response_text, author.username):
                                processed_count += 1

                                # Rate limiting - wait between responses
                                time.sleep(5)

                            if processed_count >= max_tweets_per_run:
                                break

                        logger.info(f"Processed {processed_count} tweets for {hashtag}")

                    except tweepy.TweepyException as e:
                        logger.error(f"Error processing hashtag {hashtag}: {e}")
                        continue

                logger.info(f"Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise


def main():
    """Main function to run the Twitter bot."""

    # Load credentials from environment variables
    API_KEY = os.getenv('TWITTER_API_KEY')
    API_SECRET = os.getenv('TWITTER_API_SECRET')
    ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

    # Validate credentials
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]):
        logger.error("Missing Twitter API credentials. Please set environment variables:")
        logger.error("TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN,")
        logger.error("TWITTER_ACCESS_TOKEN_SECRET, TWITTER_BEARER_TOKEN")
        return

    try:
        # Initialize bot
        bot = TwitterBot(
            api_key=API_KEY,
            api_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET,
            bearer_token=BEARER_TOKEN
        )

        # Configure monitoring parameters
        hashtags_to_monitor = ['python', 'coding', 'programming']  # Customize these

        # Start monitoring
        bot.monitor_hashtags(
            hashtags=hashtags_to_monitor,
            languages=['en'],  # English only
            min_followers=10,  # Minimum 10 followers
            exclude_retweets=True,
            exclude_replies=False,
            max_tweets_per_run=5,  # Process max 5 tweets per hashtag per check
            check_interval=300  # Check every 5 minutes (300 seconds)
        )

    except Exception as e:
        logger.error(f"Bot failed to start: {e}")


if __name__ == '__main__':
    main()
