"""
Scheduled Data Collector
Pulls 5 posts for each carrier/platform combination every minute.

Supports:
- Carriers: T-Mobile, Verizon, AT&T
- Platforms: Reddit, Google Play Store, Apple App Store
- Schedule: Every 60 seconds
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Set
from dotenv import load_dotenv
from vector_db import SocialMediaVectorDB
import threading
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduled_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScheduledCollector:
    """
    Collects 5 posts per carrier per platform every minute.
    Stores data in carrier-specific unified Azure indexes.
    """
    
    def __init__(self):
        """Initialize the scheduled collector with all necessary clients."""
        load_dotenv()
        
        # Configuration
        self.POSTS_PER_PLATFORM = 5
        self.INTERVAL_SECONDS = 60
        
        # Carrier configurations
        self.CARRIERS = {
            'tmobile': {
                'name': 'T-Mobile',
                'reddit_subreddit': 'tmobile',
                'play_store_app_id': 'com.tmobile.pr.mytmobile',
                'app_store_app_id': '1492278657',
                'app_store_country': 'us'
            },
            'verizon': {
                'name': 'Verizon',
                'reddit_subreddit': 'verizon',
                'play_store_app_id': 'com.vzw.hss.myverizon',
                'app_store_app_id': '416023011',
                'app_store_country': 'us'
            },
            'att': {
                'name': 'AT&T',
                'reddit_subreddit': 'ATT',
                'play_store_app_id': 'com.att.myatt',
                'app_store_app_id': '309172177',
                'app_store_country': 'us'
            }
        }
        
        # Initialize clients
        self._init_reddit()
        self._init_vector_dbs()
        
        # Duplicate tracking cache
        self._existing_ids: Dict[str, Set[str]] = defaultdict(set)
        self._load_existing_ids()
        
        # Statistics
        self.stats = {
            'total_runs': 0,
            'total_posts_collected': 0,
            'total_duplicates_skipped': 0,
            'posts_by_carrier': defaultdict(int),
            'posts_by_platform': defaultdict(int),
            'last_run': None
        }
    
    def _init_reddit(self):
        """Initialize Reddit API client."""
        try:
            import praw
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT", "Carrier-Analysis-Bot/1.0")
            )
            self.reddit.read_only = True
            logger.info("? Reddit API initialized")
        except Exception as e:
            logger.error(f"? Reddit initialization failed: {e}")
            self.reddit = None
    
    def _init_vector_dbs(self):
        """Initialize Azure Search vector databases for each carrier."""
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        api_key = os.getenv("AZURE_SEARCH_API_KEY")
        
        if not endpoint or not api_key:
            raise RuntimeError("Azure Search credentials required")
        
        self.vector_dbs = {}
        for carrier in self.CARRIERS.keys():
            try:
                self.vector_dbs[carrier] = SocialMediaVectorDB(
                    endpoint=endpoint,
                    api_key=api_key,
                    carrier=carrier
                )
                logger.info(f"? {carrier.upper()} vector DB initialized")
            except Exception as e:
                logger.error(f"? Failed to initialize {carrier} DB: {e}")
    
    def _load_existing_ids(self):
        """Load existing post IDs from all indexes to prevent duplicates."""
        logger.info("?? Loading existing post IDs for duplicate detection...")
        
        for carrier, db in self.vector_dbs.items():
            try:
                results = db.search_client.search(
                    search_text="*",
                    select=["post_id"],
                    top=10000
                )
                
                count = 0
                for doc in results:
                    post_id = doc.get('post_id')
                    if post_id:
                        self._existing_ids[carrier].add(post_id)
                        count += 1
                
                logger.info(f"   {carrier.upper()}: Loaded {count} existing IDs")
            except Exception as e:
                logger.warning(f"   ?? Failed to load IDs for {carrier}: {e}")
        
        total = sum(len(ids) for ids in self._existing_ids.values())
        logger.info(f"? Total existing IDs loaded: {total}")
    
    def _is_duplicate(self, carrier: str, post_id: str) -> bool:
        """Check if a post ID already exists."""
        return post_id in self._existing_ids[carrier]
    
    def _categorize_text(self, text: str) -> str:
        """Categorize text based on keywords."""
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
        if any(word in text_lower for word in ['app', 'application', 'login', 'crash', 'bug', 'interface']):
            return 'app_functionality'
        
        return 'general'
    
    def _collect_reddit_posts(self, carrier: str, limit: int = 5) -> List[Dict]:
        """Collect recent posts from Reddit for a carrier."""
        if not self.reddit:
            return []
        
        carrier_config = self.CARRIERS[carrier]
        subreddit_name = carrier_config['reddit_subreddit']
        carrier_name = carrier_config['name']
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # Get new posts
            for submission in subreddit.new(limit=limit * 2):  # Get extra to account for duplicates
                post_id = f"reddit_{submission.id}"
                
                # Skip duplicates
                if self._is_duplicate(carrier, post_id):
                    continue
                
                # Format post
                post_text = submission.title or ""
                if getattr(submission, 'selftext', None):
                    post_text = (post_text + " " + submission.selftext).strip()
                post_text = post_text[:2000]
                
                formatted_post = {
                    'text': post_text,
                    'metadata': {
                        'sentiment': 'neutral',
                        'category': self._categorize_text(post_text),
                        'date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                        'platform': 'reddit',
                        'post_id': post_id,
                        'carrier': carrier_name,
                        'author': str(submission.author) if submission.author else 'unknown',
                        'subreddit': subreddit_name,
                        'score': getattr(submission, 'score', 0),
                        'num_comments': getattr(submission, 'num_comments', 0),
                        'url': getattr(submission, 'url', ''),
                        'upvote_ratio': getattr(submission, 'upvote_ratio', 0.0),
                        'is_self': submission.is_self
                    }
                }
                
                posts.append(formatted_post)
                self._existing_ids[carrier].add(post_id)
                
                if len(posts) >= limit:
                    break
            
            logger.info(f"   Reddit ({carrier.upper()}): {len(posts)} new posts")
            return posts
            
        except Exception as e:
            logger.error(f"   ? Reddit collection failed for {carrier}: {e}")
            return []
    
    def _collect_play_store_reviews(self, carrier: str, limit: int = 5) -> List[Dict]:
        """Collect recent reviews from Google Play Store for a carrier."""
        try:
            from google_play_scraper import reviews, Sort
            
            carrier_config = self.CARRIERS[carrier]
            app_id = carrier_config['play_store_app_id']
            carrier_name = carrier_config['name']
            
            # Get reviews
            result, _ = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=limit * 2  # Get extra to account for duplicates
            )
            
            posts = []
            for review in result:
                review_id = review.get('reviewId', '')
                post_id = f"playstore_{review_id}"
                
                # Skip duplicates
                if self._is_duplicate(carrier, post_id):
                    continue
                
                review_text = review.get('content', '')
                
                formatted_post = {
                    'text': review_text[:2000],
                    'metadata': {
                        'sentiment': 'neutral',
                        'category': self._categorize_text(review_text),
                        'date': review.get('at', datetime.now()).strftime('%Y-%m-%d') if hasattr(review.get('at', datetime.now()), 'strftime') else datetime.now().strftime('%Y-%m-%d'),
                        'platform': 'google_play',
                        'post_id': post_id,
                        'carrier': carrier_name,
                        'author': review.get('userName', 'unknown'),
                        'app_name': carrier_config['name'] + ' App',
                        'rating': review.get('score', 0),
                        'thumbs_up': review.get('thumbsUpCount', 0),
                        'reply_content': review.get('replyContent', ''),
                        'review_version': review.get('reviewCreatedVersion', ''),
                        'reply_date': str(review.get('repliedAt', ''))
                    }
                }
                
                posts.append(formatted_post)
                self._existing_ids[carrier].add(post_id)
                
                if len(posts) >= limit:
                    break
            
            logger.info(f"   Play Store ({carrier.upper()}): {len(posts)} new reviews")
            return posts
            
        except Exception as e:
            logger.error(f"   ? Play Store collection failed for {carrier}: {e}")
            return []
    
    def _collect_app_store_reviews(self, carrier: str, limit: int = 5) -> List[Dict]:
        """Collect recent reviews from Apple App Store for a carrier."""
        try:
            from app_store_scraper import AppStore
            
            carrier_config = self.CARRIERS[carrier]
            app_id = carrier_config['app_store_app_id']
            carrier_name = carrier_config['name']
            country = carrier_config['app_store_country']
            
            # Get reviews
            app = AppStore(country=country, app_name=carrier_name, app_id=app_id)
            app.review(how_many=limit * 2)  # Get extra to account for duplicates
            
            posts = []
            for review in app.reviews:
                review_id = review.get('id', review.get('review', ''))
                post_id = f"appstore_{app_id}_{review_id}"
                
                # Skip duplicates
                if self._is_duplicate(carrier, post_id):
                    continue
                
                review_text = review.get('review', '')
                
                formatted_post = {
                    'text': review_text[:2000],
                    'metadata': {
                        'sentiment': 'neutral',
                        'category': self._categorize_text(review_text),
                        'date': review.get('date', datetime.now()).strftime('%Y-%m-%d') if hasattr(review.get('date', datetime.now()), 'strftime') else datetime.now().strftime('%Y-%m-%d'),
                        'platform': 'app_store',
                        'post_id': post_id,
                        'carrier': carrier_name,
                        'author': review.get('userName', 'unknown'),
                        'app_name': carrier_config['name'] + ' App',
                        'title': review.get('title', ''),
                        'rating': review.get('rating', 0),
                        'developer_response': review.get('developerResponse', {}).get('body', '') if isinstance(review.get('developerResponse'), dict) else ''
                    }
                }
                
                posts.append(formatted_post)
                self._existing_ids[carrier].add(post_id)
                
                if len(posts) >= limit:
                    break
            
            logger.info(f"   App Store ({carrier.upper()}): {len(posts)} new reviews")
            return posts
            
        except Exception as e:
            logger.error(f"   ? App Store collection failed for {carrier}: {e}")
            return []
    
    def collect_all_platforms(self, carrier: str) -> List[Dict]:
        """Collect posts from all platforms for a specific carrier."""
        all_posts = []
        
        # Collect from Reddit
        reddit_posts = self._collect_reddit_posts(carrier, self.POSTS_PER_PLATFORM)
        all_posts.extend(reddit_posts)
        self.stats['posts_by_platform']['reddit'] += len(reddit_posts)
        
        # Collect from Play Store
        play_posts = self._collect_play_store_reviews(carrier, self.POSTS_PER_PLATFORM)
        all_posts.extend(play_posts)
        self.stats['posts_by_platform']['google_play'] += len(play_posts)
        
        # Collect from App Store
        app_posts = self._collect_app_store_reviews(carrier, self.POSTS_PER_PLATFORM)
        all_posts.extend(app_posts)
        self.stats['posts_by_platform']['app_store'] += len(app_posts)
        
        return all_posts
    
    def run_collection_cycle(self):
        """Run one complete collection cycle for all carriers and platforms."""
        logger.info("\n" + "=" * 80)
        logger.info(f"?? COLLECTION CYCLE #{self.stats['total_runs'] + 1}")
        logger.info(f"? Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        cycle_posts = 0
        
        for carrier in self.CARRIERS.keys():
            logger.info(f"\n?? Collecting for {carrier.upper()}...")
            
            try:
                # Collect from all platforms
                posts = self.collect_all_platforms(carrier)
                
                # Store in vector DB
                if posts and carrier in self.vector_dbs:
                    self.vector_dbs[carrier].add_posts(posts)
                    cycle_posts += len(posts)
                    self.stats['posts_by_carrier'][carrier] += len(posts)
                    logger.info(f"   ? Stored {len(posts)} posts for {carrier.upper()}")
                else:
                    logger.info(f"   ?? No new posts for {carrier.upper()}")
                    
            except Exception as e:
                logger.error(f"   ? Error collecting for {carrier}: {e}")
        
        # Update statistics
        self.stats['total_runs'] += 1
        self.stats['total_posts_collected'] += cycle_posts
        self.stats['last_run'] = datetime.now()
        
        logger.info("\n" + "-" * 80)
        logger.info(f"? Cycle Complete: {cycle_posts} new posts collected")
        logger.info(f"?? Total Posts Collected: {self.stats['total_posts_collected']}")
        logger.info(f"?? Total Cycles Run: {self.stats['total_runs']}")
        logger.info("-" * 80)
    
    def print_statistics(self):
        """Print collection statistics."""
        logger.info("\n" + "=" * 80)
        logger.info("?? COLLECTION STATISTICS")
        logger.info("=" * 80)
        logger.info(f"Total Runs: {self.stats['total_runs']}")
        logger.info(f"Total Posts Collected: {self.stats['total_posts_collected']}")
        logger.info(f"Last Run: {self.stats['last_run']}")
        
        logger.info("\n?? By Carrier:")
        for carrier, count in self.stats['posts_by_carrier'].items():
            logger.info(f"  {carrier.upper()}: {count}")
        
        logger.info("\n?? By Platform:")
        for platform, count in self.stats['posts_by_platform'].items():
            logger.info(f"  {platform}: {count}")
        
        logger.info("=" * 80 + "\n")
    
    def run_scheduled(self, max_cycles: int = None):
        """
        Run the collector on a schedule.
        
        Args:
            max_cycles: Maximum number of cycles to run (None = infinite)
        """
        logger.info("\n" + "=" * 80)
        logger.info("?? SCHEDULED COLLECTOR STARTED")
        logger.info("=" * 80)
        logger.info(f"?? Interval: {self.INTERVAL_SECONDS} seconds")
        logger.info(f"?? Posts per platform: {self.POSTS_PER_PLATFORM}")
        logger.info(f"?? Carriers: {', '.join([c.upper() for c in self.CARRIERS.keys()])}")
        logger.info(f"?? Platforms: Reddit, Google Play Store, Apple App Store")
        if max_cycles:
            logger.info(f"?? Max cycles: {max_cycles}")
        else:
            logger.info("?? Max cycles: Infinite (press Ctrl+C to stop)")
        logger.info("=" * 80)
        
        try:
            cycle = 0
            while True:
                # Run collection
                self.run_collection_cycle()
                
                # Increment cycle counter
                cycle += 1
                
                # Check if we've reached max cycles
                if max_cycles and cycle >= max_cycles:
                    logger.info(f"\n? Reached maximum cycles ({max_cycles})")
                    break
                
                # Print statistics every 10 cycles
                if cycle % 10 == 0:
                    self.print_statistics()
                
                # Wait for next cycle
                logger.info(f"\n? Waiting {self.INTERVAL_SECONDS} seconds until next cycle...")
                time.sleep(self.INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            logger.info("\n\n?? Collection interrupted by user")
        finally:
            self.print_statistics()
            logger.info("?? Scheduled collector stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduled Data Collector')
    parser.add_argument(
        '--max-cycles',
        type=int,
        default=None,
        help='Maximum number of collection cycles (default: infinite)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Collection interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--posts-per-platform',
        type=int,
        default=5,
        help='Number of posts to collect per platform (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Create collector
    collector = ScheduledCollector()
    
    # Override defaults if specified
    if args.interval != 60:
        collector.INTERVAL_SECONDS = args.interval
    if args.posts_per_platform != 5:
        collector.POSTS_PER_PLATFORM = args.posts_per_platform
    
    # Run scheduled collection
    collector.run_scheduled(max_cycles=args.max_cycles)


if __name__ == "__main__":
    main()
