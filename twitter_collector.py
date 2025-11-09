import logging
import os
from datetime import datetime
from typing import List, Dict, Optional

from client import TwitterClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TwitterCollector:
    """
    Collect recent tweets related to T-Mobile and save to a .txt file.
    Uses TwitterClient (tweepy.Client wrapper) defined in client.py.
    """

    def __init__(self, client: Optional[TwitterClient] = None):
        self.client = client or TwitterClient()
        self.platform = "twitter"

    def default_query(self) -> str:
        # search t-mobile mentions, exclude retweets and replies-only noise, English only
        return '(tmobile OR "t-mobile" OR @TMobile) -is:retweet lang:en'

    def collect_by_query(self, query: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Search recent tweets using the given query and return a list of post dicts with metadata and top_comment.
        limit: number of tweets to request (max 100 per request).
        """
        q = query or self.default_query()
        logger.info(f"Searching Twitter with query: {q} (limit={limit})")
        tweets = self.client.search_recent(q, max_results=limit)

        posts = []
        seen = set()
        for t in tweets:
            tid = str(getattr(t, "id", ""))
            if not tid or tid in seen:
                continue
            seen.add(tid)
            pm = getattr(t, "public_metrics", {}) or {}
            score = (
                pm.get("like_count", 0)
                + pm.get("retweet_count", 0)
                + pm.get("reply_count", 0)
                + pm.get("quote_count", 0)
            )
            metadata = {
                "post_id": tid,
                "date": getattr(t, "created_at", None),
                "platform": self.platform,
                "category": "twitter_mention",
                "score": score,
                "num_comments": pm.get("reply_count", 0),
                "author_id": getattr(t, "author_id", None),
            }

            # try to fetch top reply (top comment) in the same conversation
            top_comment = ""
            conv_id = getattr(t, "conversation_id", None) or tid
            if conv_id:
                replies = self.client.get_tweet_replies(conversation_id=conv_id, exclude_author_id=metadata.get("author_id"), max_results=20)
                # find reply with highest like_count
                best = None
                best_likes = -1
                for r in replies:
                    rpm = getattr(r, "public_metrics", {}) or {}
                    likes = rpm.get("like_count", 0)
                    if likes > best_likes:
                        best_likes = likes
                        best = r
                if best:
                    top_comment = getattr(best, "text", "")

            posts.append({
                "text": getattr(t, "text", ""),
                "metadata": metadata,
                "top_comment": top_comment,
            })

        return posts

    def collect_related_to_tmobile(self, limit_per_run: int = 50) -> List[Dict]:
        return self.collect_by_query(self.default_query(), limit=limit_per_run)

    def save_to_file(self, posts: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save posts to a timestamped .txt file. Returns path to file.
        """
        if not posts:
            raise ValueError("No posts to save")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"twitter_posts_{ts}.txt"
        logger.info(f"Saving {len(posts)} posts to {filename}")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("T-MOBILE TWITTER POSTS COLLECTION\n")
                f.write(f"Collected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Posts: {len(posts)}\n")
                f.write("=" * 80 + "\n\n")
                for i, post in enumerate(posts, 1):
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"POST #{i}\n")
                    f.write(f"{'=' * 80}\n\n")
                    md = post["metadata"]
                    f.write("METADATA:\n")
                    f.write(f"  Post ID: {md.get('post_id')}\n")
                    f.write(f"  Category: {md.get('category')}\n")
                    f.write(f"  Date: {md.get('date')}\n")
                    f.write(f"  Platform: {md.get('platform')}\n")
                    f.write(f"  Score: {md.get('score')}\n")
                    f.write(f"  Comments: {md.get('num_comments')}\n")
                    if md.get("author_id"):
                        f.write(f"  Author ID: {md.get('author_id')}\n")
                    f.write("\n")
                    f.write("POST TEXT:\n")
                    f.write("-" * 80 + "\n")
                    f.write(post.get("text", "") + "\n")
                    f.write("-" * 80 + "\n\n")
                    top = post.get("top_comment", "")
                    if top:
                        f.write("TOP COMMENT:\n")
                        f.write("-" * 80 + "\n")
                        f.write(top + "\n")
                        f.write("-" * 80 + "\n")
                    else:
                        f.write("TOP COMMENT: (No comments available)\n")
                    f.write("\n")
            logger.info(f"Saved to {os.path.abspath(filename)}")
            return os.path.abspath(filename)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise

#!/usr/bin/env python3
"""
Standalone runner for the Twitter collector.
"""

from twitter_collector import TwitterCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("📱 Twitter Collector - T-Mobile")
    logger.info("=" * 60)

    collector = TwitterCollector()

    logger.info("📥 Collecting tweets related to T-Mobile...")
    posts = collector.collect_related_to_tmobile(limit_per_run=50)

    if not posts:
        logger.warning("⚠️ No tweets collected.")
        return

    logger.info(f"📊 Collected {len(posts)} tweets")
    # show sample
    for i, p in enumerate(posts[:5], 1):
        logger.info(f"{i}. {p['text'][:120]}...")
        logger.info(f"   Score: {p['metadata'].get('score')} | Comments: {p['metadata'].get('num_comments')}")
    path = collector.save_to_file(posts)
    logger.info(f"✅ Collection complete. Saved to {path}")


if __name__ == "__main__":
    main()
