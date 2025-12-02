#!/bin/bash
# Build Docker images for Stock Recommendation System

set -e

echo "=== Building Docker Images ==="
echo ""

# Build main Streamlit image
echo "Building Streamlit image..."
docker build -t stock-recommendation-ui:latest -f Dockerfile .

# Build API image
echo "Building API image..."
docker build -t stock-recommendation-api:latest -f docker/Dockerfile.api .

echo ""
echo "=== Docker Images Built Successfully ==="
echo ""
echo "To run the services:"
echo "docker-compose up -d"
echo ""
