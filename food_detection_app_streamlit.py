#!/usr/bin/env python3
"""
Food Detection Application using YOLOv8 - Streamlit Version
A Streamlit web application for detecting food items in images.
"""

import streamlit as st
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
import tempfile
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Food Detection App",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Food classes
FOOD_CLASSES = [
    "Apple Pie", "Chocolate", "French Fries", "Hotdog", "Nachos", 
    "Pizza", "onion_rings", "pancakes", "spring_rolls", "tacos"
]

# Global model variable
@st.cache_resource
def load_model():
    """Load the YOLO model with caching for Streamlit."""
    try:
        # Try to load from the expected path
        model_path = "runs/detect/yolov8n_food101/weights/best.pt"
        if os.path.exists(model_path):
            model = YOLO(model_path)
            st.success("✅ YOLO model loaded successfully!")
        else:
            st.warning("⚠️  Model not found at expected path. Using default YOLO model.")
            # Fallback to a smaller model for cloud deployment
            model = YOLO("yolov8n.pt")
        return model
    except Exception as e:
        st.error(f"❌ Error loading YOLO model: {e}")
        return None

def process_image(image, model):
    """Process image with YOLO model and return results."""
    if model is None:
        return {"error": "Model not loaded"}
    
    try:
        # Run inference
        results = model(image)
        
        # Process results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get confidence and class
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Get class name (handle both custom and COCO classes)
                    if class_id < len(FOOD_CLASSES):
                        class_name = FOOD_CLASSES[class_id]
                    else:
                        # Map COCO classes to food-related names
                        coco_food_mapping = {
                            0: "Person", 1: "Bicycle", 2: "Car", 3: "Motorcycle",
                            # Add more mappings as needed
                        }
                        class_name = coco_food_mapping.get(class_id, f"Object_{class_id}")
                    
                    detections.append({
                        'class_name': class_name,
                        'confidence': round(confidence * 100, 2),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })
        
        return {
            'success': True,
            'detections': detections,
            'total_detections': len(detections)
        }
        
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}

def draw_detections_on_image(image, detections):
    """Draw bounding boxes and labels on image using PIL."""
    # Convert to PIL Image if it's not already
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    
    # Create a copy to draw on
    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)
    
    # Try to load a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class_name']
        confidence = detection['confidence']
        
        # Draw bounding box
        draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=3)
        
        # Draw label
        label = f"{class_name}: {confidence}%"
        
        # Get text size
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw label background
        draw.rectangle([x1, y1 - text_height - 5, x1 + text_width + 5, y1], 
                      fill=(0, 255, 0))
        
        # Draw text
        draw.text((x1 + 2, y1 - text_height - 3), label, fill=(0, 0, 0), font=font)
    
    return annotated_image

def main():
    """Main Streamlit application."""
    st.title("🍕 Food Detection Application")
    st.markdown("Upload an image to detect food items using YOLOv8!")
    
    # Load model
    with st.spinner("Loading YOLO model..."):
        model = load_model()
    
    if model is None:
        st.error("Failed to load the model. Please check the model file.")
        return
    
    # Sidebar
    st.sidebar.header("📊 App Information")
    st.sidebar.markdown(f"**Supported Food Classes:** {len(FOOD_CLASSES)}")
    st.sidebar.markdown("**Model:** YOLOv8")
    
    # Display food classes
    with st.sidebar.expander("🍽️ Supported Food Items"):
        for i, food_class in enumerate(FOOD_CLASSES, 1):
            st.write(f"{i}. {food_class}")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Image")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            help="Upload an image to detect food items"
        )
        
        if uploaded_file is not None:
            # Display original image
            st.subheader("📷 Original Image")
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Process button
            if st.button("🔍 Detect Food Items", type="primary"):
                with st.spinner("Processing image..."):
                    # Process the image
                    results = process_image(image, model)
                    
                    if results.get('success'):
                        st.success(f"✅ Found {results['total_detections']} food items!")
                        
                        # Display results
                        st.subheader("🎯 Detection Results")
                        
                        # Create results table
                        if results['detections']:
                            detection_data = []
                            for detection in results['detections']:
                                detection_data.append({
                                    'Food Item': detection['class_name'],
                                    'Confidence': f"{detection['confidence']}%",
                                    'Bounding Box': f"({detection['bbox'][0]}, {detection['bbox'][1]}) to ({detection['bbox'][2]}, {detection['bbox'][3]})"
                                })
                            
                            st.dataframe(detection_data, use_container_width=True)
                        
                        # Draw detections on image
                        annotated_image = draw_detections_on_image(image, results['detections'])
                        
                        with col2:
                            st.subheader("🎨 Annotated Image")
                            st.image(annotated_image, caption="Detected Food Items", use_column_width=True)
                            
                            # Download button for annotated image
                            buf = io.BytesIO()
                            annotated_image.save(buf, format='PNG')
                            byte_im = buf.getvalue()
                            
                            st.download_button(
                                label="📥 Download Annotated Image",
                                data=byte_im,
                                file_name="annotated_food_detection.png",
                                mime="image/png"
                            )
                    else:
                        st.error(f"❌ Error: {results.get('error', 'Unknown error')}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🍕 Food Detection App powered by YOLOv8 and Streamlit</p>
            <p>Upload images to detect various food items with confidence scores</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 