"""
Vector Database module for storing and retrieving social media posts.
Auto-creates Azure Cognitive Search indexes if they don't exist.
Supports separate indexes for Google Play reviews and Reddit posts.
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

PLAYSTORE_DEFAULT_INDEX = "tmobile-playstore-reviews"
REDDIT_DEFAULT_INDEX = "tmobile-reddit-posts"

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
        index_type: str = "playstore"  # or "reddit"
    ):
        self.endpoint = endpoint or os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_SEARCH_API_KEY")
        if not self.endpoint:
            raise ValueError("AZURE_SEARCH_ENDPOINT missing")
        if not self.api_key:
            raise ValueError("AZURE_SEARCH_API_KEY missing")
        if index_type not in {"playstore", "reddit"}:
            raise ValueError("index_type must be 'playstore' or 'reddit'")
        self.index_type = index_type
        if not index_name:
            index_name = PLAYSTORE_DEFAULT_INDEX if index_type == "playstore" else REDDIT_DEFAULT_INDEX
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

    # --------------------- Index Schema Builders ---------------------
    def _build_playstore_fields(self):
        """Build field schema for Play Store reviews index."""
        return [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="text", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            self._vector_search_field(),
            SearchableField(name="sentiment", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="date", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SearchableField(name="platform", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="post_id", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="carrier", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="app_name", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Int32, filterable=True, facetable=True, sortable=True),
            SimpleField(name="thumbs_up", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SearchableField(name="author", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="reply_content", type=SearchFieldDataType.String)
        ]

    def _build_reddit_fields(self):
        """Build field schema for Reddit posts index."""
        return [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="text", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            self._vector_search_field(),
            SearchableField(name="sentiment", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="date", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SearchableField(name="platform", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="post_id", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="carrier", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="subreddit", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
            SimpleField(name="score", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="num_comments", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="url", type=SearchFieldDataType.String),
            SearchableField(name="top_comment", type=SearchFieldDataType.String)
        ]

    def _build_index_definition(self) -> SearchIndex:
        """Create the search index definition with vector search configuration."""
        # Select fields based on index type
        fields = self._build_playstore_fields() if self.index_type == "playstore" else self._build_reddit_fields()
        
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
        suggesters = [{'name': 'sg', 'source_fields': ['category', 'platform', 'carrier']}]
        
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
            current_field_names = {f.name for f in existing.fields}
            required_fields = {f.name for f in (self._build_playstore_fields() if self.index_type == "playstore" else self._build_reddit_fields())}
            missing = required_fields - current_field_names
            
            # Validate embedding field dimension (attempt both property names)
            embedding_field = next((f for f in existing.fields if f.name == self.VECTOR_FIELD), None)
            dim_val = None
            if embedding_field:
                dim_val = getattr(embedding_field, 'vector_search_dimensions', None) or getattr(embedding_field, 'dimensions', None)
            dim_mismatch = embedding_field and dim_val != self.VECTOR_DIM
            
            if missing or dim_mismatch:
                logger.warning(f"Index '{self.index_name}' missing fields {missing} or dimension mismatch={dim_mismatch}. Recreating index.")
                self.index_client.delete_index(self.index_name)
                result = self.index_client.create_or_update_index(self._build_index_definition())
                logger.info(f"✅ {result.name} created/updated")
            else:
                logger.info(f"✅ Using existing index '{self.index_name}'")
        except Exception as e:
            logger.info(f"Creating index '{self.index_name}' (reason: {e})")
            result = self.index_client.create_or_update_index(self._build_index_definition())
            logger.info(f"✅ {result.name} created")

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
            doc = {
                'id': str(uuid.uuid4()),
                'text': p.get('text',''),
                'embedding': embeddings[i].tolist(),
                'sentiment': md.get('sentiment',''),
                'category': md.get('category',''),
                'date': md.get('date',''),
                'platform': md.get('platform',''),
                'post_id': md.get('post_id',''),
                'carrier': md.get('carrier','T-Mobile')
            }
            
            if self.index_type == 'playstore':
                doc.update({
                    'app_name': md.get('app_name',''),
                    'rating': int(md.get('rating',0)) if md.get('rating') is not None else None,
                    'thumbs_up': int(md.get('thumbs_up',0)) if md.get('thumbs_up') is not None else None,
                    'author': md.get('author',''),
                    'reply_content': md.get('reply_content','')
                })
            else:  # reddit
                doc.update({
                    'subreddit': md.get('subreddit',''),
                    'score': int(md.get('score',0)) if md.get('score') is not None else None,
                    'num_comments': int(md.get('num_comments',0)) if md.get('num_comments') is not None else None,
                    'url': md.get('url',''),
                    'top_comment': p.get('top_comment','')
                })
            
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
                filter_parts.append(f"{k} eq '{v}'")
            filter_expression = " and ".join(filter_parts)
        
        if self.index_type == 'playstore':
            select_fields = ["id","text","sentiment","category","date","platform","post_id","carrier","app_name","rating","thumbs_up","author","reply_content"]
        else:
            select_fields = ["id","text","sentiment","category","date","platform","post_id","carrier","subreddit","score","num_comments","url","top_comment"]
        
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
            parts.append(f"{i}. {r['text']}")
        return "\n".join(parts)

