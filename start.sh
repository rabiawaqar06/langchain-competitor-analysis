#!/bin/bash

# Competitive Analysis Agent Startup Script
# This script helps you set up and run the application easily

echo "🚀 Competitive Analysis Agent Startup Script"
echo "============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 is installed"

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Please run this script from the competitive-analysis-agent directory"
    exit 1
fi

echo "✅ Correct directory detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
cd backend
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create reports directory
if [ ! -d "reports" ]; then
    mkdir reports
    echo "✅ Reports directory created"
fi

echo ""
echo "🎉 Setup complete! Starting the application..."
echo ""
echo "📍 The application will be available at: http://localhost:8000"
echo "🔑 You'll need a Google Gemini API key to use the application"
echo "🌐 Get your API key here: https://makersuite.google.com/app/apikey"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python main.py
