#!/bin/bash
# Setup script for Stock Recommendation System

set -e

echo "=== Stock Recommendation System Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data models logs

# Copy environment file
echo "Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please update with your API keys."
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo "3. Run 'streamlit run src/ui/app.py' to start the UI"
echo "4. Or run 'uvicorn src.api.main:app --reload' to start the API"
echo ""
