"""
Multi-Carrier Google Play Store Review Collector
Collects reviews from T-Mobile, Verizon, and AT&T apps
Stores each carrier in a UNIFIED index (one index per carrier containing all platforms)
ENHANCED: Collects more data points and richer metadata
"""

from google_play_scraper import app, reviews, Sort
from datetime import datetime
import logging
import os
from typing import List, Dict, Set
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class MultiCarrierPlayStoreCollector:
    """Collector for Google Play Store reviews from multiple carriers."""
    
    # App packages for all three carriers
    CARRIER_APPS = {
        'tmobile': {
            'com.tmobile.pr.mytmobile': 'T-Mobile',
            'com.tmobile.echolocate': 'T-Mobile Scam Shield',
            'com.tmobile.tuesdays': 'T-Mobile Tuesdays',
            'com.tmobile.services.nameid': 'T-Mobile Name ID',
            'com.tmobile.pr.adapt': 'T-Mobile Home Internet',
        },
        'verizon': {
            'com.vzw.hss.myverizon': 'My Verizon',
            'com.verizon.messaging.vzmsgs': 'Verizon Messages',
            'com.verizon.cloud': 'Verizon Cloud',
            'com.verizon.fios.tv': 'Verizon Fios TV',
            'com.verizon.scallfilter': 'Verizon Call Filter',
            'com.verizon.net.fido': 'Verizon Home',
            'com.asurion.android.verizon.vms': 'Verizon Smart Family',
        },
        'att': {
            'com.att.myWireless': 'myAT&T',
            'com.att.callprotect': 'AT&T Call Protect',
            'com.att.smartlimits': 'AT&T Secure Family',
            'com.att.shm': 'AT&T Smart Home Manager',
            'com.att.actively': 'AT&T ActiveArmor',
            'com.att.dh': 'AT&T Digital Home',
        }
    }
    
    def __init__(self):
        """Initialize collector with carrier-specific UNIFIED Azure Cognitive Search indexes."""
        logger.info("?? Initializing Multi-Carrier Play Store Collector")
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
        
        if not search_endpoint or not search_api_key:
            raise RuntimeError("Azure credentials required (AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY)")
        
        from vector_db import SocialMediaVectorDB
        
        # Create unified vector DBs for each carrier (one index per carrier)
        self.vector_dbs = {}
        for carrier in ['tmobile', 'verizon', 'att']:
            self.vector_dbs[carrier] = SocialMediaVectorDB(
                endpoint=search_endpoint, 
                api_key=search_api_key,
                carrier=carrier  # No index_type - unified index handles all platforms
            )
            logger.info(f"? Vector DB initialized for {carrier.upper()} (unified index)")
        
        # Cache of existing post_ids per carrier
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
        """Load all existing post_ids for a carrier into memory."""
        if self._cache_loaded[carrier]:
            return
        
        logger.info(f"?? Loading existing post_ids for {carrier.upper()}...")
        try:
            # Filter by platform='google_play' to get only Play Store reviews
            results = self.vector_dbs[carrier].search_client.search(
                search_text="*",
                filter="platform eq 'google_play'",
                select=["post_id"],
                top=10000
            )
            
            for doc in results:
                post_id = doc.get('post_id')
                if post_id:
                    self._existing_ids_cache[carrier].add(post_id)
            
            logger.info(f"? Loaded {len(self._existing_ids_cache[carrier])} existing Play Store post_ids for {carrier.upper()}")
            self._cache_loaded[carrier] = True
            
        except Exception as e:
            logger.warning(f"??  Failed to load cache for {carrier.upper()}: {e}")
            self._cache_loaded[carrier] = True
    
    def _is_duplicate(self, carrier: str, post_id: str) -> bool:
        """Fast duplicate check using in-memory cache."""
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
            logger.warning(f"??  Error checking duplicate for {post_id}: {e}")
            return False
    
    def get_app_info(self, package_id):
        """Get basic app information."""
        try:
            result = app(package_id, lang='en', country='us')
            return {
                'title': result.get('title'),
                'score': result.get('score'),
                'ratings': result.get('ratings'),
                'reviews': result.get('reviews'),
                'installs': result.get('installs'),
            }
        except Exception as e:
            logger.error(f"Error fetching app info for {package_id}: {e}")
            return None
    
    def categorize_review(self, text: str) -> str:
        """Categorize review based on keywords."""
        t = text.lower()
        if any(w in t for w in ['network','signal','coverage','data','5g','4g','lte','connection']): 
            return 'network_connectivity'
        if any(w in t for w in ['bill','charge','price','payment','expensive','cost','fee']): 
            return 'billing_pricing'
        if any(w in t for w in ['support','customer service','representative','agent','help','staff']): 
            return 'customer_service'
        if any(w in t for w in ['app','crash','bug','update','login','interface','feature']): 
            return 'app_functionality'
        if any(w in t for w in ['plan','unlimited','upgrade','switch','contract']): 
            return 'plans_features'
        return 'general'
    
    def determine_sentiment(self, score: int) -> str:
        """Determine sentiment based on star rating."""
        return 'positive' if score >= 4 else 'neutral' if score >= 3 else 'negative'
    
    def format_review(self, review: Dict, app_name: str, carrier: str) -> Dict:
        """Format review into standard social media post format with ENHANCED metadata."""
        review_id = review.get('reviewId', '')
        post_id = f"playstore_{carrier}_{review_id}" if review_id else f"playstore_{carrier}_{app_name}_{datetime.utcnow().timestamp()}"
        
        # Extract more data points
        content = review.get('content', '')
        reply_content = review.get('replyContent', '')
        
        return {
            'text': content,
            'metadata': {
                'sentiment': self.determine_sentiment(review.get('score', 0)),
                'category': self.categorize_review(content),
                'date': review.get('at').strftime('%Y-%m-%d') if review.get('at') else datetime.utcnow().strftime('%Y-%m-%d'),
                'platform': 'google_play',
                'app_name': app_name,
                'rating': review.get('score', 0),
                'thumbs_up': review.get('thumbsUpCount', 0),
                'author': review.get('userName', 'Anonymous'),
                'review_id': review_id,
                'reply_content': reply_content,
                'reply_date': review.get('repliedAt').strftime('%Y-%m-%d') if review.get('repliedAt') else '',
                'review_version': review.get('reviewCreatedVersion', ''),
                'has_reply': bool(reply_content),
                'post_id': post_id,
                'carrier': carrier.upper(),
                # Additional metadata for richer analysis
                'review_length': len(content),
                'has_developer_response': bool(reply_content),
            }
        }
    
    def collect_carrier_reviews(
        self, 
        carrier: str, 
        reviews_per_app: int = 1000,  # DOUBLED from 500
        stop_after_duplicates: int = 40  # DOUBLED from 20
    ) -> List[Dict]:
        """Collect reviews for a specific carrier with early stopping.
        
        ENHANCED: Collects MORE reviews per app for statistical significance (2x increase).
        """
        carrier_lower = carrier.lower()
        if carrier_lower not in self.CARRIER_APPS:
            logger.error(f"? Unknown carrier: {carrier}")
            return []
        
        # Load cache
        self._load_existing_ids_cache(carrier_lower)
        
        all_reviews = []
        apps = self.CARRIER_APPS[carrier_lower]
        
        logger.info(f"\n{'='*70}")
        logger.info(f"?? Collecting Reviews: {carrier.upper()} Apps (Play Store)")
        logger.info(f"{'='*70}")
        
        for package_id, app_name in apps.items():
            logger.info(f"\n?? Processing: {app_name}")
            
            # Get app info
            info = self.get_app_info(package_id)
            if info:
                logger.info(f"   ? Rating: {info['score']:.1f}/5.0")
                logger.info(f"   ?? Total Reviews: {info['reviews']:,}")
            
            # Collect reviews with early stop
            new_reviews = []
            consecutive_duplicates = 0
            total_fetched = 0
            
            try:
                result, _ = reviews(
                    package_id,
                    lang='en',
                    country='us',
                    sort=Sort.NEWEST,
                    count=reviews_per_app
                )
                
                for review in result:
                    total_fetched += 1
                    formatted = self.format_review(review, app_name, carrier_lower)
                    post_id = formatted['metadata']['post_id']
                    
                    if self._is_duplicate(carrier_lower, post_id):
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            logger.info(f"   ?? Stopping early: {consecutive_duplicates} consecutive duplicates")
                            break
                    else:
                        consecutive_duplicates = 0
                        new_reviews.append(formatted)
                        self._existing_ids_cache[carrier_lower].add(post_id)
                
                logger.info(f"   ? Collected {len(new_reviews)} new reviews")
                
            except Exception as e:
                logger.error(f"   ? Error collecting reviews: {e}")
            
            all_reviews.extend(new_reviews)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"?? Total Reviews Collected for {carrier.upper()}: {len(all_reviews)}")
        logger.info(f"{'='*70}")
        
        return all_reviews
    
    def collect_all_carriers(
        self, 
        reviews_per_app: int = 1000,  # DOUBLED from 500
        stop_after_duplicates: int = 40  # DOUBLED from 20
    ) -> Dict[str, List[Dict]]:
        """
        Collect reviews from all carriers and store in separate indexes.
        
        ENHANCED: Collects MORE data points for comprehensive analysis (2x increase).
        
        Returns:
            Dict mapping carrier name to list of reviews
        """
        all_carrier_reviews = {}
        
        logger.info("\n" + "="*70)
        logger.info("?? MULTI-CARRIER PLAY STORE COLLECTION (ENHANCED 2X)")
        logger.info("="*70)
        logger.info(f"Carriers: T-Mobile, Verizon, AT&T")
        logger.info(f"Reviews per app: {reviews_per_app} (2X ENHANCED)")
        logger.info(f"Stop threshold: {stop_after_duplicates} duplicates")
        logger.info("="*70)
        
        for carrier in ['tmobile', 'verizon', 'att']:
            reviews = self.collect_carrier_reviews(carrier, reviews_per_app, stop_after_duplicates)
            all_carrier_reviews[carrier] = reviews
            
            # Store in carrier-specific index
            if reviews:
                self._store_in_azure(carrier, reviews)
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("?? COLLECTION SUMMARY")
        logger.info("="*70)
        for carrier, reviews in all_carrier_reviews.items():
            logger.info(f"{carrier.upper()}: {len(reviews)} reviews")
        logger.info(f"TOTAL: {sum(len(r) for r in all_carrier_reviews.values())} reviews")
        logger.info("="*70)
        
        return all_carrier_reviews
    
    def _store_in_azure(self, carrier: str, reviews: List[Dict]):
        """Store reviews in carrier-specific UNIFIED Azure index."""
        if not reviews:
            logger.info(f"??  No reviews to store for {carrier.upper()}.")
            return
        
        logger.info(f"?? Storing {len(reviews)} new {carrier.upper()} Play Store reviews...")
        try:
            self.vector_dbs[carrier].add_posts(reviews)
            logger.info(f"? Storage complete! {len(reviews)} {carrier.upper()} reviews added to unified index")
        except Exception as e:
            logger.error(f"? Storage failed for {carrier.upper()}: {e}")


if __name__ == '__main__':
    collector = MultiCarrierPlayStoreCollector()
    all_reviews = collector.collect_all_carriers(reviews_per_app=1000)  # 2X ENHANCED
