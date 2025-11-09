# AI Data Generation System

## Overview

This system generates JSON files from multi-agent research that can replace mock data in the Flask API. The system includes a comprehensive CHI (Customer Happiness Index) calculation function that derives scores from research data.

## Key Features

### 1. CHI Calculation Function

The `calculate_chi_from_research()` function calculates the Customer Happiness Index based on:

- **Sentiment Distribution**: Positive, Neutral, Negative percentages
- **Net Sentiment Score (NSS)**: Average NSS from topics (range: -100 to 100)
- **Sentiment Balance**: Difference between positive and negative sentiment
- **Trend Analysis**: Calculates trend direction based on sentiment delta

**Formula:**
- Base CHI = 50 + (sentiment_score × 50) where sentiment_score = (positive% × 1.0 + neutral% × 0.0 + negative% × -1.0) / 100
- Final CHI = Base CHI + (NSS / 100.0) × 20 (clamped between 0-100)
- Trend: Positive if positive% - negative% > 10, Negative if < -10, else Stable

### 2. JSON Generation Functions

#### `generate_summary_json()`
- Generates summary data with CHI calculation
- Includes action cards, competitive summary, and trend data
- Output: `ai_generated_summary.json`

#### `generate_vibe_report_json()`
- Generates sentiment analysis, topics, and delight feed
- Includes sentiment by source (Reddit, Google Play, Apple App Store)
- Output: `ai_generated_vibe_report.json`

#### `generate_competitive_json()`
- Generates competitive analysis data
- Includes historical vibe gap, feature comparison, competitor weaknesses
- Output: `ai_generated_competitive.json`

#### `generate_triage_json()`
- Generates triage queue data
- Includes KPIs, queue items with urgency and time_to_fix, root cause breakdown
- Output: `ai_generated_triage.json`

### 3. Caching System

All functions check for existing JSON files first:
- If file exists, loads from cache (faster)
- If file doesn't exist, generates new data from research
- Saves generated data to file for future use

## Usage

### Generate All JSON Files

Run the generation script:

```bash
python generate_ai_data.py
```

This will:
1. Initialize the AI system
2. Generate all JSON files from multi-agent research
3. Calculate CHI scores from research data
4. Save files to the project root

### Generate Individual Files

You can also generate files individually:

```python
from ai_backend import (
    generate_summary_json,
    generate_vibe_report_json,
    generate_competitive_json,
    generate_triage_json
)

# Generate summary with CHI calculation
summary = generate_summary_json()

# Generate vibe report
vibe = generate_vibe_report_json()

# Generate competitive data
competitive = generate_competitive_json()

# Generate triage data
triage = generate_triage_json()
```

### Use in Flask API

The Flask endpoints automatically use generated JSON files when available:

```python
# In app.py, endpoints check for AI-generated data first
if AI_ENABLED and AI_BACKEND_AVAILABLE:
    ai_result = get_ai_summary_data()  # Loads from ai_generated_summary.json
    if ai_result:
        return jsonify(ai_result)
# Falls back to mock data if AI data not available
```

## File Structure

```
ai_generated_summary.json       # Summary data with CHI score
ai_generated_vibe_report.json   # Sentiment and topics data
ai_generated_competitive.json   # Competitive analysis data
ai_generated_triage.json        # Triage queue data
```

## CHI Calculation Details

The CHI calculation uses the following inputs:

1. **Sentiment Percentages**: Extracted from research summary
   - Positive: Percentage of positive feedback
   - Neutral: Percentage of neutral feedback
   - Negative: Percentage of negative feedback

2. **Net Sentiment Score (NSS)**: Average NSS from all topics
   - Range: -100 to 100
   - Positive NSS boosts CHI
   - Negative NSS reduces CHI

3. **Trend Calculation**:
   - Positive trend: positive% - negative% > 10
   - Negative trend: positive% - negative% < -10
   - Stable: otherwise

4. **Output**:
   - `chi_score`: 0-100 scale
   - `chi_trend`: Change in score (positive or negative number)
   - `trend_direction`: "up", "down", or "stable"
   - `trend_period`: Time period for trend (e.g., "Last Hour")

## Integration with Multi-Agent System

The system uses the multi-agent system's `research_query()` method to:

1. Query Azure Cognitive Search indexes (Reddit, Play Store)
2. Gather comprehensive research summaries
3. Extract structured data using Nemotron AI
4. Calculate metrics like CHI from the research

## Error Handling

- All functions return `None` on failure
- Flask endpoints fall back to mock data if AI generation fails
- Logging provides detailed error information
- Cached files are used when available to avoid regeneration

## Requirements

- AI backend enabled (`ENABLE_AI_BACKEND=1`)
- Azure credentials configured (`.env` file)
- Nemotron API key configured
- Azure Cognitive Search indexes available

## Notes

- JSON files are generated on-demand
- Files are cached for performance
- Regenerate files when you want fresh data
- CHI calculation is based on real research data, not mock data

