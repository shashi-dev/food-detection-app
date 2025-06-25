#!/bin/bash

# Streamlit Food Detection App Deployment Script

echo "🚀 Deploying Food Detection App to Streamlit Cloud..."

# Check if we're in the right directory
if [ ! -f "food_detection_app_streamlit.py" ]; then
    echo "❌ Error: food_detection_app_streamlit.py not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

# Check if .streamlit/config.toml exists
if [ ! -f ".streamlit/config.toml" ]; then
    echo "❌ Error: .streamlit/config.toml not found!"
    exit 1
fi

echo "✅ All required files found!"

# Display deployment information
echo ""
echo "📋 Deployment Information:"
echo "   - Main App: food_detection_app_streamlit.py"
echo "   - Requirements: requirements.txt"
echo "   - Config: .streamlit/config.toml"
echo ""

# Check for model file
if [ -f "runs/detect/yolov8n_food101/weights/best.pt" ]; then
    echo "✅ Custom YOLO model found!"
else
    echo "⚠️  Custom YOLO model not found. App will use default YOLOv8n model."
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Push your code to GitHub"
echo "2. Go to https://share.streamlit.io/"
echo "3. Connect your GitHub repository"
echo "4. Set the main file path to: food_detection_app_streamlit.py"
echo "5. Deploy!"
echo ""

echo "✅ Deployment script completed successfully!" 