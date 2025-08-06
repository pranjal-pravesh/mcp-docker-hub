#!/bin/bash

# MCP Hub Server Startup Script

set -e

echo "🚀 Starting MCP Hub Server..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys before running again."
    echo "   Required keys: SLACK_BOT_TOKEN, SLACK_TEAM_ID, BRAVE_API_KEY, WOLFRAM_APP_ID"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Installing dependencies globally..."
    pip install -r requirements.txt
fi

# Check if Python dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "🎯 Starting server with all available MCP servers..."
python run_hub.py --add-all-servers "$@" 