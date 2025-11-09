"""
Multi-Agent System implementation using sequential Nemotron calls.
Implements: Research Agent -> Outline Agent -> Writer Agent -> Editor Agent
Supports querying from multiple unified carrier indexes (each containing Reddit, Play Store, App Store).
"""

from nemotron_client import NemotronClient
from agentic_rag import AgenticRAG
from vector_db import SocialMediaVectorDB, CARRIER_INDEX_NAMES
from typing import Dict, Optional
import os


class MultiAgentSystem:
    """
    Multi-agent system for generating comprehensive service improvement reports.
    Uses specialized agent roles with sequential execution.
    Supports multiple unified carrier indexes (T-Mobile, Verizon, AT&T).
    Each carrier index contains data from Reddit, Google Play Store, and Apple App Store.
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
            vector_dbs: Optional dict of vector databases {'tmobile': tmobile_db, 'verizon': verizon_db, 'att': att_db}
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
        """
        Auto-initialize RAG system with unified carrier indexes if Azure credentials are available.
        Each carrier index contains data from Reddit, Play Store, and App Store.
        """
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        api_key = os.getenv("AZURE_SEARCH_API_KEY")
       
        if not endpoint or not api_key:
            raise ValueError(
                "Azure Cognitive Search credentials required. "
                "Either provide agentic_rag or vector_dbs, or set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY"
            )
       
        vector_dbs = {}
       
        # Try to initialize each carrier's unified index
        for carrier in ['tmobile', 'verizon', 'att']:
            try:
                db = SocialMediaVectorDB(
                    endpoint=endpoint,
                    api_key=api_key,
                    carrier=carrier
                )
                doc_count = db.search_client.get_document_count()
                vector_dbs[carrier] = db
                print(f"✅ {carrier.upper()} unified index initialized ({doc_count} documents)")
            except Exception as e:
                print(f"⚠️ {carrier.upper()} index not available: {e}")
       
        if not vector_dbs:
            raise ValueError("No carrier indexes could be initialized")
       
        print(f"\n📊 Total carriers initialized: {len(vector_dbs)}")
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
        Research Agent: Uses Agentic RAG to gather relevant information from ALL platforms.
       
        ENHANCED: Ensures comprehensive multi-platform data collection.
       
        Args:
            user_query: User's query
       
        Returns:
            Research summary with data from ALL platforms
        """
        system_prompt = (
            "You are a Research Agent with access to UNIFIED carrier indexes containing data from:\n"
            "- Reddit community discussions (r/tmobile, r/verizon, r/ATT)\n"
            "- Google Play Store reviews (Android app feedback)\n"
            "- Apple App Store reviews (iOS app feedback)\n\n"
            "MANDATORY RESEARCH PROTOCOL:\n"
            "1. You MUST use retrieval tools to gather data from ALL platforms\n"
            "2. For single-carrier analysis: Use 'retrieve_carrier_feedback' (gets all platforms)\n"
            "3. For competitive analysis: Use 'retrieve_competitive_comparison' (gets all carriers × all platforms)\n"
            "4. You may use 'retrieve_platform_specific' for deep-dives, but ONLY after getting comprehensive data\n\n"
            "YOUR RESEARCH SUMMARY MUST INCLUDE:\n"
            "1. DATA SOURCES SECTION:\n"
            "   - Explicitly list which platforms were searched\n"
            "   - Note the volume of data from each platform\n"
            "   - Mention any platforms with limited/no data\n\n"
            "2. PLATFORM-BY-PLATFORM ANALYSIS:\n"
            "   - Reddit Findings: Community sentiment, recurring discussions, pain points\n"
            "   - Play Store Findings: Android-specific issues, app ratings, common complaints\n"
            "   - App Store Findings: iOS-specific issues, app ratings, user feedback\n\n"
            "3. CROSS-PLATFORM PATTERNS:\n"
            "   - Issues mentioned on Reddit AND in app reviews\n"
            "   - Problems affecting both Android and iOS users\n"
            "   - Universal complaints vs platform-specific issues\n\n"
            "4. STATISTICAL BREAKDOWN:\n"
            "   - Sentiment distribution per platform\n"
            "   - Category frequency per platform\n"
            "   - Rating averages (for app stores)\n"
            "   - Engagement metrics (Reddit scores, review counts)\n\n"
            "5. KEY THEMES WITH PLATFORM ATTRIBUTION:\n"
            "   - For EACH major theme, specify which platforms it appears on\n"
            "   - Example: 'Network connectivity issues (Reddit: 45 mentions, Play Store: 32 1-star reviews, App Store: 28 1-star reviews)'\n\n"
            "6. NOTABLE EXAMPLES FROM EACH PLATFORM:\n"
            "   - Quote specific Reddit posts\n"
            "   - Quote specific Play Store reviews\n"
            "   - Quote specific App Store reviews\n\n"
            "CRITICAL: Your summary will be used by other agents. It must be:\n"
            "- Comprehensive (covering ALL platforms)\n"
            "- Structured (organized by platform)\n"
            "- Factual (based only on retrieved data)\n"
            "- Detailed (with specific examples and statistics)\n\n"
            "DO NOT proceed without retrieving data from all available platforms."
        )
       
        # Enhanced research prompt that explicitly requests multi-platform data
        research_prompt = (
            f"RESEARCH REQUEST: {user_query}\n\n"
            "MANDATORY INSTRUCTIONS:\n"
            "1. Retrieve feedback from ALL platforms (Reddit + Play Store + App Store)\n"
            "2. If analyzing multiple carriers, retrieve from ALL carriers\n"
            "3. Gather at least 10 results per platform for statistical significance\n"
            "4. Create a comprehensive research summary following the required structure\n\n"
            "Your research MUST cover:\n"
            "- Reddit community discussions and sentiment\n"
            "- Google Play Store Android user feedback and ratings\n"
            "- Apple App Store iOS user feedback and ratings\n\n"
            "Begin your research now. Use the retrieval tools to gather comprehensive multi-platform data."
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
    
    def research_query(self, user_query: str, verbose: bool = False) -> str:
            """
            Public method to execute research query using the research agent.
            Returns research summary text that can be used for data extraction.
            
            Args:
                user_query: User's query (e.g., "Analyze customer sentiment")
                verbose: Whether to print progress messages
            
            Returns:
                Research summary as string
            """
            if verbose:
                print("🔍 Research Agent: Gathering information from Azure indexes...")
            return self._research_agent(user_query)
        
