from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Initialization and Configuration ---
app = Flask(__name__)
# IMPORTANT: CORS is needed to allow your React frontend (on a different port) to fetch data from Flask.
CORS(app) 

# --- Mock Data Generation (Simplified Structures for Hackathon) ---

# T-Mobile Brand Colors
MAGENTA = "#E20074"
CRITICAL_RED = "#D62828"
HIGH_YELLOW = "#FFC300"

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


# --- API Endpoints ---

@app.route('/api/vibecheck/summary', methods=['GET'])
def summary():
    """Returns data for the main Home/All Teams page."""
    return jsonify(get_summary_data())

@app.route('/api/vibecheck/competitive', methods=['GET'])
def competitive():
    """Returns data for the detailed Competitive Intelligence page."""
    return jsonify(get_competitive_data())

# --- Run Server ---
if __name__ == '__main__':
    # Run on port 5001 (port 5000 is often used by AirPlay Receiver on macOS)
    # The React app will run on port 3000 (default for React)
    app.run(debug=True, port=5001)