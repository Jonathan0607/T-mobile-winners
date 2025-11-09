from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

# Import AI backend functions
try:
    from ai_backend import (
        initialize_ai,
        get_ai_vibe_report_data,
        get_ai_competitive_data,
        get_ai_triage_data,
        get_ai_summary_data
    )
    AI_BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI backend not available: {e}")
    AI_BACKEND_AVAILABLE = False

# --- Initialization and Configuration ---
app = Flask(__name__)
# IMPORTANT: CORS is needed to allow your React frontend (on a different port) to fetch data from Flask.
CORS(app) 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Mock Data Generation (Simplified Structures for Hackathon) ---

# T-Mobile Brand Colors
MAGENTA = "#E20074"
CRITICAL_RED = "#D62828"
HIGH_YELLOW = "#FFC300"

# Decide whether to enable AI endpoints (env var)
AI_ENABLED = os.getenv("ENABLE_AI_BACKEND", "0") == "1"
if AI_ENABLED and AI_BACKEND_AVAILABLE:
    if initialize_ai():
        logger.info("✅ AI backend initialized successfully")
    else:
        logger.warning("⚠️ AI backend initialization failed, will use mock data")
        AI_ENABLED = False
else:
    logger.info("ℹ️ AI backend disabled or not available, using mock data")

@app.route('/api/vibecheck/vibe_report', methods=['GET'])
def vibe_report():
    """Returns data for the Vibe Report: Internal Analysis page."""
    if AI_ENABLED and AI_BACKEND_AVAILABLE:
        try:
            ai_result = get_ai_vibe_report_data()
            if ai_result:
                logger.info("✅ Using AI-generated vibe report data")
                return jsonify(ai_result)
            else:
                logger.warning("⚠️ AI vibe report returned None, using mock data")
        except Exception as e:
            logger.error(f"❌ Error getting AI vibe report: {e}")
            # Fall through to mock data
    return jsonify(get_vibe_report_data())

@app.route('/api/vibecheck/competitive', methods=['GET'])
def competitive():
    """Returns data for the detailed Competitive Intelligence page."""
    if AI_ENABLED and AI_BACKEND_AVAILABLE:
        try:
            ai_result = get_ai_competitive_data()
            if ai_result:
                logger.info("✅ Using AI-generated competitive data")
                return jsonify(ai_result)
            else:
                logger.warning("⚠️ AI competitive data returned None, using mock data")
        except Exception as e:
            logger.error(f"❌ Error getting AI competitive data: {e}")
            # Fall through to mock data
    return jsonify(get_competitive_data())

@app.route('/api/vibecheck/triage_queue', methods=['GET'])
def triage_queue():
    """Returns data for the Actionable Insights page."""
    if AI_ENABLED and AI_BACKEND_AVAILABLE:
        try:
            ai_result = get_ai_triage_data()
            if ai_result:
                logger.info("✅ Using AI-generated triage data")
                # Ensure all queue items have urgency and time_to_fix fields
                if "queue" in ai_result:
                    for item in ai_result["queue"]:
                        if "urgency" not in item:
                            # Calculate urgency from velocity if not present
                            velocity = item.get("velocity", 0)
                            if velocity >= 8.0:
                                item["urgency"] = "Critical"
                            elif velocity >= 6.0:
                                item["urgency"] = "High"
                            elif velocity >= 4.0:
                                item["urgency"] = "Medium"
                            else:
                                item["urgency"] = "Low"
                        if "time_to_fix" not in item:
                            # Use time_since_alert_h as fallback
                            item["time_to_fix"] = item.get("time_since_alert_h", 0)
                return jsonify(ai_result)
            else:
                logger.warning("⚠️ AI triage data returned None, using mock data")
        except Exception as e:
            logger.error(f"❌ Error getting AI triage data: {e}")
            # Fall through to mock data
    return jsonify(get_triage_queue_data())

@app.route('/api/vibecheck/summary', methods=['GET'])
def summary():
    """Returns data for the main Home/All Teams page."""
    if AI_ENABLED and AI_BACKEND_AVAILABLE:
        try:
            ai_result = get_ai_summary_data()
            if ai_result:
                logger.info("✅ Using AI-generated summary data")
                # Merge with mock data to ensure all required fields are present
                base = get_summary_data()
                # Update with AI data where available
                if "chi_score" in ai_result:
                    base["chi_score"] = ai_result.get("chi_score", base["chi_score"])
                if "chi_trend" in ai_result:
                    base["chi_trend"] = ai_result.get("chi_trend", base["chi_trend"])
                if "trend_direction" in ai_result:
                    base["trend_direction"] = ai_result.get("trend_direction", base["trend_direction"])
                if "trend_period" in ai_result:
                    base["trend_period"] = ai_result.get("trend_period", "Last Hour")
                if "action_cards" in ai_result and ai_result["action_cards"]:
                    base["action_cards"] = ai_result["action_cards"]
                if "competitive_summary" in ai_result and ai_result["competitive_summary"]:
                    base["competitive_summary"] = ai_result["competitive_summary"]
                return jsonify(base)
            else:
                logger.warning("⚠️ AI summary data returned None, using mock data")
        except Exception as e:
            logger.error(f"❌ Error getting AI summary data: {e}")
            # Fall through to mock data
    return jsonify(get_summary_data())
# ...existing code...

# Helper to generate mock trend data
def generate_trend_data():
    time_points = [datetime.now() - timedelta(hours=24 - i) for i in range(25)]
    scores = np.clip(
        88 + 3 * np.sin(np.linspace(0, 2 * np.pi, 25)) - np.arange(25) * 0.1,
        75, 95
    )
    # Convert to format Recharts prefers
    return [{"time": t.strftime("%H:%M"), "score": round(s, 2)} for t, s in zip(time_points, scores)]

# Home Page / Summary Data
def get_summary_data():
    return {
        "chi_score": 85.2,
        "chi_trend": -1.5,
        "trend_direction": "down",
        "trend_period": "Last Hour",
        "trend_data": generate_trend_data(),
        "action_cards": [
            {
                "id": "A101",
                "team": "Network Engineering",
                "priority": "Critical",
                "title": "Investigate 5G outage in Miami",
                "insight": "40% spike in 'slow data' complaints in zip 33139 over 1hr.",
                "color": CRITICAL_RED
            },
            {
                "id": "A102",
                "team": "Social Media Support",
                "priority": "High",
                "title": "Draft response to #SlowMagenta trend",
                "insight": "Sentiment velocity shows high risk of negative virality in 2 hours.",
                "color": HIGH_YELLOW
            }
        ],
        # Only simple comparison on home page
        "competitive_summary": [
            {"carrier": "T-Mobile", "score": 85.2, "color": MAGENTA},
            {"carrier": "AT&T", "score": 87.7, "color": HIGH_YELLOW},
            {"carrier": "Verizon", "score": 81.2, "color": "#CCCCCC"},
        ]
    }

# Competitive Intelligence Page Data (Detailed)
def get_competitive_data():
    return {
        "historical_vibe_gap": [
            {"date": "Day 1", "T_Mobile": 85, "ATT": 87, "Verizon": 82},
            {"date": "Day 2", "T_Mobile": 84, "ATT": 86, "Verizon": 81},
            {"date": "Day 3", "T_Mobile": 86, "ATT": 87, "Verizon": 80},
            {"date": "Day 4", "T_Mobile": 85, "ATT": 87.5, "Verizon": 81.5},
            {"date": "Day 5", "T_Mobile": 85.2, "ATT": 87.7, "Verizon": 81.2},
        ],
        "feature_comparison_matrix": [
            {'Feature/Service': '5G Speed', 'T_Mobile': 'Positive (8.5/10)', 'ATT': 'Positive (8.0/10)', 'Verizon': 'Positive (8.8/10)'},
            {'Feature/Service': 'Customer Service', 'T_Mobile': 'Mixed (6.8/10)', 'ATT': 'Negative (4.2/10)', 'Verizon': 'Mixed (6.0/10)'},
            {'Feature/Service': 'Rural Coverage', 'T_Mobile': 'Neutral (5.5/10)', 'ATT': 'Positive (7.9/10)', 'Verizon': 'Strong Positive (9.2/10)'},
            {'Feature/Service': 'Pricing/Plans', 'T_Mobile': 'Positive (8.9/10)', 'ATT': 'Mixed (6.5/10)', 'Verizon': 'Negative (4.0/10)'},
        ],
        "comp_weaknesses": [
            {"competitor": "AT&T", "weakness": "Billing complexity is a recurring customer complaint.", "action_suggestion": "Review simplicity of T-Mobile billing statements."},
            {"competitor": "Verizon", "weakness": "High prices and hidden fees are driving dissatisfaction.", "action_suggestion": "Highlight T-Mobile's transparent 'no-fee' promise in marketing."},
        ],
        "tmobile_critiques": [
            {"critique": "Occasional 5G performance dips in urban centers (e.g., NYC).", "source_impact": "High (Twitter, App Reviews)", "team_suggestion": "Network Engineering: Investigate micro-cell saturation in specific zones."},
            {"critique": "Confusion around 'premium data' caps on certain plans.", "source_impact": "Medium (Support calls)", "team_suggestion": "Product/Marketing: Clarify plan details on website and during sales."},
        ]
    }

# Vibe Report / Internal Analysis Data
def get_vibe_report_data():
    return {
        "sentiment_polarity": [
            {"name": "Positive", "value": 45, "color": MAGENTA},
            {"name": "Neutral", "value": 35, "color": "#9CA3AF"},
            {"name": "Negative", "value": 20, "color": "#D62828"},
        ],
        "sentiment_by_source": [
            {"source": "Reddit", "Positive": 120, "Neutral": 80, "Negative": 50},
            {"source": "Google Play", "Positive": 450, "Neutral": 200, "Negative": 150},
            {"source": "Apple App Store", "Positive": 380, "Neutral": 180, "Negative": 120},
        ],
        "top_topics": [
            {"topic": "5G Network Speed", "volume": 1250, "nss": 62},
            {"topic": "Customer Service Response Time", "volume": 890, "nss": -35},
            {"topic": "Billing Transparency", "volume": 720, "nss": 55},
            {"topic": "Data Plan Pricing", "volume": 680, "nss": 48},
            {"topic": "Coverage in Rural Areas", "volume": 550, "nss": -28},
            {"topic": "App Usability", "volume": 420, "nss": 38},
            {"topic": "International Roaming", "volume": 380, "nss": -15},
            {"topic": "Device Trade-In Program", "volume": 320, "nss": 42},
        ],
        "delight_feed": [
            {"snippet": "Love the 5G speeds in my area! Fastest I've ever experienced.", "source": "Reddit", "emotion": "Joy"},
            {"snippet": "Customer service actually solved my issue on the first call. Amazing!", "source": "Google Play", "emotion": "Satisfaction"},
            {"snippet": "No hidden fees - exactly what they promised. Refreshing change!", "source": "Apple App Store", "emotion": "Trust"},
            {"snippet": "The app makes managing my account so easy. Great UX!", "source": "Reddit", "emotion": "Delight"},
            {"snippet": "Trade-in program got me a great deal on my new phone.", "source": "Google Play", "emotion": "Gratitude"},
            {"snippet": "Coverage has been amazing even in remote areas. Really impressed!", "source": "Apple App Store", "emotion": "Surprise"},
        ]
    }


# Actionable Insights / Triage Queue Data
def get_triage_queue_data():
    # Helper function to determine urgency based on velocity and status
    def get_urgency(velocity, status):
        if status == "Resolved":
            return "Low"
        if velocity >= 8.0:
            return "Critical"
        elif velocity >= 6.0:
            return "High"
        elif velocity >= 4.0:
            return "Medium"
        else:
            return "Low"
    
    # Helper function to calculate time to fix (estimated based on velocity and time since alert)
    def get_time_to_fix(velocity, time_since_alert_h, status):
        if status == "Resolved":
            return time_since_alert_h  # Use actual resolution time
        # Estimate based on velocity: higher velocity = more urgent = faster fix needed
        # Base estimate: 24 hours, reduced by velocity factor
        base_time = 24.0
        velocity_factor = max(0.3, 1.0 - (velocity / 10.0))
        estimated_time = base_time * velocity_factor
        # Add time since alert to get total estimated time
        return time_since_alert_h + estimated_time
    
    queue_items = [
        {
            "id": "T001",
            "title": "5G Network Outage - Miami Metro Area",
            "velocity": 9.2,
            "time_since_alert_h": 2.3,
            "status": "New",
            "owner_team": "Network Engineering",
            "resolution_summary": None
        },
        {
            "id": "T002",
            "title": "Customer Service Response Time Spike",
            "velocity": 7.8,
            "time_since_alert_h": 5.1,
            "status": "In Progress",
            "owner_team": "Customer Support",
            "resolution_summary": None
        },
        {
            "id": "T003",
            "title": "Billing System Integration Error",
            "velocity": 6.5,
            "time_since_alert_h": 1.2,
            "status": "New",
            "owner_team": "IT Operations",
            "resolution_summary": None
        },
        {
            "id": "T004",
            "title": "App Store Review Score Decline",
            "velocity": 8.9,
            "time_since_alert_h": 3.7,
            "status": "In Progress",
            "owner_team": "Product Team",
            "resolution_summary": None
        },
        {
            "id": "T005",
            "title": "Data Plan Confusion - Customer Complaints",
            "velocity": 5.2,
            "time_since_alert_h": 0.8,
            "status": "Resolved",
            "owner_team": "Marketing",
            "resolution_summary": "Clarified plan details on website and updated customer-facing documentation."
        },
        {
            "id": "T006",
            "title": "Rural Coverage Gap - Montana Region",
            "velocity": 4.8,
            "time_since_alert_h": 6.2,
            "status": "In Progress",
            "owner_team": "Network Engineering",
            "resolution_summary": None
        },
        {
            "id": "T007",
            "title": "International Roaming Charges Issue",
            "velocity": 7.1,
            "time_since_alert_h": 2.9,
            "status": "Resolved",
            "owner_team": "Billing",
            "resolution_summary": "Fixed calculation error in roaming charge algorithm. Refunds processed for affected customers."
        },
        {
            "id": "T008",
            "title": "Device Trade-In Program Delay",
            "velocity": 5.9,
            "time_since_alert_h": 4.5,
            "status": "Resolved",
            "owner_team": "Operations",
            "resolution_summary": "Streamlined trade-in process and added additional processing capacity."
        }
    ]
    
    # Add urgency and time_to_fix to each item
    for item in queue_items:
        item["urgency"] = get_urgency(item["velocity"], item["status"])
        item["time_to_fix"] = get_time_to_fix(item["velocity"], item["time_since_alert_h"], item["status"])
    
    return {
        "kpis": {
            "critical_count": 12,
            "mttr_h": 3.5,
            "resolved_24h": 28
        },
        "queue": queue_items,
        "cause_breakdown": [
            {"name": "Network Infrastructure", "value": 35, "color": CRITICAL_RED},
            {"name": "Customer Service", "value": 25, "color": "#FFC300"},
            {"name": "Billing System", "value": 20, "color": "#9CA3AF"},
            {"name": "Product/App Issues", "value": 15, "color": "#3B82F6"},
            {"name": "Other", "value": 5, "color": "#6B7280"}
        ]
    }

@app.route('/api/vibecheck/chat', methods=['POST'])
def chat():
    """Handles chat requests from the AI Co-Pilot interface."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Simulated AI response (in production, this would call Nemotron AI)
        # For now, return a helpful mock response based on the query
        response_text = generate_ai_response(query)
        
        return jsonify({'response': response_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_ai_response(query: str) -> str:
    """Generate a mock AI response based on the user's query."""
    query_lower = query.lower()
    
    # Pattern matching for common questions
    if 'critical' in query_lower or 'issue' in query_lower:
        return "Based on the current triage queue, there are 12 critical issues requiring immediate attention. The top priority is the 5G Network Outage in Miami Metro Area with a velocity of 9.2. I recommend escalating this to Network Engineering immediately."
    
    elif 'mttr' in query_lower or 'mean time' in query_lower:
        return "The Mean Time To Resolution (MTTR) for the last 7 days is 3.5 hours. This is within our target range. However, we've resolved 28 issues in the last 24 hours, indicating high activity levels."
    
    elif 'sentiment' in query_lower or 'vibe' in query_lower:
        return "The current CHI Score is 85.2, showing a slight downward trend of -1.5. Sentiment analysis reveals 45% positive, 35% neutral, and 20% negative mentions. The main pain points are Customer Service Response Time (NSS: -35) and Coverage in Rural Areas (NSS: -28)."
    
    elif 'competitive' in query_lower or 'competitor' in query_lower:
        return "T-Mobile currently has a vibe score of 85.2, compared to AT&T (87.7) and Verizon (81.2). Our main competitive advantages are in Pricing/Plans and 5G Speed. Verizon's weakness is expensive plans, which we can leverage in marketing."
    
    elif 'network' in query_lower or 'coverage' in query_lower:
        return "Network Infrastructure issues account for 35% of all root causes. The most critical issue is a 5G Network Outage in Miami Metro Area. I recommend prioritizing network stability improvements and expanding coverage in rural areas."
    
    elif 'billing' in query_lower or 'charge' in query_lower:
        return "Billing System issues represent 20% of root causes. Recent resolutions include fixing international roaming charge calculations. The system is currently stable, but ongoing monitoring is recommended."
    
    elif 'help' in query_lower or 'what' in query_lower:
        return "I can help you with:\n\n• Critical issues and triage queue status\n• MTTR and resolution metrics\n• Sentiment analysis and CHI scores\n• Competitive intelligence\n• Network and infrastructure insights\n• Billing and customer service data\n\nWhat would you like to know more about?"
    
    else:
        return f"I understand you're asking about: '{query}'. Based on the current dashboard data, I can provide insights on critical issues, sentiment analysis, competitive intelligence, and operational metrics. Could you be more specific about what you'd like to know?"

# --- Run Server ---
if __name__ == '__main__':
    # Run on port 5001 (port 5000 is often used by AirPlay Receiver on macOS)
    # The React app will run on port 3000 (default for React)
    app.run(debug=True, port=5001)