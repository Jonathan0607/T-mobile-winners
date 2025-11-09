# ...existing code...
import os
import json
from typing import Any, Dict, Optional

from nemotron_client import NemotronClient
from vector_db import SocialMediaVectorDB
from agentic_rag import AgenticRAG
from multi_agent_system import MultiAgentSystem

# Minimal initializer that tries to wire Nemotron + Azure vector DBs
_ai = {
    "nemotron": None,
    "agentic_rag": None,
    "multi_agent": None
}

def initialize_ai():
    """Initialize Nemotron, vector DBs and AgenticRAG / MultiAgentSystem. Safe to call repeatedly."""
    if _ai["nemotron"] is not None:
        return

    # Init Nemotron (assumes NemotronClient uses env or default config)
    try:
        nemotron = NemotronClient()
        _ai["nemotron"] = nemotron
    except Exception as e:
        _ai["nemotron"] = None
        return

    # Try to initialize vector DBs (use AZURE env vars if present)
    vector_dbs = {}
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    if endpoint and api_key:
        try:
            reddit_db = SocialMediaVectorDB(endpoint=endpoint, api_key=api_key, index_type="reddit")
            vector_dbs["reddit"] = reddit_db
        except Exception:
            pass
        try:
            play_db = SocialMediaVectorDB(endpoint=endpoint, api_key=api_key, index_type="playstore")
            vector_dbs["playstore"] = play_db
        except Exception:
            pass

    # Build AgenticRAG and MultiAgentSystem
    try:
        if vector_dbs:
            agentic = AgenticRAG(nemotron, vector_dbs)
        else:
            # fallback to a Nemotron-backed RAG without vector DBs
            agentic = AgenticRAG(nemotron, {}) 
        _ai["agentic_rag"] = agentic
        _ai["multi_agent"] = MultiAgentSystem(nemotron, agentic)
    except Exception:
        _ai["agentic_rag"] = None
        _ai["multi_agent"] = None

def _call_agent_for_json(prompt: str, top_k: int = 3) -> Optional[Dict[str, Any]]:
    """
    Ask the agent to return STRICT JSON. Agent should be prompted with a JSON schema requirement.
    Returns parsed JSON or None on failure.
    """
    initialize_ai()
    agent = _ai.get("agentic_rag")
    if not agent:
        return None

    system_instruction = (
        "Return ONLY valid JSON (no markdown, no commentary). "
        "Ensure the output can be parsed by json.loads(). "
        "If data are missing, fill with null or empty lists/objects."
    )
    user_prompt = f"{system_instruction}\n\n{prompt}"
    try:
        raw = agent.direct_prompt(user_prompt, k=top_k)
        # Some agents wrap results; try to find first '{' to parse
        start = raw.find('{')
        if start >= 0:
            raw = raw[start:]
        return json.loads(raw)
    except Exception:
        return None

# Public helpers used by Flask endpoints
def ai_vibe_report() -> Optional[Dict]:
    """Ask the RAG agent for vibe report JSON matching frontend schema."""
    prompt = (
        "Produce a Vibe Report JSON object with keys: sentiment_polarity (list of {name,value,color}), "
        "sentiment_by_source (list of {source,Positive,Neutral,Negative}), top_topics (list of {topic,volume,nss}), "
        "delight_feed (list of {snippet,source,emotion})."
    )
    return _call_agent_for_json(prompt, top_k=4)

def ai_competitive_summary() -> Optional[Dict]:
    prompt = (
        "Return a JSON object with keys: historical_vibe_gap (list of {date,T_Mobile,ATT,Verizon}), "
        "feature_comparison_matrix (list of {Feature/Service,T_Mobile,ATT,Verizon}), comp_weaknesses (list), "
        "tmobile_critiques (list)."
    )
    return _call_agent_for_json(prompt, top_k=3)

def ai_triage_insights() -> Optional[Dict]:
    prompt = (
        "Return a JSON object with keys: kpis (critical_count,mttr_h,resolved_24h), queue (list of items with id,title,velocity,time_since_alert_h,status,owner_team,resolution_summary), "
        "cause_breakdown (list of {name,value,color})."
    )
    return _call_agent_for_json(prompt, top_k=3)

def ai_summary() -> Optional[Dict]:
    """General short multi-source summary + 3 recommended actions."""
    prompt = (
        "Return JSON: {summary: string, recommendations: [{title,priority,reason}] } based on retrieved platform context."
    )
    return _call_agent_for_json(prompt, top_k=5)

def ai_chi_score_estimate() -> Optional[Dict]:
    """Return a JSON like {chi_score: number, chi_trend: number, explanation: string}"""
    prompt = (
        "Based on retrieved context produce JSON {chi_score: number between 0-100, chi_trend: number, explanation: string}."
    )
    return _call_agent_for_json(prompt, top_k=4)
# ...existing code...