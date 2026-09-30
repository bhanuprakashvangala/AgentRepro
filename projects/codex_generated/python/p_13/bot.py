#!/usr/bin/env python3
"""Twitter hashtag monitor and responder using Tweepy."""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Set

import tweepy

logger = logging.getLogger("twitter_bot")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@dataclass(frozen=True)
class BotConfig:
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: str
    hashtags: Sequence[str]
    languages: Set[str]
    ignore_users: Set[str]
    reply_template: str
    dry_run: bool


class HashtagStream(tweepy.StreamingClient):
    """Streaming client that feeds tweets to a handler callback."""

    def __init__(self, bearer_token: str, handler, *, wait_on_rate_limit: bool = True) -> None:
        super().__init__(bearer_token, wait_on_rate_limit=wait_on_rate_limit)
        self._handler = handler

    def on_tweet(self, tweet: tweepy.Tweet) -> None:  # type: ignore[override]
        try:
            self._handler(tweet)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Failed to process tweet %s: %s", getattr(tweet, "id", "<unknown>"), exc)

    def on_connection_error(self) -> None:  # type: ignore[override]
        logger.warning("Connection error encountered. Reconnecting in 10 seconds...")
        time.sleep(10)
        self.disconnect()

    def on_request_error(self, status_code: int) -> None:  # type: ignore[override]
        logger.error("Stream request error: status=%s", status_code)
        if status_code in {420, 429, 503}:
            backoff = 60
            logger.info("Backing off for %s seconds due to rate limits/service issues.", backoff)
            time.sleep(backoff)
        else:
            time.sleep(5)


class TwitterBot:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.client = tweepy.Client(
            consumer_key=config.consumer_key,
            consumer_secret=config.consumer_secret,
            access_token=config.access_token,
            access_token_secret=config.access_token_secret,
            bearer_token=config.bearer_token,
            wait_on_rate_limit=True,
        )
        self.stream = HashtagStream(config.bearer_token, self.handle_tweet)
        self._setup_stream_rules()

    def _setup_stream_rules(self) -> None:
        existing_rules = self.stream.get_rules()
        if existing_rules and existing_rules.data:
            logger.info("Clearing existing stream rules (%s)", len(existing_rules.data))
            self.stream.delete_rules([rule.id for rule in existing_rules.data])

        hashtag_query = " OR ".join(f"#{tag}" for tag in self.config.hashtags)
        query = f"({hashtag_query})"
        query += " -is:retweet -is:reply"
        if self.config.languages:
            lang_query = " OR ".join(f"lang:{lang.lower()}" for lang in self.config.languages)
            query += f" ({lang_query})"
        logger.info("Adding stream rule: %s", query)
        self.stream.add_rules(tweepy.StreamRule(query))

    def start(self) -> None:
        logger.info(
            "Starting stream. Monitoring hashtags: %s", ", ".join(f"#{tag}" for tag in self.config.hashtags)
        )
        self.stream.filter(expansions=["author_id"], tweet_fields=["lang", "author_id", "created_at"], threaded=True)

    def stop(self) -> None:
        logger.info("Stopping stream...")
        self.stream.disconnect()

    def handle_tweet(self, tweet: tweepy.Tweet) -> None:
        if not tweet.author_id:
            logger.debug("Skipping tweet without author: %s", tweet.id)
            return

        username = self._resolve_username(tweet.author_id)
        if not username:
            logger.debug("Unable to resolve username for %s", tweet.author_id)
            return

        if username.lower() in self.config.ignore_users:
            logger.info("Skipping ignored user @%s", username)
            return

        if tweet.lang and self.config.languages and tweet.lang.lower() not in self.config.languages:
            logger.debug("Skipping tweet %s due to language filter", tweet.id)
            return

        reply_text = self.config.reply_template.format(username=username, tweet_id=tweet.id)
        logger.info("Responding to @%s (%s)", username, tweet.id)
        if self.config.dry_run:
            logger.info("DRY RUN: would reply with: %s", reply_text)
            return

        try:
            self.client.create_tweet(in_reply_to_tweet_id=tweet.id, text=reply_text)
        except tweepy.TweepyException as exc:
            logger.error("Failed to send reply to @%s: %s", username, exc)

    def _resolve_username(self, user_id: int | str) -> Optional[str]:
        try:
            user_resp = self.client.get_user(id=user_id, user_fields=["username"])
        except tweepy.TweepyException as exc:
            logger.error("Failed to fetch user %s: %s", user_id, exc)
            return None
        if user_resp and user_resp.data:
            return user_resp.data.username
        return None


def load_config(args: argparse.Namespace) -> BotConfig:
    required_env = {
        "TWITTER_BEARER_TOKEN": "bearer_token",
        "TWITTER_API_KEY": "consumer_key",
        "TWITTER_API_SECRET": "consumer_secret",
        "TWITTER_ACCESS_TOKEN": "access_token",
        "TWITTER_ACCESS_SECRET": "access_token_secret",
    }
    env_values = {}
    missing = []
    for env_var in required_env:
        value = os.environ.get(env_var)
        if not value:
            missing.append(env_var)
        else:
            env_values[required_env[env_var]] = value
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    hashtags = [tag.strip().lstrip("#") for tag in args.hashtags.split(",") if tag.strip()]
    if not hashtags:
        raise ValueError("At least one hashtag must be provided via --hashtags")

    languages = {lang.strip().lower() for lang in args.languages.split(",") if lang.strip()} if args.languages else set()
    ignore_users = {user.strip().lstrip("@").lower() for user in args.ignore_users.split(",") if user.strip()} if args.ignore_users else set()

    return BotConfig(
        consumer_key=env_values["consumer_key"],
        consumer_secret=env_values["consumer_secret"],
        access_token=env_values["access_token"],
        access_token_secret=env_values["access_token_secret"],
        bearer_token=env_values["bearer_token"],
        hashtags=hashtags,
        languages=languages,
        ignore_users=ignore_users,
        reply_template=args.reply_template,
        dry_run=args.dry_run,
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Real-time Twitter hashtag responder")
    parser.add_argument("--hashtags", required=True, help="Comma-separated list of hashtags to monitor")
    parser.add_argument(
        "--languages",
        default="",
        help="Comma-separated list of language codes to allow (e.g., en, es). Leave blank for all.",
    )
    parser.add_argument(
        "--ignore-users",
        default="",
        help="Comma-separated list of usernames to ignore",
    )
    parser.add_argument(
        "--reply-template",
        default="Thanks for sharing, @{username}!",
        help="Template for replies. Use {username} placeholder.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without sending replies (logs actions only)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    try:
        args = parse_args(argv)
        config = load_config(args)
        bot = TwitterBot(config)
        bot.start()
        logger.info("Bot is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Received interrupt. Shutting down...")
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Fatal error: %s", exc)
        sys.exit(1)
    finally:
        try:
            bot.stop()  # type: ignore[name-defined]
        except Exception:  # pylint: disable=broad-except
            pass


if __name__ == "__main__":
    main()
