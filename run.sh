#!/bin/bash

# Crop Recommendation System - Startup Script
# This script helps you start the application easily

echo "🌾 Crop Recommendation System Startup Script"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Validate setup
echo "✅ Validating setup..."
python validate_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting the application..."
    echo "📱 Open your browser and go to: http://localhost:5001"
    echo "⏹️  Press Ctrl+C to stop the server"
    echo ""
    python app.py
else
    echo "❌ Setup validation failed. Please check the errors above."
    exit 1
fi
