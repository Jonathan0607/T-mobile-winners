#!/bin/bash
# Start Flask server script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Flask server
python app.py

