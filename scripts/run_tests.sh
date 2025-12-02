#!/bin/bash
# Run tests for Stock Recommendation System

set -e

echo "=== Running Tests ==="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with coverage
echo "Running pytest with coverage..."
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "=== Test Summary ==="
echo "Coverage report generated in htmlcov/index.html"
echo ""
