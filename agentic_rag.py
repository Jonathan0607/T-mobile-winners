"""
Agentic RAG implementation with intelligent retrieval decision-making.
The agent decides WHEN to retrieve information from the vector database.
ENHANCED: Ensures comprehensive multi-platform retrieval for thorough analysis.
"""

from nemotron_client import NemotronClient
from vector_db import SocialMediaVectorDB
from typing import Dict, Optional, List, Union
import json


class AgenticRAG:
    """Agentic RAG system that intelligently retrieves context from UNIFIED carrier indexes."""
    
    def __init__(
        self, 
        nemotron_client: NemotronClient, 
        vector_dbs: Union[SocialMediaVectorDB, Dict[str, SocialMediaVectorDB]]
    ):
        """
        Initialize the Agentic RAG system.
        
        Args:
            nemotron_client: Initialized Nemotron client
            vector_dbs: Dict mapping carrier names to unified databases
                       e.g., {'tmobile': tmobile_db, 'verizon': verizon_db, 'att': att_db}
        """
        self.nemotron = nemotron_client
        
        # Support both single DB (backward compatibility) and multiple DBs
        if isinstance(vector_dbs, dict):
            self.vector_dbs = vector_dbs
            self.multi_index = True
        else:
            self.vector_dbs = {'default': vector_dbs}
            self.multi_index = False
        
        # Define the retrieval tool schemas
        self.tool_schemas = self._build_tool_schemas()
    
    def _build_tool_schemas(self) -> List[Dict]:
        """Build tool schemas for unified carrier indexes."""
        schemas = []
        
        # Tool to retrieve from ALL platforms within a carrier index
        schemas.append({
            "type": "function",
            "function": {
                "name": "retrieve_carrier_feedback",
                "description": "Searches ALL platforms (Reddit, Play Store, App Store) for a specific carrier. Returns comprehensive feedback from community discussions, Android reviews, and iOS reviews. ALWAYS USE THIS for thorough multi-platform analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "carrier": {
                            "type": "string",
                            "description": "Carrier to search ('tmobile', 'verizon', or 'att')",
                            "enum": ["tmobile", "verizon", "att"]
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Search query to find relevant feedback across all platforms"
                        },
                        "top_k_per_platform": {
                            "type": "integer",
                            "description": "Number of results per platform (default: 10 for comprehensive analysis)",
                            "default": 10
                        }
                    },
                    "required": ["carrier", "search_query"]
                }
            }
        })
        
        # Tool to retrieve from specific platform only (when needed)
        schemas.append({
            "type": "function",
            "function": {
                "name": "retrieve_platform_specific",
                "description": "Searches a SPECIFIC platform (Reddit, Play Store, or App Store) for a carrier. Use only when platform-specific insights are needed. For comprehensive analysis, use retrieve_carrier_feedback instead.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "carrier": {
                            "type": "string",
                            "description": "Carrier to search",
                            "enum": ["tmobile", "verizon", "att"]
                        },
                        "platform": {
                            "type": "string",
                            "description": "Platform to search",
                            "enum": ["reddit", "google_play", "app_store"]
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["carrier", "platform", "search_query"]
                }
            }
        })
        
        # Tool to compare ALL carriers across ALL platforms
        schemas.append({
            "type": "function",
            "function": {
                "name": "retrieve_competitive_comparison",
                "description": "Searches ALL carriers (T-Mobile, Verizon, AT&T) across ALL platforms (Reddit, Play Store, App Store) for competitive analysis. MANDATORY for comparison queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "Search query to find comparable feedback across all carriers"
                        },
                        "top_k_per_carrier_platform": {
                            "type": "integer",
                            "description": "Results per carrier per platform (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["search_query"]
                }
            }
        })
        
        return schemas
    
    def retrieve_carrier_feedback(
        self, 
        carrier: str,
        search_query: str, 
        top_k_per_platform: int = 10
    ) -> str:
        """
        Retrieve from ALL platforms for a specific carrier.
        
        ENHANCED: Ensures comprehensive multi-platform retrieval.
        """
        carrier_lower = carrier.lower()
        if carrier_lower not in self.vector_dbs:
            return f"Error: {carrier.upper()} index not available"
        
        db = self.vector_dbs[carrier_lower]
        results_by_platform = {}
        
        # Retrieve from each platform
        for platform in ['reddit', 'google_play', 'app_store']:
            try:
                platform_results = db.search(
                    query=search_query,
                    top_k=top_k_per_platform,
                    filter_metadata={'platform': platform}
                )
                results_by_platform[platform] = platform_results
            except Exception as e:
                results_by_platform[platform] = []
        
        # Format results with platform headers
        output = [f"[{carrier.upper()} - COMPREHENSIVE MULTI-PLATFORM FEEDBACK]"]
        output.append(f"Search Query: {search_query}\n")
        
        for platform, results in results_by_platform.items():
            platform_name = {
                'reddit': 'Reddit Community Discussions',
                'google_play': 'Google Play Store Reviews (Android)',
                'app_store': 'Apple App Store Reviews (iOS)'
            }.get(platform, platform)
            
            output.append(f"\n{'='*60}")
            output.append(f"{platform_name.upper()} ({len(results)} results)")
            output.append('='*60)
            
            if results:
                for i, r in enumerate(results, 1):
                    text = r.get('text', '')
                    rating = r.get('rating')
                    score = r.get('score')
                    category = r.get('category', 'general')
                    sentiment = r.get('sentiment', 'neutral')
                    
                    output.append(f"\n{i}. [{category}] [{sentiment}]")
                    if rating:
                        output.append(f"   Rating: {'?' * rating}/5")
                    if score is not None:
                        output.append(f"   Reddit Score: {score}")
                    output.append(f"   {text}")
            else:
                output.append(f"\n   No results found on {platform_name}")
        
        return "\n".join(output)
    
    def retrieve_platform_specific(
        self,
        carrier: str,
        platform: str,
        search_query: str,
        top_k: int = 10
    ) -> str:
        """Retrieve from specific platform only."""
        carrier_lower = carrier.lower()
        if carrier_lower not in self.vector_dbs:
            return f"Error: {carrier.upper()} index not available"
        
        platform_name = {
            'reddit': 'Reddit',
            'google_play': 'Google Play Store',
            'app_store': 'Apple App Store'
        }.get(platform, platform)
        
        db = self.vector_dbs[carrier_lower]
        results = db.search(
            query=search_query,
            top_k=top_k,
            filter_metadata={'platform': platform}
        )
        
        output = [f"[{carrier.upper()} - {platform_name.upper()}]"]
        output.append(f"Search Query: {search_query}\n")
        
        for i, r in enumerate(results, 1):
            output.append(f"{i}. {r.get('text', '')}")
        
        return "\n".join(output)
    
    def retrieve_competitive_comparison(
        self,
        search_query: str,
        top_k_per_carrier_platform: int = 5
    ) -> str:
        """
        Retrieve from ALL carriers across ALL platforms for competitive analysis.
        
        ENHANCED: Ensures comprehensive competitive data collection.
        """
        output = ["[COMPETITIVE COMPARISON - ALL CARRIERS x ALL PLATFORMS]"]
        output.append(f"Search Query: {search_query}\n")
        
        for carrier in ['tmobile', 'verizon', 'att']:
            if carrier not in self.vector_dbs:
                continue
            
            output.append(f"\n{'#'*70}")
            output.append(f"{carrier.upper()} FEEDBACK")
            output.append('#'*70)
            
            db = self.vector_dbs[carrier]
            
            for platform in ['reddit', 'google_play', 'app_store']:
                platform_name = {
                    'reddit': 'Reddit',
                    'google_play': 'Google Play Store',
                    'app_store': 'Apple App Store'
                }.get(platform, platform)
                
                try:
                    results = db.search(
                        query=search_query,
                        top_k=top_k_per_carrier_platform,
                        filter_metadata={'platform': platform}
                    )
                    
                    output.append(f"\n{'-'*60}")
                    output.append(f"{platform_name} ({len(results)} results)")
                    output.append('-'*60)
                    
                    for i, r in enumerate(results, 1):
                        text = r.get('text', '')
                        rating = r.get('rating')
                        sentiment = r.get('sentiment', 'neutral')
                        
                        output.append(f"\n{i}. [{sentiment}]")
                        if rating:
                            output.append(f"   {'?' * rating}/5")
                        output.append(f"   {text[:200]}...")
                except Exception as e:
                    output.append(f"\n   Error retrieving {platform_name}: {e}")
        
        return "\n".join(output)
    
    def query(self, user_query: str, system_prompt: Optional[str] = None) -> str:
        """
        Query the agentic RAG system. Agent MUST use tools for comprehensive analysis.
        
        ENHANCED: Enforces multi-platform retrieval.
        """
        if system_prompt is None:
            system_prompt = (
                "You are an intelligent Research Agent with access to UNIFIED carrier indexes.\n"
                "Each index contains feedback from Reddit, Google Play Store, and Apple App Store.\n\n"
                "CRITICAL RULES FOR COMPREHENSIVE ANALYSIS:\n"
                "1. ALWAYS use 'retrieve_carrier_feedback' for single-carrier analysis - it searches ALL platforms\n"
                "2. ALWAYS use 'retrieve_competitive_comparison' for multi-carrier analysis - it covers everything\n"
                "3. NEVER rely on a single platform - always gather Reddit + Play Store + App Store data\n"
                "4. When analyzing, EXPLICITLY mention findings from each platform separately\n"
                "5. Identify patterns that appear across multiple platforms vs platform-specific issues\n\n"
                "AVAILABLE TOOLS:\n"
                "- retrieve_carrier_feedback: Get ALL platform feedback for one carrier (USE THIS FIRST)\n"
                "- retrieve_platform_specific: Get specific platform data (use for platform-deep-dives)\n"
                "- retrieve_competitive_comparison: Compare ALL carriers across ALL platforms (MANDATORY for comparisons)\n\n"
                "RESPONSE FORMAT:\n"
                "After retrieval, structure your analysis as:\n"
                "1. OVERVIEW: Key findings across all platforms\n"
                "2. REDDIT INSIGHTS: What community discussions reveal\n"
                "3. PLAY STORE INSIGHTS: Android user feedback\n"
                "4. APP STORE INSIGHTS: iOS user feedback\n"
                "5. CROSS-PLATFORM PATTERNS: Issues appearing everywhere\n"
                "6. PLATFORM-SPECIFIC ISSUES: Unique to one platform\n"
                "7. RECOMMENDATIONS: Actionable items prioritized by impact\n\n"
                "MANDATE: You MUST retrieve data from ALL platforms before drawing conclusions."
            )
        
        # Define the tools mapping
        tools = {
            'retrieve_carrier_feedback': self.retrieve_carrier_feedback,
            'retrieve_platform_specific': self.retrieve_platform_specific,
            'retrieve_competitive_comparison': self.retrieve_competitive_comparison
        }
        
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
        k: int = 5
    ) -> str:
        """Directly prompt the RAG agent with minimal parameters.
        Performs retrieval across all available platforms using the prompt as the retrieval query.
        Args:
            prompt: User question / instruction.
            k: Number of results per platform to retrieve.
        Returns:
            Synthesized model answer.
        """
        retrieval_query = prompt
        platforms = list(self.vector_dbs.keys())
        context_sections = []
        for key in platforms:
            if key not in self.vector_dbs:
                continue
            try:
                db = self.vector_dbs[key]
                ctx = db.retrieve_context(retrieval_query, k, None)
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
        system_prompt = (
            "You are an assistant analyzing multi-platform user feedback (Reddit, app reviews). "
            "Use the retrieved context to answer the user's question concisely and accurately. "
            "If evidence is weak or missing, clearly state limitations."
        )
        final_user_prompt = (
            f"User Question:\n{prompt}\n\nRetrieved Context:\n{combined_context}\n\n" \
            "Provide a synthesized answer."
        )
        try:
            if hasattr(self.nemotron, 'chat'):
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": final_user_prompt}
                ]
                return self.nemotron.chat(messages)
            return self.nemotron.call_with_tools(
                system_prompt=system_prompt,
                user_prompt=final_user_prompt,
                tools={},
                tool_schemas=[]
            )
        except Exception as e:
            return f"Error generating response: {e}"

