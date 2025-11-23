#!/bin/bash

# F1-Score Grand Prix - Local Setup & Run Script

set -e

echo "=========================================="
echo "F1-Score Grand Prix - Setup & Run"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Found Python: $python_version"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Generate sample data
echo "Generating sample datasets..."
python3 sample_data_generation.py
echo ""

# Run backend
echo "=========================================="
echo "Starting F1-Score Grand Prix Backend"
echo "=========================================="
echo ""
echo "🏁 Server running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 backend/main.py
