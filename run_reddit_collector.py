"""
Standalone Reddit collector - collects posts from r/tmobile and displays them.
No Azure dependencies required.
Saves posts with metadata and top comments to a .txt file.
"""

from reddit_collector import RedditCollector
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Collect and display Reddit posts."""
    
    logger.info("=" * 60)
    logger.info("📱 Reddit Collector - r/tmobile")
    logger.info("=" * 60)
    
    # Initialize collector
    collector = RedditCollector()
    
    if not collector.reddit:
        logger.error("❌ Reddit client not initialized. Check your credentials.")
        return
    
    # Collect posts
    logger.info("\n📥 Collecting posts from r/tmobile...")
    
    # Collect all types
    posts = collector.collect_all_types(subreddit_name="tmobile", limit_per_type=10)
    
    if not posts:
        logger.warning("⚠️  No posts collected.")
        return
    
    # Display results
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Collected {len(posts)} unique posts")
    logger.info("=" * 60)
    
    # Show first 5 posts
    logger.info("\n📝 Sample Posts (showing first 5):\n")
    for i, post in enumerate(posts[:5], 1):
        logger.info(f"{i}. {post['text'][:100]}...")
        logger.info(f"   Category: {post['metadata']['category']} | Score: {post['metadata'].get('score', 'N/A')} | Date: {post['metadata']['date']}")
        logger.info("")
    
    if len(posts) > 5:
        logger.info(f"... and {len(posts) - 5} more posts")
    
    # Category breakdown
    categories = {}
    for post in posts:
        cat = post['metadata']['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 Posts by Category")
    logger.info("=" * 60)
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {cat.replace('_', ' ').title()}: {count}")
    
    logger.info("\n✅ Collection complete!")
    logger.info(f"💡 You can use these {len(posts)} posts for analysis or storage.")
    
    # Save to file
    save_to_file(posts)


def save_to_file(posts):
    """Save posts with metadata and top comments to a .txt file."""
    
    if not posts:
        logger.warning("No posts to save.")
        return
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reddit_posts_{timestamp}.txt"
    
    logger.info(f"\n💾 Saving posts to {filename}...")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("T-MOBILE REDDIT POSTS COLLECTION\n")
            f.write(f"Collected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Posts: {len(posts)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, post in enumerate(posts, 1):
                f.write(f"\n{'=' * 80}\n")
                f.write(f"POST #{i}\n")
                f.write(f"{'=' * 80}\n\n")
                
                # Metadata
                metadata = post['metadata']
                f.write("METADATA:\n")
                f.write(f"  Post ID: {metadata['post_id']}\n")
                f.write(f"  Category: {metadata['category']}\n")
                f.write(f"  Date: {metadata['date']}\n")
                f.write(f"  Platform: {metadata['platform']}\n")
                f.write(f"  Subreddit: {metadata.get('subreddit', 'tmobile')}\n")
                f.write(f"  Score: {metadata.get('score', 'N/A')}\n")
                f.write(f"  Comments: {metadata.get('num_comments', 'N/A')}\n")
                if 'url' in metadata:
                    f.write(f"  URL: {metadata['url']}\n")
                f.write("\n")
                
                # Post text
                f.write("POST TEXT:\n")
                f.write("-" * 80 + "\n")
                f.write(post['text'] + "\n")
                f.write("-" * 80 + "\n\n")
                
                # Top comment
                top_comment = post.get('top_comment', '')
                if top_comment:
                    f.write("TOP COMMENT:\n")
                    f.write("-" * 80 + "\n")
                    f.write(top_comment + "\n")
                    f.write("-" * 80 + "\n")
                else:
                    f.write("TOP COMMENT: (No comments available)\n")
                
                f.write("\n")
        
        logger.info(f"✅ Posts saved to {filename}")
        logger.info(f"📄 File location: {os.path.abspath(filename)}")
        
    except Exception as e:
        logger.error(f"❌ Error saving to file: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

