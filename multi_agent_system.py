"""
Multi-Agent System implementation using sequential Nemotron calls.
Implements: Research Agent → Outline Agent → Writer Agent → Editor Agent
Supports querying from multiple Azure Cognitive Search indexes.
"""

from nemotron_client import NemotronClient
from agentic_rag import AgenticRAG
from vector_db import SocialMediaVectorDB
from typing import Dict, Optional
import os


class MultiAgentSystem:
    """
    Multi-agent system for generating comprehensive service improvement reports.
    Uses specialized agent roles with sequential execution.
    Supports multiple Azure indexes for different platforms.
    """
    
    def __init__(
        self, 
        nemotron_client: NemotronClient, 
        agentic_rag: Optional[AgenticRAG] = None,
        vector_dbs: Optional[Dict[str, SocialMediaVectorDB]] = None
    ):
        """
        Initialize the multi-agent system.
        
        Args:
            nemotron_client: Initialized Nemotron client
            agentic_rag: Optional initialized Agentic RAG system (if None, will be created from vector_dbs)
            vector_dbs: Optional dict of vector databases {'reddit': reddit_db, 'playstore': playstore_db}
                       Used only if agentic_rag is None
        """
        self.nemotron = nemotron_client
        
        if agentic_rag is not None:
            self.agentic_rag = agentic_rag
        elif vector_dbs is not None:
            self.agentic_rag = AgenticRAG(nemotron_client, vector_dbs)
        else:
            # Try to auto-initialize from environment
            self.agentic_rag = self._auto_initialize_rag()
    
    def _auto_initialize_rag(self) -> AgenticRAG:
        """Auto-initialize RAG system with both indexes if Azure credentials are available."""
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        api_key = os.getenv("AZURE_SEARCH_API_KEY")
        
        if not endpoint or not api_key:
            raise ValueError(
                "Azure Cognitive Search credentials required. "
                "Either provide agentic_rag or vector_dbs, or set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY"
            )
        
        vector_dbs = {}
        
        try:
            # Try to initialize Reddit index
            reddit_db = SocialMediaVectorDB(
                endpoint=endpoint,
                api_key=api_key,
                index_type="reddit"
            )
            vector_dbs['reddit'] = reddit_db
            print("✅ Reddit index initialized")
        except Exception as e:
            print(f"⚠️ Reddit index not available: {e}")
        
        try:
            # Try to initialize Play Store index
            playstore_db = SocialMediaVectorDB(
                endpoint=endpoint,
                api_key=api_key,
                index_type="playstore"
            )
            vector_dbs['playstore'] = playstore_db
            print("✅ Play Store index initialized")
        except Exception as e:
            print(f"⚠️ Play Store index not available: {e}")
        
        if not vector_dbs:
            raise ValueError("No vector databases could be initialized")
        
        return AgenticRAG(self.nemotron, vector_dbs)
    
    def generate_report(self, user_query: str, verbose: bool = True) -> Dict[str, str]:
        """
        Generate a comprehensive report using the multi-agent pipeline.
        
        Args:
            user_query: User's query (e.g., "Analyze complaints about network connectivity")
            verbose: Whether to print progress messages
        
        Returns:
            Dict with keys: 'research_summary', 'outline', 'draft', 'final_report'
        """
        # Step 1: Research Agent (uses Agentic RAG)
        if verbose:
            print("🔍 Research Agent: Gathering information from Azure indexes...")
        research_summary = self._research_agent(user_query)
        
        # Step 2: Outline Agent
        if verbose:
            print("📋 Outline Agent: Creating report structure...")
        outline = self._outline_agent(research_summary, user_query)
        
        # Step 3: Writer Agent
        if verbose:
            print("✍️  Writer Agent: Drafting report...")
        draft = self._writer_agent(research_summary, outline)
        
        # Step 4: Editor Agent
        if verbose:
            print("📝 Editor Agent: Reviewing and refining...")
        final_report = self._editor_agent(research_summary, outline, draft)
        
        if verbose:
            print("✅ Report generation complete!")
        
        return {
            'research_summary': research_summary,
            'outline': outline,
            'draft': draft,
            'final_report': final_report
        }
    
    def _research_agent(self, user_query: str) -> str:
        """
        Research Agent: Uses Agentic RAG to gather relevant information from Azure indexes.
        
        Args:
            user_query: User's query
        
        Returns:
            Research summary
        """
        system_prompt = (
            "You are a Research Agent with access to multiple Azure Cognitive Search indexes "
            "containing social media data (Reddit posts and Google Play Store reviews).\n\n"
            "Your goal is to gather comprehensive, relevant information using the available retrieval tools.\n\n"
            "RESEARCH STRATEGY:\n"
            "1. Determine which platforms are most relevant for the query\n"
            "2. Use retrieve_reddit_posts for general service feedback and discussions\n"
            "3. Use retrieve_playstore_reviews for app-specific issues\n"
            "4. Use retrieve_all_platforms for comprehensive analysis\n"
            "5. You may use multiple tools if needed for thorough research\n\n"
            "Your research summary should:\n"
            "1. Clearly indicate which platforms were searched\n"
            "2. Identify key themes and patterns from each source\n"
            "3. Highlight specific complaints or issues with examples\n"
            "4. Highlight and contextualize any positive feedback\n"
            "5. Include relevant statistics (e.g., frequency of issues, ratings)\n"
            "6. Be factual and only rely on retrieved information\n"
            "7. Distinguish between Reddit discussions and Play Store reviews when relevant"
        )
        
        # Use Agentic RAG to get context-aware research
        research_prompt = (
            f"User Query: {user_query}\n\n"
            "Please research this topic thoroughly using the available retrieval tools. "
            "Choose the most appropriate platforms based on the query. "
            "Gather all relevant information and create a comprehensive research summary."
        )
        
        return self.agentic_rag.query(research_prompt, system_prompt)
    
    def _outline_agent(self, research_summary: str, user_query: str) -> str:
        """
        Outline Agent: Creates a structured outline for the report.
        
        Args:
            research_summary: Output from Research Agent
            user_query: Original user query
        
        Returns:
            Detailed outline
        """
        system_prompt = (
            "You are an Outline Agent. Your job is to create a logical, "
            "well-structured outline for a service improvement report.\n\n"
            "The outline should be detailed, with clear sections and subsections. "
            "It should flow logically from problem identification to solutions.\n\n"
            "If the research includes data from multiple platforms (Reddit, Play Store), "
            "consider organizing findings by platform where appropriate."
        )
        
        user_prompt = f"""
# Original Query:
{user_query}

# Research Summary:
{research_summary}

# Task:
Based on the research summary above, create a detailed, numbered outline for a 
comprehensive service improvement report. The outline should include:

1. Executive Summary section
2. Data Sources section (mention which platforms were analyzed)
3. Problem Analysis section (with subsections for each major issue)
4. Platform-Specific Insights (if applicable - e.g., App Issues vs Service Issues)
5. Recommendations section (with specific, actionable suggestions)
6. Implementation Priority section
7. Conclusion section

Make the outline specific and detailed, with clear subsection headings.
Format it as a numbered list with proper indentation for subsections.
"""
        
        return self.nemotron.call(system_prompt, user_prompt, temperature=0.3, max_tokens=1024)
    
    def _writer_agent(self, research_summary: str, outline: str) -> str:
        """
        Writer Agent: Expands the outline into a full draft.
        
        Args:
            research_summary: Output from Research Agent
            outline: Output from Outline Agent
        
        Returns:
            Full draft report
        """
        system_prompt = (
            "You are a professional Report Writer. Your job is to expand the "
            "provided outline into a coherent, well-written draft.\n\n"
            "CRITICAL RULES:\n"
            "1. You MUST use the Research Summary as your ONLY source of facts\n"
            "2. You MUST follow the outline structure exactly\n"
            "3. Write in a professional, clear, and actionable tone\n"
            "4. Do not invent facts or information not in the research summary\n"
            "5. Make recommendations specific and implementable\n"
            "6. When citing feedback, mention the source platform (Reddit/Play Store) if relevant\n"
            "7. Use specific examples from the research summary to support your points"
        )
        
        user_prompt = f"""
# Research Summary (Your Source of Facts):
{research_summary}

# Outline to Follow:
{outline}

# Task:
Write the full report draft now. Expand each section of the outline into detailed, 
well-written content. Use the research summary for all facts and data. Follow the 
outline structure exactly. Make sure recommendations are specific and actionable.

When discussing user feedback, cite specific examples and mention which platform 
they came from (Reddit discussions or Play Store reviews) when relevant.
"""
        
        return self.nemotron.call(system_prompt, user_prompt, temperature=0.4, max_tokens=2048)
    
    def _editor_agent(self, research_summary: str, outline: str, draft: str) -> str:
        """
        Editor Agent: Reviews and refines the draft for accuracy and quality.
        
        Args:
            research_summary: Original research summary
            outline: Original outline
            draft: Draft from Writer Agent
        
        Returns:
            Final, edited report
        """
        system_prompt = (
            "You are an Editor Agent (The Critic). Your job is to review the draft "
            "for factual accuracy, structural compliance, and overall quality.\n\n"
            "Your responsibilities:\n"
            "1. Verify all facts against the research summary\n"
            "2. Ensure the draft follows the outline structure\n"
            "3. Check for clarity, coherence, and professional tone\n"
            "4. Verify that platform sources are correctly attributed\n"
            "5. Suggest improvements while maintaining accuracy\n"
            "6. Remove any information not supported by the research summary\n"
            "7. Ensure recommendations are actionable and specific\n\n"
            "Output the final, polished report."
        )
        
        user_prompt = f"""
# Research Summary (Factual Reference):
{research_summary}

# Original Outline (Structure Reference):
{outline}

# Draft to Review:
{draft}

# Task:
Review this draft carefully. Check for:
1. Factual accuracy (compare against research summary)
2. Structural compliance (does it follow the outline?)
3. Clarity and professionalism
4. Proper attribution of sources (Reddit vs Play Store)
5. Actionability of recommendations

Output the final, polished report with any necessary corrections and improvements.
Do not add new facts not in the research summary.
Ensure all platform attributions are accurate.
"""
        
        return self.nemotron.call(system_prompt, user_prompt, temperature=0.2, max_tokens=2048)

