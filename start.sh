#!/bin/bash

# Code Intelligence System Startup Script

echo "🚀 Starting Code Intelligence System..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, chromadb, networkx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing dependencies..."
    pip install -r requirements.txt
fi

# Create data directory
mkdir -p data

# Start the server
echo ""
echo "🌐 Starting web server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

cd code-intelligence
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
