#!/usr/bin/env python3
"""
Script to generate all AI JSON files from multi-agent research.
This will create JSON files that can replace mock data in the Flask API.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set AI backend enabled
os.environ["ENABLE_AI_BACKEND"] = "1"

from ai_backend import (
    initialize_ai,
    generate_vibe_report_json,
    generate_competitive_json,
    generate_triage_json,
    generate_summary_json,
    calculate_chi_from_research
)

def main():
    print("=" * 80)
    print("AI Data Generation Script")
    print("=" * 80)
    print()
    
    # Initialize AI system
    print("🔧 Initializing AI system...")
    if not initialize_ai():
        print("❌ Failed to initialize AI system. Please check your Azure credentials and Nemotron configuration.")
        sys.exit(1)
    
    print("✅ AI system initialized")
    print()
    
    # Generate all JSON files
    print("📊 Generating JSON files from multi-agent research...")
    print()
    
    # 1. Generate Summary JSON (with CHI calculation)
    print("1️⃣ Generating summary data with CHI calculation...")
    summary_data = generate_summary_json("ai_generated_summary.json")
    if summary_data:
        print(f"   ✅ Summary data generated")
        print(f"   📈 CHI Score: {summary_data.get('chi_score', 'N/A')}")
        print(f"   📉 Trend: {summary_data.get('chi_trend', 'N/A')} ({summary_data.get('trend_direction', 'N/A')})")
    else:
        print("   ⚠️ Failed to generate summary data")
    print()
    
    # 2. Generate Vibe Report JSON
    print("2️⃣ Generating vibe report data...")
    vibe_data = generate_vibe_report_json("ai_generated_vibe_report.json")
    if vibe_data:
        print(f"   ✅ Vibe report data generated")
        if "sentiment_polarity" in vibe_data:
            sentiment_str = ", ".join([f"{s['name']}: {s['value']}%" for s in vibe_data['sentiment_polarity']])
            print(f"   💭 Sentiment: {sentiment_str}")
    else:
        print("   ⚠️ Failed to generate vibe report data")
    print()
    
    # 3. Generate Competitive JSON
    print("3️⃣ Generating competitive analysis data...")
    competitive_data = generate_competitive_json("ai_generated_competitive.json")
    if competitive_data:
        print(f"   ✅ Competitive data generated")
    else:
        print("   ⚠️ Failed to generate competitive data")
    print()
    
    # 4. Generate Triage JSON
    print("4️⃣ Generating triage queue data...")
    triage_data = generate_triage_json("ai_generated_triage.json")
    if triage_data:
        print(f"   ✅ Triage data generated")
        if "kpis" in triage_data:
            print(f"   🎯 Critical Issues: {triage_data['kpis'].get('critical_count', 'N/A')}")
            print(f"   ⏱️ MTTR: {triage_data['kpis'].get('mttr_h', 'N/A')} hours")
    else:
        print("   ⚠️ Failed to generate triage data")
    print()
    
    print("=" * 80)
    print("✅ Data generation complete!")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  - ai_generated_summary.json")
    print("  - ai_generated_vibe_report.json")
    print("  - ai_generated_competitive.json")
    print("  - ai_generated_triage.json")
    print()
    print("These files will be used by the Flask API when AI backend is enabled.")
    print("The Flask endpoints will load from these files if they exist.")

if __name__ == "__main__":
    main()

