# ...existing code...
import os
from dotenv import load_dotenv
import tweepy

load_dotenv()


class TwitterClient:
    def __init__(self, bearer_token: str | None = None):
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise EnvironmentError("TWITTER_BEARER_TOKEN not set in environment")
        self.client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)

    def get_user_by_username(self, username: str):
        return self.client.get_user(username=username)

    def get_user_tweets(self, user_id: str, max_results: int = 100):
        # max_results per request is up to 100
        resp = self.client.get_users_tweets(
            id=user_id,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "public_metrics", "text", "conversation_id", "author_id"]
        )
        return resp.data or []

    # changed/added: search recent tweets by query
    def search_recent(self, query: str, max_results: int = 100):
        """
        Wrapper around Tweepy's search_recent_tweets.
        Returns list of Tweet objects (or empty list).
        """
        try:
            resp = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "text", "conversation_id", "author_id"]
            )
            return resp.data or []
        except Exception:
            # let caller handle or return empty list on error
            return []

    def get_tweet_replies(self, conversation_id: str, exclude_author_id: str | None = None, max_results: int = 50):
        """
        Find replies in the same conversation. Optionally exclude the original author.
        Picks from recent tweets matching conversation_id.
        """
        # build query: conversation_id:<id> -is:retweet (optionally exclude original author's tweets)
        q = f"conversation_id:{conversation_id} -is:retweet"
        if exclude_author_id:
            q += f" -from:{exclude_author_id}"
        try:
            resp = self.client.search_recent_tweets(
                query=q,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "text", "author_id"]
            )
            return resp.data or []
        except Exception:
            return []
# ...existing code...