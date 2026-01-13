#!/bin/bash

echo "=========================================="
echo "🚀 Starting Thought Leadership Web UI"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your API keys."
    echo "See env.example for reference."
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting web server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Start the Flask app
python app.py

