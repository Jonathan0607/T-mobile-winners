"""
Reddit collector using PRAW to fetch top posts from r/tmobile subreddit.
"""

import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RedditCollector:
    """Collects posts from r/tmobile subreddit using PRAW."""
    
    def __init__(self):
        """Initialize Reddit API client using PRAW."""
        load_dotenv()
        
        try:
            import praw
            
            self.client_id = os.getenv("REDDIT_CLIENT_ID")
            self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            self.user_agent = os.getenv("REDDIT_USER_AGENT", "T-Mobile-Analysis-Bot/1.0")
            
            if not self.client_id or not self.client_secret:
                logger.warning("Reddit credentials not found. Reddit collection disabled.")
                logger.warning("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file")
                self.reddit = None
                return
            
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # Test connection
            try:
                self.reddit.read_only = True
                logger.info("✅ Reddit API client initialized (read-only mode)")
            except Exception as e:
                logger.error(f"Error testing Reddit connection: {e}")
                self.reddit = None
                
        except ImportError:
            logger.error("praw not installed. Install with: pip install praw")
            self.reddit = None
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {e}")
            self.reddit = None
    
    def get_top_posts(self, subreddit_name: str = "tmobile", limit: int = 25, time_filter: str = "week") -> List[Dict]:
        """
        Get top posts from r/tmobile subreddit.
        
        Args:
            subreddit_name: Subreddit name (default: "tmobile")
            limit: Number of posts to fetch (default: 25)
            time_filter: Time filter - "hour", "day", "week", "month", "year", "all" (default: "week")
        
        Returns:
            List of formatted post dictionaries
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized. Cannot fetch posts.")
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            logger.info(f"📱 Fetching top {limit} posts from r/{subreddit_name} (time: {time_filter})")
            
            posts = []
            
            # Get top posts
            for submission in subreddit.top(time_filter=time_filter, limit=limit):
                try:
                    # Combine title and text
                    post_text = submission.title
                    if submission.selftext:
                        post_text += f" {submission.selftext}"
                    
                    # Limit text length for processing
                    post_text = post_text[:2000]  # Reasonable length for analysis
                    
                    # Get top comment
                    top_comment = self._get_top_comment(submission)
                    
                    # Format post
                    formatted_post = {
                        'text': post_text,
                        'top_comment': top_comment,
                        'metadata': {
                            'sentiment': 'neutral',  # Could add sentiment analysis
                            'category': self._categorize_post(post_text),
                            'date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                            'platform': 'reddit',
                            'post_id': f"reddit_{submission.id}",
                            'carrier': 'T-Mobile',
                            'subreddit': subreddit_name,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'url': submission.url
                        }
                    }
                    
                    posts.append(formatted_post)
                    
                except Exception as e:
                    logger.warning(f"Error processing submission {submission.id}: {e}")
                    continue
            
            logger.info(f"✅ Collected {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            return []
    
    def get_hot_posts(self, subreddit_name: str = "tmobile", limit: int = 25) -> List[Dict]:
        """
        Get hot (trending) posts from r/tmobile subreddit.
        
        Args:
            subreddit_name: Subreddit name (default: "tmobile")
            limit: Number of posts to fetch (default: 25)
        
        Returns:
            List of formatted post dictionaries
        """
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            logger.info(f"📱 Fetching hot {limit} posts from r/{subreddit_name}")
            
            posts = []
            
            for submission in subreddit.hot(limit=limit):
                try:
                    post_text = submission.title
                    if submission.selftext:
                        post_text += f" {submission.selftext}"
                    post_text = post_text[:2000]  # Reasonable length for analysis
                    
                    # Get top comment
                    top_comment = self._get_top_comment(submission)
                    
                    formatted_post = {
                        'text': post_text,
                        'top_comment': top_comment,
                        'metadata': {
                            'sentiment': 'neutral',
                            'category': self._categorize_post(post_text),
                            'date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                            'platform': 'reddit',
                            'post_id': f"reddit_{submission.id}",
                            'carrier': 'T-Mobile',
                            'subreddit': subreddit_name,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'url': submission.url
                        }
                    }
                    
                    posts.append(formatted_post)
                    
                except Exception as e:
                    logger.warning(f"Error processing submission: {e}")
                    continue
            
            logger.info(f"✅ Collected {len(posts)} hot posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching hot posts: {e}")
            return []
    
    def get_new_posts(self, subreddit_name: str = "tmobile", limit: int = 25) -> List[Dict]:
        """
        Get newest posts from r/tmobile subreddit.
        
        Args:
            subreddit_name: Subreddit name (default: "tmobile")
            limit: Number of posts to fetch (default: 25)
        
        Returns:
            List of formatted post dictionaries
        """
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            logger.info(f"📱 Fetching {limit} newest posts from r/{subreddit_name}")
            
            posts = []
            
            for submission in subreddit.new(limit=limit):
                try:
                    post_text = submission.title
                    if submission.selftext:
                        post_text += f" {submission.selftext}"
                    post_text = post_text[:2000]  # Reasonable length for analysis
                    
                    # Get top comment
                    top_comment = self._get_top_comment(submission)
                    
                    formatted_post = {
                        'text': post_text,
                        'top_comment': top_comment,
                        'metadata': {
                            'sentiment': 'neutral',
                            'category': self._categorize_post(post_text),
                            'date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                            'platform': 'reddit',
                            'post_id': f"reddit_{submission.id}",
                            'carrier': 'T-Mobile',
                            'subreddit': subreddit_name,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'url': submission.url
                        }
                    }
                    
                    posts.append(formatted_post)
                    
                except Exception as e:
                    logger.warning(f"Error processing submission: {e}")
                    continue
            
            logger.info(f"✅ Collected {len(posts)} new posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching new posts: {e}")
            return []
    
    def _get_top_comment(self, submission) -> str:
        """
        Get the top comment from a Reddit submission.
        
        Args:
            submission: PRAW submission object
        
        Returns:
            Top comment text or empty string if no comments
        """
        try:
            # Replace "more comments" with actual comments
            submission.comments.replace_more(limit=0)
            
            # Get top-level comments sorted by score
            comments = submission.comments.list()
            if comments:
                # Sort by score (highest first)
                top_comment = max(comments, key=lambda c: c.score if hasattr(c, 'score') else 0)
                if hasattr(top_comment, 'body'):
                    return top_comment.body[:500]  # Limit comment length
            return ""
        except Exception as e:
            logger.debug(f"Error getting top comment: {e}")
            return ""
    
    def _categorize_post(self, text: str) -> str:
        """Categorize post based on keywords."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['network', 'connection', 'connectivity', 'signal', 'disconnect']):
            return 'network_connectivity'
        elif any(word in text_lower for word in ['5g', '5 g', 'lte', 'speed', 'data', 'download', 'upload']):
            return 'data_speed'
        elif any(word in text_lower for word in ['coverage', 'signal', 'bars', 'dead zone', 'no service']):
            return 'signal_strength'
        elif any(word in text_lower for word in ['customer service', 'support', 'help', 'agent', 'cs', 'rep']):
            return 'customer_service'
        elif any(word in text_lower for word in ['bill', 'price', 'cost', 'plan', 'charge', 'payment', 'billing']):
            return 'plan_billing'
        elif any(word in text_lower for word in ['call', 'voice', 'dropped', 'call quality']):
            return 'call_quality'
        elif any(word in text_lower for word in ['roaming', 'international', 'travel']):
            return 'roaming'
        elif any(word in text_lower for word in ['phone', 'device', 'compatible', 'unlock']):
            return 'device_compatibility'
        elif any(word in text_lower for word in ['outage', 'down', 'not working']):
            return 'network_outage'
        else:
            return 'general'
    
    def collect_all_types(self, subreddit_name: str = "tmobile", limit_per_type: int = 10) -> List[Dict]:
        """
        Collect top, hot, and new posts from r/tmobile.
        
        Args:
            subreddit_name: Subreddit name (default: "tmobile")
            limit_per_type: Number of posts per type (default: 10)
        
        Returns:
            Combined list of all posts
        """
        all_posts = []
        
        # Get top posts (this week)
        top_posts = self.get_top_posts(subreddit_name, limit_per_type, "week")
        all_posts.extend(top_posts)
        
        # Get hot posts
        hot_posts = self.get_hot_posts(subreddit_name, limit_per_type)
        all_posts.extend(hot_posts)
        
        # Get new posts
        new_posts = self.get_new_posts(subreddit_name, limit_per_type)
        all_posts.extend(new_posts)
        
        # Remove duplicates based on post_id
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            post_id = post['metadata']['post_id']
            if post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_posts.append(post)
        
        logger.info(f"✅ Total unique posts collected: {len(unique_posts)}")
        return unique_posts

