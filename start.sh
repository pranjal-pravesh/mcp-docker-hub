#!/bin/bash
set -e

echo "🚀 Starting MCP Hub Server..."
echo "📋 Environment variables:"
env | grep -E "(SLACK|BRAVE|WOLFRAM|GITHUB|POSTGRES|REDIS|OPENWEATHER|NEWS)" || echo "No MCP environment variables found"

# Start the hub server
exec python scripts/run_hub.py --host 0.0.0.0 --port $PORT 