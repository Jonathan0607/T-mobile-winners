"""
Agentic RAG implementation with intelligent retrieval decision-making.
The agent decides WHEN to retrieve information from the vector database.
Supports querying from multiple Azure Cognitive Search indexes (Reddit, Play Store).
"""

from nemotron_client import NemotronClient
from vector_db import SocialMediaVectorDB
from typing import Dict, Optional, List, Union
import json


class AgenticRAG:
    """Agentic RAG system that intelligently decides when to retrieve context from multiple indexes."""
    
    def __init__(
        self, 
        nemotron_client: NemotronClient, 
        vector_dbs: Union[SocialMediaVectorDB, Dict[str, SocialMediaVectorDB]]
    ):
        """
        Initialize the Agentic RAG system.
        
        Args:
            nemotron_client: Initialized Nemotron client
            vector_dbs: Either a single SocialMediaVectorDB or a dict mapping index types to databases
                       e.g., {'reddit': reddit_db, 'playstore': playstore_db}
        """
        self.nemotron = nemotron_client
        
        # Support both single DB (backward compatibility) and multiple DBs
        if isinstance(vector_dbs, dict):
            self.vector_dbs = vector_dbs
            self.multi_index = True
        else:
            self.vector_dbs = {'default': vector_dbs}
            self.multi_index = False
        
        # Define the retrieval tool schemas based on available indexes
        self.tool_schemas = self._build_tool_schemas()
    
    def _build_tool_schemas(self) -> List[Dict]:
        """Build tool schemas based on available indexes."""
        schemas = []
        
        if self.multi_index:
            # Separate tools for each index
            if 'reddit' in self.vector_dbs:
                schemas.append({
                    "type": "function",
                    "function": {
                        "name": "retrieve_reddit_posts",
                        "description": "Searches Reddit posts from r/tmobile subreddit for relevant discussions, complaints, or feedback. Use this when looking for community discussions, user experiences, or general feedback on Reddit.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_query": {
                                    "type": "string",
                                    "description": "Search query to find relevant Reddit posts"
                                },
                                "top_k": {
                                    "type": "integer",
                                    "description": "Number of posts to retrieve (default: 5)",
                                    "default": 5
                                },
                                "filter_metadata": {
                                    "type": "object",
                                    "description": "Optional filters (e.g., {'sentiment': 'negative', 'category': 'network_connectivity'})",
                                    "default": {}
                                }
                            },
                            "required": ["search_query"]
                        }
                    }
                })
            
            if 'playstore' in self.vector_dbs:
                schemas.append({
                    "type": "function",
                    "function": {
                        "name": "retrieve_playstore_reviews",
                        "description": "Searches Google Play Store app reviews for T-Mobile apps. Use this when looking for app-specific feedback, ratings, bugs, or feature requests.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_query": {
                                    "type": "string",
                                    "description": "Search query to find relevant app reviews"
                                },
                                "top_k": {
                                    "type": "integer",
                                    "description": "Number of reviews to retrieve (default: 5)",
                                    "default": 5
                                },
                                "filter_metadata": {
                                    "type": "object",
                                    "description": "Optional filters (e.g., {'app_name': 'T-Mobile', 'rating': 1})",
                                    "default": {}
                                }
                            },
                            "required": ["search_query"]
                        }
                    }
                })
            
            # Add a combined search tool
            schemas.append({
                "type": "function",
                "function": {
                    "name": "retrieve_all_platforms",
                    "description": "Searches ALL available platforms (Reddit + Play Store) for comprehensive feedback. Use this when you need broad coverage across multiple sources.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "Search query to find relevant posts/reviews across all platforms"
                            },
                            "top_k_per_platform": {
                                "type": "integer",
                                "description": "Number of results per platform (default: 3)",
                                "default": 3
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            })
        else:
            # Single tool for backward compatibility
            schemas.append({
                "type": "function",
                "function": {
                    "name": "retrieve_social_media_posts",
                    "description": "Searches the internal social media feedback database for relevant posts. Use this tool when the user's query requires specific, domain-specific information about the service, customer feedback, complaints, or social media posts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "The precise search query to find relevant social media posts"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of posts to retrieve (default: 5)",
                                "default": 5
                            },
                            "filter_metadata": {
                                "type": "object",
                                "description": "Optional metadata filters",
                                "default": {}
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            })
        
        return schemas
    
    def retrieve_reddit_posts(
        self, 
        search_query: str, 
        top_k: int = 5, 
        filter_metadata: Optional[Dict] = None
    ) -> str:
        """Retrieve posts from Reddit index."""
        if 'reddit' not in self.vector_dbs:
            return "Error: Reddit index not available"
        
        if filter_metadata is None or (isinstance(filter_metadata, dict) and len(filter_metadata) == 0):
            filter_metadata = None
        
        context = self.vector_dbs['reddit'].retrieve_context(search_query, top_k, filter_metadata)
        return f"[Reddit Posts]\n{context}"
    
    def retrieve_playstore_reviews(
        self, 
        search_query: str, 
        top_k: int = 5, 
        filter_metadata: Optional[Dict] = None
    ) -> str:
        """Retrieve reviews from Play Store index."""
        if 'playstore' not in self.vector_dbs:
            return "Error: Play Store index not available"
        
        if filter_metadata is None or (isinstance(filter_metadata, dict) and len(filter_metadata) == 0):
            filter_metadata = None
        
        context = self.vector_dbs['playstore'].retrieve_context(search_query, top_k, filter_metadata)
        return f"[Google Play Store Reviews]\n{context}"
    
    def retrieve_all_platforms(
        self, 
        search_query: str, 
        top_k_per_platform: int = 3
    ) -> str:
        """Retrieve from all available platforms."""
        results = []
        
        if 'reddit' in self.vector_dbs:
            reddit_context = self.vector_dbs['reddit'].retrieve_context(search_query, top_k_per_platform)
            results.append(f"[Reddit Posts]\n{reddit_context}")
        
        if 'playstore' in self.vector_dbs:
            playstore_context = self.vector_dbs['playstore'].retrieve_context(search_query, top_k_per_platform)
            results.append(f"[Google Play Store Reviews]\n{playstore_context}")
        
        return "\n\n".join(results)
    
    def retrieve_social_media_posts(
        self, 
        search_query: str, 
        top_k: int = 5, 
        filter_metadata: Optional[Dict] = None
    ) -> str:
        """Backward compatibility method for single DB mode."""
        if 'default' in self.vector_dbs:
            if filter_metadata is None or (isinstance(filter_metadata, dict) and len(filter_metadata) == 0):
                filter_metadata = None
            return self.vector_dbs['default'].retrieve_context(search_query, top_k, filter_metadata)
        else:
            # If multi-index, combine all
            return self.retrieve_all_platforms(search_query, top_k)
    
    def query(self, user_query: str, system_prompt: Optional[str] = None) -> str:
        """
        Query the agentic RAG system. The agent decides if retrieval is needed.
        
        Args:
            user_query: User's question or request
            system_prompt: Optional custom system prompt (uses default if None)
        
        Returns:
            Agent's response with retrieved context if needed
        """
        if system_prompt is None:
            if self.multi_index:
                system_prompt = (
                    "You are an intelligent Research Agent with access to multiple data sources.\n\n"
                    "AVAILABLE TOOLS:\n"
                )
                if 'reddit' in self.vector_dbs:
                    system_prompt += "- retrieve_reddit_posts: Search Reddit r/tmobile discussions\n"
                if 'playstore' in self.vector_dbs:
                    system_prompt += "- retrieve_playstore_reviews: Search Google Play Store app reviews\n"
                system_prompt += "- retrieve_all_platforms: Search ALL platforms for comprehensive coverage\n\n"
                
                system_prompt += (
                    "DECISION RULES:\n"
                    "1. For app-specific issues (crashes, bugs, UI): Use retrieve_playstore_reviews\n"
                    "2. For general service feedback (network, billing, support): Use retrieve_reddit_posts\n"
                    "3. For comprehensive analysis: Use retrieve_all_platforms\n"
                    "4. For general knowledge questions: Answer directly without tools\n\n"
                    "After retrieving context, analyze it thoroughly and provide a comprehensive answer."
                )
            else:
                system_prompt = (
                    "You are an intelligent Research Agent. Your goal is to gather accurate, "
                    "relevant information to answer user queries.\n\n"
                    "You have access to a tool called 'retrieve_social_media_posts' that searches "
                    "an internal database of social media posts about a service.\n\n"
                    "DECISION RULES:\n"
                    "1. If the query requires specific, domain-specific information, use the tool.\n"
                    "2. If the query is general knowledge, answer directly without using the tool.\n"
                    "3. After retrieving context, analyze it and provide a comprehensive answer.\n\n"
                    "Always be thorough and accurate in your responses."
                )
        
        # Define the tools mapping
        tools = {}
        if self.multi_index:
            if 'reddit' in self.vector_dbs:
                tools['retrieve_reddit_posts'] = self.retrieve_reddit_posts
            if 'playstore' in self.vector_dbs:
                tools['retrieve_playstore_reviews'] = self.retrieve_playstore_reviews
            tools['retrieve_all_platforms'] = self.retrieve_all_platforms
        else:
            tools['retrieve_social_media_posts'] = self.retrieve_social_media_posts
        
        # Call with tool support
        response = self.nemotron.call_with_tools(
            system_prompt=system_prompt,
            user_prompt=user_query,
            tools=tools,
            tool_schemas=self.tool_schemas
        )
        
        return response
    
    def direct_prompt(
        self,
        prompt: str,
        retrieval_query: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        top_k: int = 5,
        system_prompt: Optional[str] = None,
        filter_metadata: Optional[Dict] = None,
    ) -> str:
        """Directly prompt the RAG agent while forcing retrieval first.
        
        This is a convenience wrapper that:
        1. Performs vector retrieval on the requested platforms (or all available)
        2. Concatenates retrieved context
        3. Sends a single chat completion to the model WITHOUT tool calling
        
        Args:
            prompt: User's question.
            retrieval_query: Query used for retrieval (defaults to the prompt).
            platforms: List of platform keys to search (e.g. ['reddit','playstore']). If None, use all.
            top_k: Number of results per platform.
            system_prompt: Optional system prompt override.
            filter_metadata: Optional metadata filters passed to each retrieval.
        Returns:
            Model response string.
        """
        if retrieval_query is None:
            retrieval_query = prompt
        if platforms is None:
            # Use all known indexes; for single-db mode use 'default'
            platforms = list(self.vector_dbs.keys())
        # Normalize metadata filters
        fm = filter_metadata if filter_metadata else None
        # Collect context pieces
        context_sections = []
        for key in platforms:
            if key not in self.vector_dbs:
                continue
            try:
                db = self.vector_dbs[key]
                ctx = db.retrieve_context(retrieval_query, top_k, fm)
                header = {
                    'reddit': 'Reddit Posts',
                    'playstore': 'Google Play Store Reviews',
                    'appstore': 'Apple App Store Reviews',
                    'default': 'Social Media Posts'
                }.get(key, key.title())
                context_sections.append(f"[{header}]\n{ctx}")
            except Exception as e:
                context_sections.append(f"[{key}] Retrieval error: {e}")
        combined_context = "\n\n".join(context_sections) if context_sections else "No context retrieved."
        # Build system prompt
        if system_prompt is None:
            system_prompt = (
                "You are an assistant analyzing user feedback from multiple sources. "
                "Use the retrieved context below to answer the user's question. "
                "If the context is insufficient, state what additional data would be needed."
            )
        final_user_prompt = (
            f"User Question:\n{prompt}\n\nRetrieved Context:\n{combined_context}\n\n" \
            "Provide a concise, accurate answer synthesizing the context."
        )
        # Prefer a simple chat call if available
        try:
            if hasattr(self.nemotron, 'chat'):
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": final_user_prompt}
                ]
                return self.nemotron.chat(messages)
            # Fallback to tool call without tools
            return self.nemotron.call_with_tools(
                system_prompt=system_prompt,
                user_prompt=final_user_prompt,
                tools={},
                tool_schemas=[]
            )
        except Exception as e:
            return f"Error generating response: {e}"

