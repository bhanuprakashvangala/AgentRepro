import tweepy
import time
import random

# --- IMPORTANT: Configuration ---
# To run in LIVE mode, set USE_MOCK_STREAM = False and fill in your Twitter API v2 keys.
# Get keys from https://developer.twitter.com/en/portal/dashboard
USE_MOCK_STREAM = True

BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"
API_KEY = "YOUR_API_KEY_HERE"
API_SECRET = "YOUR_API_SECRET_HERE"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
ACCESS_TOKEN_SECRET = "YOUR_ACCESS_TOKEN_SECRET_HERE"

# --- Bot Settings ---
HASHTAGS_TO_MONITOR = ["#python", "#100DaysOfCode"]
RESPONSE_MESSAGES = [
    "Nice tweet about {hashtag}! Keep up the great work.",
    "Love seeing posts about {hashtag}! Thanks for sharing.",
    "This is a great {hashtag} resource!"
]

# =============================================================================
# --- Mock Objects for Reproducible Demo ---
# =============================================================================

class MockTweet:
    """A mock object to simulate a tweepy.Tweet."""
    def __init__(self, text, author_id, tweet_id):
        self.id = tweet_id
        self.text = text
        self.author_id = author_id
        self.lang = 'en'

class MockAPIClient:
    """A mock object to simulate tweepy.Client for replies."""
    def create_tweet(self, in_reply_to_tweet_id, text):
        print("\n--- MOCK REPLY ---")
        print(f"Replying to Tweet ID: {in_reply_to_tweet_id}")
        print(f"Message: {text}")
        print("------------------")
        # In a real scenario, this would return a response object
        return {"data": {"id": random.randint(1000, 9999), "text": text}}

# =============================================================================
# --- Live Twitter Bot Logic ---
# =============================================================================

def process_tweet(tweet, api_client):
    """Contains the logic for filtering and responding to a tweet."""
    try:
        print(f"\nProcessing Tweet ID: {tweet.id}")
        print(f"From Author ID: {tweet.author_id}")
        print(f"Text: {tweet.text}")

        # --- Filtering Criteria ---
        # 1. Ignore retweets
        if tweet.text.startswith("RT @"):
            print("Filter: Skipping retweet.")
            return

        # 2. Filter by language (optional)
        if tweet.lang != 'en':
            print(f"Filter: Skipping non-English tweet (lang: {tweet.lang}).")
            return

        # --- Response Logic ---
        matched_hashtag = None
        for hashtag in HASHTAGS_TO_MONITOR:
            if hashtag.lower() in tweet.text.lower():
                matched_hashtag = hashtag
                break
        
        if matched_hashtag:
            print(f"Action: Found matching hashtag: {matched_hashtag}")
            response_text = random.choice(RESPONSE_MESSAGES).format(hashtag=matched_hashtag)
            
            # Post the reply
            api_client.create_tweet(in_reply_to_tweet_id=tweet.id, text=response_text)
            print("Action: Reply sent successfully.")
        else:
            print("Filter: No matching hashtags found.")

    except Exception as e:
        print(f"An error occurred during tweet processing: {e}")

class MyStreamingClient(tweepy.StreamingClient):
    """The main streaming client that connects to the live Twitter feed."""
    def __init__(self, bearer_token, **kwargs):
        super().__init__(bearer_token, **kwargs)
        # Initialize the v2 client for sending replies
        self.api_client = tweepy.Client(bearer_token=bearer_token,
                                        consumer_key=API_KEY,
                                        consumer_secret=API_SECRET,
                                        access_token=ACCESS_TOKEN,
                                        access_token_secret=ACCESS_TOKEN_SECRET)

    def on_tweet(self, tweet):
        """This method is called when a new tweet matching the rules is received."""
        process_tweet(tweet, self.api_client)

def run_live_bot():
    """Starts the live Twitter bot."""
    print("--- Starting Live Twitter Bot ---")
    if any(k == "YOUR_BEARER_TOKEN_HERE" for k in [BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("\nERROR: Please fill in your Twitter API keys in the script to run in live mode.")
        return

    streaming_client = MyStreamingClient(BEARER_TOKEN)

    # Clear any existing rules
    rules = streaming_client.get_rules().data
    if rules:
        streaming_client.delete_rules([rule.id for rule in rules])

    # Add new rules to track hashtags
    rule_query = " OR ".join(HASHTAGS_TO_MONITOR) + " -is:retweet"
    streaming_client.add_rules(tweepy.StreamRule(value=rule_query))
    print(f"Rule added: {rule_query}")

    # Start the stream
    streaming_client.filter(tweet_fields=["lang", "author_id"])

def run_mock_bot():
    """Runs a mock version of the bot for demonstration without API keys."""
    print("--- Starting Mock Twitter Bot ---")
    print("This will simulate receiving tweets and show the bot's response logic.")
    mock_api = MockAPIClient()
    
    try:
        while True:
            # Simulate receiving a new tweet
            mock_hashtag = random.choice(HASHTAGS_TO_MONITOR)
            mock_text = f"This is a great tweet about {mock_hashtag}! I love learning new things. #devlife"
            mock_tweet_obj = MockTweet(text=mock_text, author_id=12345, tweet_id=random.randint(10000, 99999))
            
            process_tweet(mock_tweet_obj, mock_api)
            
            # Wait for a few seconds before the next simulated tweet
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n--- Mock Bot Stopped ---")

if __name__ == "__main__":
    if USE_MOCK_STREAM:
        run_mock_bot()
    else:
        run_live_bot()
