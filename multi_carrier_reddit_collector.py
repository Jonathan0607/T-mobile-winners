"""
Multi-Carrier Reddit Collector
Collects Reddit posts from carrier-specific subreddits (r/tmobile, r/verizon, r/att)
Stores each carrier in a UNIFIED index (one index per carrier containing all platforms)
ENHANCED: Collects more data points and richer metadata
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Set
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class MultiCarrierRedditCollector:
    """Collector for Reddit posts from multiple carrier subreddits."""
    
    # Subreddits for each carrier
    CARRIER_SUBREDDITS = {
        'tmobile': 'tmobile',
        'verizon': 'verizon',
        'att': 'att'  # Fixed: lowercase 'att' is the correct subreddit name
    }
    
    def __init__(self):
        """Initialize Reddit API client and UNIFIED Azure Search for all carriers."""
        # Initialize Reddit
        try:
            import praw
            self.client_id = os.getenv("REDDIT_CLIENT_ID")
            self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            self.user_agent = os.getenv("REDDIT_USER_AGENT", "Multi-Carrier-Analysis-Bot/1.0")
            
            if not self.client_id or not self.client_secret:
                raise RuntimeError("Reddit credentials required (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)")
            
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            self.reddit.read_only = True
            logger.info("? Reddit API client initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Reddit: {e}")
        
        # Initialize UNIFIED Azure Search indexes (one per carrier)
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        api_key = os.getenv("AZURE_SEARCH_API_KEY")
        if not endpoint or not api_key:
            raise RuntimeError("Azure credentials required (AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY)")
        
        from vector_db import SocialMediaVectorDB
        
        self.vector_dbs = {}
        for carrier in ['tmobile', 'verizon', 'att']:
            self.vector_dbs[carrier] = SocialMediaVectorDB(
                endpoint=endpoint, 
                api_key=api_key,
                carrier=carrier  # No index_type - unified index
            )
            logger.info(f"? Vector DB initialized for {carrier.upper()} (unified index)")
        
        # Cache for fast duplicate checking per carrier
        self._existing_ids_cache: Dict[str, Set[str]] = {
            'tmobile': set(),
            'verizon': set(),
            'att': set()
        }
        self._cache_loaded: Dict[str, bool] = {
            'tmobile': False,
            'verizon': False,
            'att': False
        }
    
    def _load_existing_ids_cache(self, carrier: str):
        """Load all existing Reddit post_ids for a carrier into memory."""
        if self._cache_loaded[carrier]:
            return
        
        logger.info(f"?? Loading existing Reddit post_ids for {carrier.upper()}...")
        try:
            # Filter by platform='reddit' to get only Reddit posts
            results = self.vector_dbs[carrier].search_client.search(
                search_text="*",
                filter="platform eq 'reddit'",
                select=["post_id"],
                top=10000
            )
            
            for doc in results:
                post_id = doc.get('post_id')
                if post_id:
                    self._existing_ids_cache[carrier].add(post_id)
            
            logger.info(f"? Loaded {len(self._existing_ids_cache[carrier])} existing Reddit posts for {carrier.upper()}")
            self._cache_loaded[carrier] = True
            
        except Exception as e:
            logger.warning(f"??  Failed to load cache for {carrier.upper()}: {e}")
            self._cache_loaded[carrier] = True
    
    def _is_duplicate(self, carrier: str, post_id: str) -> bool:
        """Fast duplicate check using cache."""
        if post_id in self._existing_ids_cache[carrier]:
            return True
        
        try:
            existing = list(self.vector_dbs[carrier].search_client.search(
                search_text="", 
                filter=f"post_id eq '{post_id}'", 
                select=["post_id"], 
                top=1
            ))
            
            if existing:
                self._existing_ids_cache[carrier].add(post_id)
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"??  Error checking duplicate: {e}")
            return False
    
    def _format_submission(self, submission, subreddit_name: str, carrier: str) -> Dict:
        """Format Reddit submission into standard format with ENHANCED metadata."""
        post_text = submission.title or ""
        if getattr(submission, 'selftext', None):
            post_text = (post_text + " " + submission.selftext).strip()
        post_text = post_text[:2000]
        
        top_comment = self._get_top_comment(submission)
        
        # Extract MORE metadata
        return {
            'text': post_text,
            'top_comment': top_comment,
            'metadata': {
                'sentiment': 'neutral',
                'category': self._categorize_post(post_text),
                'date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                'platform': 'reddit',
                'post_id': f"reddit_{carrier}_{submission.id}",
                'carrier': carrier.upper(),
                'subreddit': subreddit_name,
                'score': getattr(submission, 'score', 0),
                'num_comments': getattr(submission, 'num_comments', 0),
                'url': getattr(submission, 'url', ''),
                'author': str(getattr(submission, 'author', 'Anonymous')),
                'upvote_ratio': getattr(submission, 'upvote_ratio', 0.0),
                'flair': str(getattr(submission, 'link_flair_text', '')),
                'awards': getattr(submission, 'total_awards_received', 0),
                'is_self': getattr(submission, 'is_self', False),
                # Additional metadata for richer analysis
                'has_top_comment': bool(top_comment),
                'post_length': len(post_text),
                'is_video': getattr(submission, 'is_video', False),
                'over_18': getattr(submission, 'over_18', False),
            }
        }
    
    def _get_top_comment(self, submission) -> str:
        """Get the top comment from a submission with MORE context."""
        try:
            submission.comments.replace_more(limit=0)
            comments = submission.comments.list()
            if comments:
                top_comment = max(comments, key=lambda c: getattr(c, 'score', 0))
                body = getattr(top_comment, 'body', '')
                return body[:1000]  # INCREASED from 500 for more context
            return ""
        except Exception:
            return ""
    
    def _categorize_post(self, text: str) -> str:
        """Categorize post based on keywords."""
        text_lower = text.lower()
        if any(word in text_lower for word in ['network', 'connection', 'connectivity', 'signal', 'disconnect']):
            return 'network_connectivity'
        if any(word in text_lower for word in ['5g', '5 g', 'lte', 'speed', 'data', 'download', 'upload']):
            return 'data_speed'
        if any(word in text_lower for word in ['coverage', 'signal', 'bars', 'dead zone', 'no service']):
            return 'signal_strength'
        if any(word in text_lower for word in ['customer service', 'support', 'help', 'agent', 'cs', 'rep']):
            return 'customer_service'
        if any(word in text_lower for word in ['bill', 'price', 'cost', 'plan', 'charge', 'payment', 'billing']):
            return 'plan_billing'
        return 'general'
    
    def collect_carrier_posts(
        self,
        carrier: str,
        post_type: str = "hot",
        limit: int = 400,  # DOUBLED from 200
        time_filter: str = "month"  # CHANGED from "week" for more data
    ) -> List[Dict]:
        """
        Collect posts for a specific carrier with real-time deduplication.
        
        ENHANCED: Collects MORE posts for richer dataset (2x increase).
        
        Args:
            carrier: Carrier name ('tmobile', 'verizon', 'att')
            post_type: Type of posts ("hot", "new", "top")
            limit: Maximum posts to fetch (2X ENHANCED)
            time_filter: Time filter for top posts (EXPANDED to month)
            
        Returns:
            List of new (non-duplicate) posts
        """
        carrier_lower = carrier.lower()
        if carrier_lower not in self.CARRIER_SUBREDDITS:
            logger.error(f"? Unknown carrier: {carrier}")
            return []
        
        subreddit_name = self.CARRIER_SUBREDDITS[carrier_lower]
        subreddit = self.reddit.subreddit(subreddit_name)
        
        logger.info(f"?? Collecting {post_type} posts from r/{subreddit_name} (limit: {limit})")
        
        new_posts = []
        total_checked = 0
        duplicates = 0
        
        # Get the appropriate post generator
        if post_type == "hot":
            posts_generator = subreddit.hot(limit=limit)
        elif post_type == "new":
            posts_generator = subreddit.new(limit=limit)
        elif post_type == "top":
            posts_generator = subreddit.top(time_filter=time_filter, limit=limit)
        else:
            raise ValueError(f"Invalid post_type: {post_type}")
        
        # Check each post as we fetch it
        for submission in posts_generator:
            total_checked += 1
            post_id = f"reddit_{carrier_lower}_{submission.id}"
            
            # Check for duplicate
            if self._is_duplicate(carrier_lower, post_id):
                duplicates += 1
                logger.debug(f"   ??  Skipping duplicate: {post_id}")
                continue
            
            # New post - format and add
            formatted = self._format_submission(submission, subreddit_name, carrier_lower)
            new_posts.append(formatted)
            
            # Add to cache immediately
            self._existing_ids_cache[carrier_lower].add(post_id)
            logger.debug(f"   ? New post: {post_id}")
        
        logger.info(f"   ?? Checked: {total_checked} | New: {len(new_posts)} | Duplicates: {duplicates}")
        return new_posts
    
    def collect_all_carriers(
        self,
        limit_per_type: int = 400,  # DOUBLED from 200
        post_types: List[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Collect Reddit posts from all carriers.
        
        ENHANCED: Collects MORE posts per type for richer dataset (2x increase).
        
        Args:
            limit_per_type: Limit per post type (2X ENHANCED)
            post_types: List of post types to collect (default: ['hot', 'new', 'top'])
            
        Returns:
            Dict mapping carrier to list of posts
        """
        if post_types is None:
            post_types = ['hot', 'new', 'top']
        
        logger.info("\n" + "="*70)
        logger.info("?? MULTI-CARRIER REDDIT COLLECTION (ENHANCED 2X)")
        logger.info("="*70)
        logger.info(f"Carriers: T-Mobile, Verizon, AT&T")
        logger.info(f"Post types: {', '.join(post_types)}")
        logger.info(f"Limit per type: {limit_per_type} (2X ENHANCED)")
        logger.info("="*70)
        
        all_carrier_posts = {}
        
        for carrier in ['tmobile', 'verizon', 'att']:
            # Load cache for this carrier
            self._load_existing_ids_cache(carrier)
            
            logger.info(f"\n{'='*70}")
            logger.info(f"?? Collecting from {carrier.upper()}: r/{self.CARRIER_SUBREDDITS[carrier]}")
            logger.info(f"{'='*70}")
            
            carrier_posts = []
            
            # Collect each post type
            for post_type in post_types:
                logger.info(f"\n?? Collecting {post_type.upper()} posts...")
                posts = self.collect_carrier_posts(
                    carrier,
                    post_type=post_type,
                    limit=limit_per_type
                )
                carrier_posts.extend(posts)
                logger.info(f"   ? Added {len(posts)} new {post_type} posts")
            
            all_carrier_posts[carrier] = carrier_posts
            
            logger.info(f"\n{'='*70}")
            logger.info(f"?? Total Reddit posts for {carrier.upper()}: {len(carrier_posts)}")
            logger.info(f"{'='*70}")
            
            # Store in unified carrier index
            if carrier_posts:
                self._store_in_azure(carrier, carrier_posts)
        
        # Final summary
        logger.info("\n" + "="*70)
        logger.info("?? REDDIT COLLECTION SUMMARY")
        logger.info("="*70)
        for carrier, posts in all_carrier_posts.items():
            logger.info(f"{carrier.upper()}: {len(posts)} posts")
        logger.info(f"TOTAL: {sum(len(p) for p in all_carrier_posts.values())} posts")
        logger.info("="*70)
        
        return all_carrier_posts
    
    def _store_in_azure(self, carrier: str, posts: List[Dict]):
        """Store posts in carrier-specific UNIFIED Azure index."""
        if not posts:
            logger.info(f"??  No posts to store for {carrier.upper()}.")
            return
        
        logger.info(f"?? Storing {len(posts)} new {carrier.upper()} Reddit posts...")
        try:
            self.vector_dbs[carrier].add_posts(posts)
            logger.info(f"? Storage complete! {len(posts)} {carrier.upper()} posts added to unified index")
        except Exception as e:
            logger.error(f"? Storage failed for {carrier.upper()}: {e}")


if __name__ == '__main__':
    collector = MultiCarrierRedditCollector()
    all_posts = collector.collect_all_carriers(limit_per_type=400)  # 2X ENHANCED
