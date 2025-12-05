#!/bin/bash

# HeritageLens AI Launch Script
# This script sets up and runs the HeritageLens AI Streamlit application

echo "🏛️ HeritageLens AI - Starting Application..."
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Check if model file exists
if [ ! -f "best.pt" ]; then
    echo "❌ Model file 'best.pt' not found in current directory."
    echo "Please ensure the YOLOv11 model weights are present."
    exit 1
fi

# Install requirements if needed
echo "📦 Checking and installing dependencies..."
pip install -r requirements.txt

# Check if streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "❌ Streamlit is not installed. Installing..."
    pip install streamlit
fi

# Check if ultralytics is installed
if ! python3 -c "import ultralytics" &> /dev/null; then
    echo "❌ Ultralytics is not installed. Installing..."
    pip install ultralytics
fi

echo "✅ Dependencies checked successfully!"
echo ""
echo "🚀 Launching HeritageLens AI..."
echo "The application will open in your default web browser."
echo "If it doesn't open automatically, navigate to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application."
echo ""

# Run the Streamlit app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
