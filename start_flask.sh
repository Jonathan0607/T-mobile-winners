#!/bin/bash
# Start Flask server script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Flask server with AI backend enabled
# Make sure you have set these environment variables in your .env file:
# - ENABLE_AI_BACKEND=1
# - NVIDIA_API_KEY=your_nvidia_api_key
# - AZURE_SEARCH_ENDPOINT=your_azure_endpoint
# - AZURE_SEARCH_API_KEY=your_azure_api_key
ENABLE_AI_BACKEND=1 python app.py

