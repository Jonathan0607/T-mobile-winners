"""
Vector Database module for storing and retrieving social media posts.
Auto-creates Azure Cognitive Search indexes if they don't exist.
NOW SUPPORTS CARRIER-SPECIFIC INDEXES - One index per carrier containing all platforms.
"""

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    ComplexField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    HnswParameters,
    VectorSearchProfile,
    SearchField
)
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os
import uuid
import logging

logger = logging.getLogger(__name__)

# Carrier-specific index names (ONE index per carrier, holds ALL platforms)
CARRIER_INDEX_NAMES = {
    "tmobile": "tmobile-all-reviews",
    "att": "att-all-reviews",
    "verizon": "verizon-all-reviews"
}

# Default for backward compatibility
DEFAULT_INDEX = 'tmobile-all-reviews'

class SocialMediaVectorDB:
    VECTOR_FIELD = "embedding"
    VECTOR_PROFILE = "my-vector-profile"
    HNSW_NAME = "my-hnsw-config"
    VECTOR_DIM = 384  # all-MiniLM-L6-v2

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        carrier: str = "tmobile"  # "tmobile", "verizon", "att"
    ):
        self.endpoint = endpoint or os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_SEARCH_API_KEY")
        if not self.endpoint:
            raise ValueError("AZURE_SEARCH_ENDPOINT missing")
        if not self.api_key:
            raise ValueError("AZURE_SEARCH_API_KEY missing")
        
        # Validate and set carrier
        self.carrier = carrier.lower() if carrier else 'tmobile'
        if self.carrier not in CARRIER_INDEX_NAMES:
            raise ValueError(f"carrier must be one of {list(CARRIER_INDEX_NAMES.keys())}")
        
        # Determine index name - one index per carrier
        if not index_name:
            index_name = CARRIER_INDEX_NAMES.get(self.carrier, DEFAULT_INDEX)
        
        self.index_name = index_name

        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create credential using AzureKeyCredential
        self.credential = AzureKeyCredential(self.api_key)
        
        # Create search index client
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        
        # Create search client
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

        self._ensure_index()
        self._log_diagnostics()

    # ---------- Vector field builder with compatibility handling ----------
    def _vector_search_field(self) -> SearchField:
        """Build the vector field using current SDK property names; fallback on older naming if needed."""
        try:
            # Primary (newer SDK) naming
            return SearchField(
                name=self.VECTOR_FIELD,
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                vector_search_dimensions=self.VECTOR_DIM,
                vector_search_profile_name=self.VECTOR_PROFILE
            )
        except TypeError:
            # Fallback (older preview naming) - attribute names may differ
            try:
                return SearchField(
                    name=self.VECTOR_FIELD,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    dimensions=self.VECTOR_DIM,  # older property name
                    vector_search_configuration_name=self.VECTOR_PROFILE
                )
            except TypeError as e:
                raise RuntimeError(f"Unable to build vector field with either naming convention: {e}")

    # --------------------- Unified Schema (All Platforms) ---------------------
    def _build_unified_fields(self):
        """
        Build unified field schema that supports ALL platform types:
        - Reddit posts
        - Google Play Store reviews  
        - Apple App Store reviews
        
        Uses 'platform' field to distinguish between sources.
        """
        return [
            # Core fields (all platforms)
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="text", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            self._vector_search_field(),
            SearchableField(name="sentiment", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="date", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SearchableField(name="platform", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),  # 'reddit', 'google_play', 'app_store'
            SimpleField(name="post_id", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="carrier", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="author", type=SearchFieldDataType.String, filterable=True),
            
            # App-specific fields (Play Store & App Store)
            SearchableField(name="app_name", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Int32, filterable=True, facetable=True, sortable=True),
            
            # Play Store specific
            SimpleField(name="thumbs_up", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SearchableField(name="reply_content", type=SearchFieldDataType.String),
            SearchableField(name="review_version", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
            SimpleField(name="reply_date", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SimpleField(name="has_reply", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
            SimpleField(name="user_image", type=SearchFieldDataType.String),
            
            # App Store specific
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="developer_response", type=SearchFieldDataType.String),
            SimpleField(name="has_developer_response", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
            
            # Universal for apps
            SimpleField(name="review_length", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            
            # Reddit specific
            SearchableField(name="subreddit", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="score", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="num_comments", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="url", type=SearchFieldDataType.String),
            SearchableField(name="top_comment", type=SearchFieldDataType.String),
            SimpleField(name="upvote_ratio", type=SearchFieldDataType.Double, filterable=True, sortable=True),
            SearchableField(name="flair", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="awards", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="is_self", type=SearchFieldDataType.Boolean, filterable=True, facetable=True)
        ]

    def _build_index_definition(self) -> SearchIndex:
        """Create the unified search index definition with vector search configuration."""
        fields = self._build_unified_fields()
        
        # Configure HNSW algorithm for vector search
        hnsw = HnswAlgorithmConfiguration(
            name=self.HNSW_NAME,
            parameters=HnswParameters(m=4, ef_construction=300, ef_search=300, metric="cosine")
        )
        
        # Create vector search configuration
        vector_search = VectorSearch(
            algorithms=[hnsw],
            profiles=[VectorSearchProfile(name=self.VECTOR_PROFILE, algorithm_configuration_name=self.HNSW_NAME)]
        )
        
        # Suggesters for autocomplete functionality
        suggesters = [{'name': 'sg', 'source_fields': ['category', 'platform', 'carrier', 'app_name', 'subreddit']}]
        
        # Create the search index
        return SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
            suggesters=suggesters,
            scoring_profiles=[]
        )

    # --------------------- Ensure/Update Index ---------------------
    def _ensure_index(self):
        """Ensure the index exists, creating or updating as needed."""
        try:
            existing = self.index_client.get_index(self.index_name)
            # Index exists - check if it has the required fields
            current_field_names = {f.name for f in existing.fields}
            
            # Get required fields
            required_fields = {f.name for f in self._build_unified_fields()}
            
            missing = required_fields - current_field_names
            
            # Only check for critical fields (id, text, embedding)
            critical_fields = {"id", "text", self.VECTOR_FIELD}
            missing_critical = critical_fields - current_field_names
            
            if missing_critical:
                # Critical fields are missing, but don't try to recreate if we're at quota limit
                logger.warning(f"Index '{self.index_name}' missing critical fields {missing_critical}. Index may not work properly.")
                logger.info(f"✅ Using existing index '{self.index_name}' (may have limitations)")
            elif missing:
                # Non-critical fields missing, but index is usable
                logger.info(f"✅ Using existing index '{self.index_name}' (some optional fields missing: {missing})")
            else:
                logger.info(f"✅ Using existing index '{self.index_name}'")
        except Exception as e:
            error_msg = str(e)
            # Check if index doesn't exist (404) or if it's a quota issue (429)
            if "404" in error_msg or "not found" in error_msg.lower():
                logger.info(f"Creating index '{self.index_name}' (reason: index not found)")
                try:
                    result = self.index_client.create_or_update_index(self._build_index_definition())
                    logger.info(f"✅ {result.name} created")
                except Exception as create_error:
                    if "429" in str(create_error) or "quota" in str(create_error).lower():
                        logger.warning(f"⚠️ Cannot create index '{self.index_name}': Quota exceeded. Please use existing indexes or upgrade your Azure plan.")
                        raise
                    else:
                        raise
            elif "429" in error_msg or "quota" in error_msg.lower():
                logger.warning(f"⚠️ Cannot create index '{self.index_name}': Quota exceeded. Index may already exist - trying to use it.")
                # Try to use the index anyway - it might exist but we can't verify due to quota
                try:
                    # Just verify we can access it
                    self.search_client.get_document_count()
                    logger.info(f"✅ Index '{self.index_name}' is accessible")
                except:
                    raise ValueError(f"Cannot access index '{self.index_name}' and cannot create new one due to quota limits")
            else:
                raise

    def _log_diagnostics(self):
        """Log diagnostic information about the index."""
        try:
            count = self.search_client.get_document_count()
            logger.info(f"🔍 Index '{self.index_name}' doc count: {count}")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch document count: {e}")

    # --------------------- Insert Posts ---------------------
    def add_posts(self, posts: List[Dict[str, any]]):
        """Add posts to the search index with embeddings."""
        if not posts:
            logger.info("ℹ️ No posts provided")
            return
        
        texts = [p['text'] for p in posts]
        try:
            embeddings = self.encoder.encode(texts, show_progress_bar=False)
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            return
        
        documents = []
        for i, p in enumerate(posts):
            md = p.get('metadata', {})
            platform = md.get('platform', 'unknown')
            
            # Base document structure (all platforms)
            doc = {
                'id': str(uuid.uuid4()),
                'text': p.get('text',''),
                'embedding': embeddings[i].tolist(),
                'sentiment': md.get('sentiment',''),
                'category': md.get('category',''),
                'date': md.get('date',''),
                'platform': platform,
                'post_id': md.get('post_id',''),
                'carrier': md.get('carrier',''),
                'author': md.get('author',''),
                'app_name': md.get('app_name',''),
                'rating': int(md.get('rating',0)) if md.get('rating') is not None else None,
                'thumbs_up': int(md.get('thumbs_up',0)) if md.get('thumbs_up') is not None else None,
                'reply_content': md.get('reply_content',''),
                'review_version': md.get('review_version',''),
                'reply_date': md.get('reply_date',''),
                'has_reply': bool(md.get('reply_content','')),
                'user_image': md.get('user_image',''),
                'title': md.get('title',''),
                'developer_response': md.get('developer_response',''),
                'has_developer_response': bool(md.get('developer_response','')),
                'review_length': len(p.get('text','')),
                'subreddit': md.get('subreddit',''),
                'score': int(md.get('score',0)) if md.get('score') is not None else None,
                'num_comments': int(md.get('num_comments',0)) if md.get('num_comments') is not None else None,
                'url': md.get('url',''),
                'top_comment': p.get('top_comment',''),
                'upvote_ratio': md.get('upvote_ratio',0.0),
                'flair': md.get('flair',''),
                'awards': md.get('awards',0),
                'is_self': md.get('is_self', False)
            }
            
            documents.append(doc)
        
        results = self.search_client.upload_documents(documents=documents)
        succeeded = sum(1 for r in results if r.succeeded)
        failed = [r for r in results if not r.succeeded]
        logger.info(f"📦 Uploaded {succeeded}/{len(documents)} documents to index '{self.index_name}'")
        for f in failed:
            logger.error(f"❌ Failed key={f.key} error={f.error_message}")

    # --------------------- Search ---------------------
    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Perform vector search on the index."""
        from azure.search.documents.models import VectorizedQuery
        
        embedding = self.encoder.encode([query], show_progress_bar=False)[0]
        vector_query = VectorizedQuery(vector=embedding.tolist(), k_nearest_neighbors=top_k, fields="embedding")
        
        filter_expression = None
        if filter_metadata:
            filter_parts = []
            for k, v in filter_metadata.items():
                if isinstance(v, str):
                    filter_parts.append(f"{k} eq '{v}'")
                elif isinstance(v, bool):
                    filter_parts.append(f"{k} eq {str(v).lower()}")
                else:
                    filter_parts.append(f"{k} eq {v}")
            filter_expression = " and ".join(filter_parts)
        
        # All fields available in unified schema
        select_fields = ["id","text","sentiment","category","date","platform","post_id","carrier",
                        "author","app_name","rating","thumbs_up","reply_content","review_version",
                        "reply_date","has_reply","user_image","title","developer_response",
                        "has_developer_response","review_length","subreddit","score","num_comments",
                        "url","top_comment","upvote_ratio","flair","awards","is_self"]
        
        results_iter = self.search_client.search(
            search_text="",
            vector_queries=[vector_query],
            top=top_k,
            filter=filter_expression,
            select=select_fields
        )
        
        return list(results_iter)

    def retrieve_context(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> str:
        """Retrieve context for RAG queries."""
        results = self.search(query, top_k, filter_metadata)
        if not results:
            return "No relevant posts found."
        parts = []
        for i, r in enumerate(results, 1):
            platform = r.get('platform', 'unknown')
            parts.append(f"{i}. [{platform.upper()}] {r['text']}")
        return "\n".join(parts)

    # --------------------- Maintenance / Deduplication ---------------------
    def _iterate_all_documents(self, select_fields=None, page_size: int = 1000):
        """Internal generator to iterate all documents in the index with paging."""
        select_fields = select_fields or ["id", "post_id", "text", self.VECTOR_FIELD]
        try:
            results = self.search_client.search(
                search_text="*",
                top=page_size,
                select=select_fields
            )
            for doc in results:
                yield doc
            # Handle continuation tokens if SDK provides them
            while hasattr(results, "get_continuation_token"):
                token = results.get_continuation_token()
                if not token:
                    break
                results = self.search_client.search(
                    search_text="*",
                    top=page_size,
                    continuation_token=token,
                    select=select_fields
                )
                for doc in results:
                    yield doc
        except Exception as e:
            logger.error(f"❌ Failed iterating documents: {e}")
            return

    def remove_duplicates(
        self,
        by: str = "embedding",  # options: embedding, post_id, text
        embedding_precision: int = 4,
        page_size: int = 1000,
        dry_run: bool = True
    ) -> Dict[str, any]:
        """
        Detect and optionally remove duplicate documents from the index.

        Args:
            by: Criterion for duplicate detection: 'embedding', 'post_id', or 'text'.
            embedding_precision: Decimal precision for rounding embedding floats when hashing (used if by='embedding').
            page_size: Number of docs per page when scanning.
            dry_run: If True, only report duplicates without deleting.

        Returns:
            Summary dict: { 'criterion', 'total', 'unique', 'duplicates', 'removed', 'dry_run', 'details': [...] }
        """
        if by not in {"embedding", "post_id", "text"}:
            raise ValueError("'by' must be one of: embedding, post_id, text")

        logger.info(f"🔍 Starting duplicate scan by '{by}' (dry_run={dry_run}) on index '{self.index_name}'...")
        total = 0
        duplicate_count = 0
        to_delete_keys = []
        details = []
        seen = {}

        # Choose select fields
        select_fields = ["id", "post_id", "text"]
        if by == "embedding":
            select_fields.append(self.VECTOR_FIELD)

        for doc in self._iterate_all_documents(select_fields=select_fields, page_size=page_size):
            total += 1
            doc_id = doc.get("id")
            post_id = doc.get("post_id")
            text_val = doc.get("text", "")
            key = None

            if by == "post_id":
                key = post_id or ""
            elif by == "text":
                key = text_val.strip().lower()
            elif by == "embedding":
                emb = doc.get(self.VECTOR_FIELD)
                if emb is None:
                    # Fallback to text if embedding missing
                    key = f"NOEMB::{text_val.strip().lower()}"
                else:
                    # Create a rounded hash string to tolerate float noise
                    try:
                        rounded = [round(float(x), embedding_precision) for x in emb]
                        key = "|".join(map(str, rounded))
                    except Exception:
                        key = f"BAD_EMB::{text_val.strip().lower()}"

            if key in seen:
                duplicate_count += 1
                original_id = seen[key]
                details.append({
                    'duplicate_id': doc_id,
                    'original_id': original_id,
                    'post_id': post_id,
                    'criterion_key': key
                })
                to_delete_keys.append(doc_id)
            else:
                seen[key] = doc_id

        unique = len(seen)
        logger.info(f"✅ Scan complete. Total={total} Unique={unique} Duplicates={duplicate_count}")

        removed = 0
        if not dry_run and to_delete_keys:
            logger.info(f"🗑️ Deleting {len(to_delete_keys)} duplicate documents...")
            try:
                # Azure Search delete requires documents with key field
                delete_payload = [{'id': k} for k in to_delete_keys]
                results = self.search_client.delete_documents(documents=delete_payload)
                removed = sum(1 for r in results if r.succeeded)
                failed = [r for r in results if not r.succeeded]
                if failed:
                    for f in failed:
                        logger.error(f"❌ Delete failed key={f.key} error={f.error_message}")
                logger.info(f"🧹 Removed {removed}/{len(to_delete_keys)} duplicates")
            except Exception as e:
                logger.error(f"❌ Failed deleting duplicates: {e}")

        summary = {
            'index': self.index_name,
            'criterion': by,
            'total': total,
            'unique': unique,
            'duplicates': duplicate_count,
            'removed': removed,
            'dry_run': dry_run,
            'details': details[:50]  # include sample of first 50 duplicates
        }
        logger.info(f"📒 Summary: {summary}")
        return summary

