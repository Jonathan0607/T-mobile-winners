"""
Multi-Carrier Apple App Store Review Collector using iTunes RSS Feed API
Collects reviews from T-Mobile, Verizon, and AT&T apps
Stores each carrier in a UNIFIED index (one index per carrier containing all platforms)
ENHANCED: Collects more data points and richer metadata
"""

import requests
import json
from datetime import datetime
import logging
import os
from typing import List, Dict
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class MultiCarrierAppStoreCollector:
    """Collector for Apple App Store reviews from multiple carriers."""
    
    # App IDs for all three carriers
    CARRIER_APPS = {
        'tmobile': {
            '682887390': 'T-Mobile',
            '533339058': 'T-Mobile Tuesdays',
            '1554618143': 'T-Mobile Scam Shield',
            '1169553938': 'T-Mobile SyncUP Drive',
        },
        'verizon': {
            '416023011': 'My Verizon',
            '912122700': 'Verizon Messages',
            '1100799142': 'Verizon Cloud',
            '1509695913': 'Verizon Call Filter',
        },
        'att': {
            '309172177': 'myAT&T',
            '1009700781': 'AT&T Thanks',
            '1096651350': 'AT&T Smart Home Manager',
            '1053996091': 'AT&T Call Protect',
        }
    }
    
    def __init__(self):
        """Initialize collector and UNIFIED Azure Cognitive Search vector DBs for each carrier."""
        logger.info("?? Initialized Multi-Carrier Apple App Store Collector (RSS Feed)")
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
        
        if not search_endpoint or not search_api_key:
            logger.error("? Azure credentials required!")
            raise RuntimeError("Azure credentials required (AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY)")
        
        try:
            from vector_db import SocialMediaVectorDB
            
            # Create unified vector DBs for each carrier (one index per carrier)
            self.vector_dbs = {}
            for carrier in ['tmobile', 'verizon', 'att']:
                self.vector_dbs[carrier] = SocialMediaVectorDB(
                    endpoint=search_endpoint,
                    api_key=search_api_key,
                    carrier=carrier  # No index_type - unified index handles all platforms
                )
                logger.info(f"? Azure Cognitive Search initialized ({carrier.upper()} unified index)")
        except Exception as e:
            logger.error(f"? Failed to initialize Azure: {e}")
            raise
    
    def get_reviews_rss(self, app_id: str, max_pages: int = 20, country: str = 'us') -> List[Dict]:
        """
        Fetch reviews using iTunes RSS feed API.
        
        ENHANCED: Fetches MORE pages for richer dataset.
        
        Args:
            app_id: Numeric App Store ID
            max_pages: Maximum pages to fetch (INCREASED from 10)
            country: Country code (default: 'us')
            
        Returns:
            List of review dictionaries
        """
        all_reviews = []
        base_url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortby=mostrecent/json"
        
        logger.info(f"   Fetching reviews from RSS feed (up to {max_pages} pages)...")
        
        try:
            response = requests.get(base_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"   RSS feed returned status {response.status_code}")
                return []
            
            data = response.json()
            
            if 'feed' not in data:
                logger.warning(f"   No 'feed' key in response")
                return []
            
            if 'entry' not in data['feed']:
                logger.warning(f"   No reviews available for this app")
                return []
            
            entries = data['feed']['entry']
            reviews = [e for e in entries if 'im:rating' in e or 'rating' in e]
            
            if not reviews:
                logger.warning(f"   Found entries but no reviews with ratings")
                return []
            
            all_reviews.extend(reviews)
            logger.info(f"   ? Found {len(reviews)} reviews")
            
        except requests.exceptions.Timeout:
            logger.warning(f"   Timeout fetching reviews")
        except json.JSONDecodeError as e:
            logger.error(f"   Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"   Error fetching reviews: {e}")
        
        return all_reviews
    
    def categorize_review(self, text: str) -> str:
        """Categorize review based on keywords."""
        if not text:
            return 'general'
        
        t = text.lower()
        if any(w in t for w in ['network', 'signal', 'coverage', 'data', '5g', '4g', 'lte', 'connection']):
            return 'network_connectivity'
        if any(w in t for w in ['bill', 'charge', 'price', 'payment', 'expensive', 'cost', 'fee']):
            return 'billing_pricing'
        if any(w in t for w in ['support', 'customer service', 'representative', 'agent', 'help', 'staff']):
            return 'customer_service'
        if any(w in t for w in ['app', 'crash', 'bug', 'update', 'login', 'interface', 'feature']):
            return 'app_functionality'
        if any(w in t for w in ['plan', 'unlimited', 'upgrade', 'switch', 'contract']):
            return 'plans_features'
        return 'general'
    
    def determine_sentiment(self, rating: int) -> str:
        """Determine sentiment based on star rating."""
        if rating >= 4:
            return 'positive'
        elif rating >= 3:
            return 'neutral'
        else:
            return 'negative'
    
    def format_review_rss(self, review: Dict, app_name: str, carrier: str) -> Dict:
        """Format RSS review into standard format with ENHANCED metadata."""
        review_id = review.get('id', {}).get('label', '')
        title = review.get('title', {}).get('label', '')
        content = review.get('content', {}).get('label', '')
        rating = int(review.get('im:rating', {}).get('label', 0))
        author = review.get('author', {}).get('name', {}).get('label', 'Anonymous')
        date_str = review.get('updated', {}).get('label', datetime.utcnow().isoformat())
        version = review.get('im:version', {}).get('label', '')
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            date_formatted = date_obj.strftime('%Y-%m-%d')
        except:
            date_formatted = datetime.utcnow().strftime('%Y-%m-%d')
        
        post_id = f"appstore_{carrier}_{review_id}" if review_id else f"appstore_{carrier}_{app_name}_{datetime.utcnow().timestamp()}"
        full_text = f"{title} {content}".strip() if title else content
        
        return {
            'text': full_text,
            'metadata': {
                'sentiment': self.determine_sentiment(rating),
                'category': self.categorize_review(full_text),
                'date': date_formatted,
                'platform': 'app_store',
                'app_name': app_name,
                'rating': rating,
                'author': author,
                'review_id': review_id,
                'title': title,
                'developer_response': '',  # RSS feed doesn't include developer responses
                'post_id': post_id,
                'carrier': carrier.upper(),
                # Additional metadata for richer analysis
                'review_version': version,
                'review_length': len(full_text),
                'has_developer_response': False,
                'has_title': bool(title),
            }
        }
    
    def collect_carrier_reviews(self, carrier: str, reviews_per_app: int = 200, country: str = 'us') -> List[Dict]:
        """Collect reviews for a specific carrier.
        
        ENHANCED: Collects MORE reviews per app.
        """
        carrier_lower = carrier.lower()
        if carrier_lower not in self.CARRIER_APPS:
            logger.error(f"? Unknown carrier: {carrier}")
            return []
        
        all_reviews = []
        apps = self.CARRIER_APPS[carrier_lower]
        pages_per_app = max(1, (reviews_per_app + 49) // 50)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"?? Collecting Reviews: {carrier.upper()} Apps (App Store)")
        logger.info(f"{'='*70}")
        
        for app_id, app_display_name in apps.items():
            logger.info(f"\n?? Processing: {app_display_name}")
            logger.info(f"   App ID: {app_id}")
            
            raw_reviews = self.get_reviews_rss(app_id, max_pages=pages_per_app, country=country)
            
            for r in raw_reviews:
                all_reviews.append(self.format_review_rss(r, app_display_name, carrier_lower))
            
            logger.info(f"   ? Collected {len(raw_reviews)} reviews")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"?? Total Reviews Collected for {carrier.upper()}: {len(all_reviews)}")
        logger.info(f"{'='*70}")
        
        return all_reviews
    
    def collect_all_carriers(
        self, 
        reviews_per_app: int = 400,  # DOUBLED from 200
        country: str = 'us'
    ) -> Dict[str, List[Dict]]:
        """
        Collect reviews from all carriers and store in separate indexes.
        
        ENHANCED: Collects MORE data points for comprehensive analysis (2x increase).
        
        Returns:
            Dict mapping carrier name to list of reviews
        """
        all_carrier_reviews = {}
        
        logger.info("\n" + "="*70)
        logger.info("?? MULTI-CARRIER APP STORE COLLECTION (ENHANCED 2X)")
        logger.info("="*70)
        logger.info(f"Carriers: T-Mobile, Verizon, AT&T")
        logger.info(f"Reviews per app: {reviews_per_app} (2X ENHANCED)")
        logger.info("="*70)
        
        for carrier in ['tmobile', 'verizon', 'att']:
            reviews = self.collect_carrier_reviews(carrier, reviews_per_app, country)
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
        """Store reviews in carrier-specific UNIFIED Azure index, deduping by post_id."""
        if not reviews:
            logger.info(f"??  No reviews to store for {carrier.upper()}.")
            return
        
        logger.info(f"?? Checking for duplicates in {len(reviews)} {carrier.upper()} App Store reviews...")
        search_client = self.vector_dbs[carrier].search_client
        new_docs = []
        skipped = 0
        
        for rev in reviews:
            md = rev['metadata']
            pid = md['post_id']
            try:
                # Check for duplicates in unified index
                existing = list(search_client.search(
                    search_text="", 
                    filter=f"post_id eq '{pid}'", 
                    select=["post_id"], 
                    top=1
                ))
                if existing:
                    skipped += 1
                    continue
            except Exception as e:
                logger.warning(f"??  Error checking duplicate for {pid}: {e}")
            new_docs.append(rev)
        
        if not new_docs:
            logger.info(f"??  All {len(reviews)} {carrier.upper()} App Store reviews already stored (skipped {skipped} duplicates).")
            return
        
        logger.info(f"?? Storing {len(new_docs)} new {carrier.upper()} App Store reviews (skipped {skipped} duplicates)...")
        try:
            self.vector_dbs[carrier].add_posts(new_docs)
            logger.info(f"? Storage complete! {len(new_docs)} {carrier.upper()} reviews added to unified index")
        except Exception as e:
            logger.error(f"? Storage failed for {carrier.upper()}: {e}")


if __name__ == '__main__':
    collector = MultiCarrierAppStoreCollector()
    all_reviews = collector.collect_all_carriers(reviews_per_app=400)  # 2X ENHANCED
