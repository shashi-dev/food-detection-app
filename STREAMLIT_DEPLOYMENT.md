# 🍕 Food Detection App - Streamlit Deployment Guide

This guide will help you deploy the Food Detection Application to Streamlit Cloud without the OpenCV dependency issues.

## 🚀 Quick Deployment

### Prerequisites
- GitHub account
- Food detection app code pushed to GitHub
- Streamlit Cloud account (free at https://share.streamlit.io/)

### Step 1: Prepare Your Repository

Make sure your repository contains these files:
```
food-detection-app/
├── food_detection_app_streamlit.py  # Main Streamlit app
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── runs/detect/yolov8n_food101/weights/best.pt  # Optional: Custom model
└── README.md
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: Visit https://share.streamlit.io/
2. **Sign in**: Use your GitHub account
3. **New App**: Click "New app"
4. **Repository**: Select your food detection app repository
5. **Branch**: Choose your main branch (usually `main` or `master`)
6. **Main file path**: Set to `food_detection_app_streamlit.py`
7. **Deploy**: Click "Deploy!"

## 🔧 Configuration

### Streamlit Config (.streamlit/config.toml)
```toml
[global]
developmentMode = false

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Requirements (requirements.txt)
```
streamlit==1.46.0
ultralytics==8.0.196
pillow==10.0.1
numpy==1.24.3
torch==2.5.0
torchvision>=0.14.0
```

## 🎯 Key Features

### ✅ What Works
- **No OpenCV Dependencies**: Uses PIL for image processing
- **Cloud Optimized**: Designed for Streamlit Cloud deployment
- **Model Caching**: Efficient model loading with Streamlit caching
- **Fallback Model**: Uses default YOLOv8n if custom model not found
- **Interactive UI**: Modern Streamlit interface with file upload
- **Download Results**: Save annotated images directly from the app

### 🍽️ Supported Food Classes
1. Apple Pie
2. Chocolate
3. French Fries
4. Hotdog
5. Nachos
6. Pizza
7. Onion Rings
8. Pancakes
9. Spring Rolls
10. Tacos

## 🛠️ Troubleshooting

### Common Issues

#### 1. Model Loading Error
**Problem**: Custom model not found
**Solution**: The app will automatically fallback to the default YOLOv8n model

#### 2. Memory Issues
**Problem**: App crashes due to memory limits
**Solution**: 
- Use smaller images (max 16MB)
- The app automatically resizes images for processing

#### 3. Slow Loading
**Problem**: App takes too long to start
**Solution**: 
- Model is cached after first load
- Subsequent visits will be faster

### Performance Tips

1. **Image Size**: Keep uploaded images under 5MB for best performance
2. **Model**: Use the custom trained model for better food detection accuracy
3. **Caching**: The app uses Streamlit's caching for optimal performance

## 🔄 Local Development

To run the app locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run food_detection_app_streamlit.py
```

## 📊 App Structure

```
food_detection_app_streamlit.py
├── Main Application
│   ├── Page Configuration
│   ├── Model Loading (with caching)
│   ├── Image Processing
│   └── UI Components
├── Functions
│   ├── load_model() - Load YOLO model
│   ├── process_image() - Run inference
│   ├── draw_detections_on_image() - Annotate results
│   └── main() - Streamlit app logic
└── Features
    ├── File Upload
    ├── Real-time Processing
    ├── Results Display
    ├── Image Download
    └── Responsive Design
```

## 🎨 Customization

### Theme Colors
Edit `.streamlit/config.toml` to change the app theme:
```toml
[theme]
primaryColor = "#FF6B6B"      # Main accent color
backgroundColor = "#FFFFFF"   # Background color
secondaryBackgroundColor = "#F0F2F6"  # Sidebar background
textColor = "#262730"         # Text color
```

### Food Classes
Update the `FOOD_CLASSES` list in `food_detection_app_streamlit.py` to match your model's classes.

## 📈 Monitoring

### Streamlit Cloud Dashboard
- **Usage**: Monitor app usage and performance
- **Logs**: View real-time application logs
- **Settings**: Configure app settings and environment variables

### Performance Metrics
- **Load Time**: Model loading and caching performance
- **Processing Time**: Image detection speed
- **Memory Usage**: Resource utilization

## 🆘 Support

If you encounter issues:

1. **Check Logs**: View Streamlit Cloud logs for error messages
2. **Verify Files**: Ensure all required files are in your repository
3. **Test Locally**: Run the app locally to identify issues
4. **Update Dependencies**: Keep requirements.txt up to date

## 🎉 Success!

Once deployed, your app will be available at:
`https://your-app-name-your-username.streamlit.app`

The app provides a user-friendly interface for food detection with:
- 📤 Easy image upload
- 🔍 Real-time food detection
- 📊 Detailed results display
- 🎨 Annotated image output
- 📥 Download functionality

Enjoy your deployed Food Detection App! 🍕 