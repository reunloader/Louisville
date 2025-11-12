#!/bin/bash

# Derby City Watch Chatbot - Quick Start Script

echo "======================================"
echo "Derby City Watch Chatbot"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API key!"
    echo "   1. Open .env in a text editor"
    echo "   2. Choose AI_PROVIDER (gemini or openai)"
    echo "   3. Add your API key"
    echo ""
    read -p "Press Enter after you've configured .env..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if _posts directory exists
if [ ! -d "../_posts" ]; then
    echo "⚠️  Warning: _posts directory not found at ../_posts"
    echo "Make sure POSTS_DIRECTORY in .env is correct"
fi

echo "======================================"
echo "Starting Derby City Watch Chatbot..."
echo "======================================"
echo ""

# Run the application
python app.py
