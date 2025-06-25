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
        # Try multiple possible model paths
        possible_paths = [
            "runs/detect/yolov8n_food101/weights/best.pt",
            "best.pt",
            "model.pt",
            "yolov8n_food101.pt",
            "food_detection_model.pt"
        ]
        
        model = None
        loaded_path = None
        
        # Try each possible path
        for model_path in possible_paths:
            if os.path.exists(model_path):
                try:
                    model = YOLO(model_path)
                    loaded_path = model_path
                    break
                except Exception as e:
                    st.warning(f"⚠️  Failed to load model from {model_path}: {e}")
                    continue
        
        if model is not None:
            st.success(f"✅ Custom YOLO model loaded successfully from: {loaded_path}")
            return model
        else:
            st.warning("⚠️  No custom model found. Using default YOLOv8n model.")
            st.info("💡 To use your custom model, add it to the repository as 'best.pt' or update the model path.")
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
    
    # Initialize session state
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'processed_results' not in st.session_state:
        st.session_state.processed_results = None
    if 'upload_key' not in st.session_state:
        st.session_state.upload_key = 0
    
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
    
    # Model upload section
    with st.sidebar.expander("🤖 Upload Custom Model"):
        st.markdown("Upload your custom YOLO model (.pt file)")
        uploaded_model = st.file_uploader(
            "Choose a YOLO model file",
            type=['pt'],
            key="model_uploader",
            help="Upload your custom trained YOLO model"
        )
        
        if uploaded_model is not None:
            # Save the uploaded model
            model_filename = uploaded_model.name
            with open(model_filename, "wb") as f:
                f.write(uploaded_model.getbuffer())
            
            st.success(f"✅ Model uploaded: {model_filename}")
            st.info("🔄 Please refresh the page to load the new model.")
    
    # Display food classes
    with st.sidebar.expander("🍽️ Supported Food Items"):
        for i, food_class in enumerate(FOOD_CLASSES, 1):
            st.write(f"{i}. {food_class}")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Image")
        
        # Add a clear button to reset
        if st.button("🔄 Clear Upload", help="Clear the current upload and start fresh", key="clear_button"):
            st.session_state.uploaded_file = None
            st.session_state.processed_results = None
            st.session_state.upload_key += 1
            st.rerun()
        
        # Upload method selector
        upload_method = st.selectbox(
            "Choose upload method:",
            ["URL Upload (Recommended)", "File Upload", "Camera Upload"],
            key="upload_method_selector",
            help="URL upload is most reliable and doesn't require clicking"
        )
        
        uploaded_file = None
        image = None
        
        if upload_method == "URL Upload (Recommended)":
            st.markdown("**🌐 Upload from URL (Most Reliable)**")
            st.markdown("Paste an image URL below:")
            
            image_url = st.text_input(
                "Image URL:",
                placeholder="https://example.com/food-image.jpg",
                key="url_input",
                help="Paste a direct link to an image"
            )
            
            if image_url and image_url.strip():
                try:
                    import requests
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        image = Image.open(io.BytesIO(response.content))
                        st.success("✅ Image loaded successfully from URL!")
                        st.image(image, caption="Image from URL", use_container_width=True)
                        
                        # Create a mock uploaded file for consistency
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_byte_arr.seek(0)
                        uploaded_file = type('MockFile', (), {
                            'name': 'image_from_url.png',
                            'getvalue': lambda self: img_byte_arr.getvalue()
                        })()
                    else:
                        st.error(f"❌ Failed to load image from URL (Status: {response.status_code})")
                except Exception as e:
                    st.error(f"❌ Error loading image from URL: {str(e)}")
                    st.info("💡 Make sure the URL is a direct link to an image file.")
        
        elif upload_method == "File Upload":
            st.markdown("**📁 File Upload**")
            try:
                uploaded_file = st.file_uploader(
                    "Choose an image file",
                    type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
                    key=f"file_uploader_{st.session_state.upload_key}",
                    help="Upload an image file from your computer"
                )
                
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    st.success(f"✅ Successfully uploaded: {uploaded_file.name}")
                    st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ File upload error: {str(e)}")
                st.info("💡 Try the URL upload method instead.")
        
        else:  # Camera Upload
            st.markdown("**📷 Camera Upload**")
            try:
                uploaded_file = st.camera_input(
                    "Take a photo",
                    key=f"camera_uploader_{st.session_state.upload_key}",
                    help="Take a photo with your camera"
                )
                
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    st.success("✅ Photo captured successfully!")
                    st.image(image, caption="Photo from camera", use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Camera error: {str(e)}")
                st.info("💡 Try the URL upload method instead.")
        
        # Process image if available
        if image is not None and uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            
            # Show file info
            try:
                if hasattr(uploaded_file, 'getvalue') and callable(getattr(uploaded_file, 'getvalue', None)):
                    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
                    st.info(f"📁 File size: {file_size:.2f} MB")
                elif hasattr(uploaded_file, 'size'):
                    file_size = uploaded_file.size / (1024 * 1024)  # MB
                    st.info(f"📁 File size: {file_size:.2f} MB")
                else:
                    st.info("📁 File size: Unknown")
            except Exception:
                st.info("📁 File size: Unknown")
            
            # Process button
            process_key = f"detect_button_{st.session_state.upload_key}"
            if st.button("🔍 Detect Food Items", type="primary", key=process_key):
                with st.spinner("Processing image..."):
                    try:
                        # Process the image
                        results = process_image(image, model)
                        st.session_state.processed_results = results
                        
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
                                st.image(annotated_image, caption="Detected Food Items", use_container_width=True)
                                
                                # Download button for annotated image
                                buf = io.BytesIO()
                                annotated_image.save(buf, format='PNG')
                                byte_im = buf.getvalue()
                                
                                download_key = f"download_button_{st.session_state.upload_key}"
                                st.download_button(
                                    label="📥 Download Annotated Image",
                                    data=byte_im,
                                    file_name=f"annotated_food_detection.png",
                                    mime="image/png",
                                    key=download_key
                                )
                        else:
                            st.error(f"❌ Error: {results.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"❌ Processing error: {str(e)}")
        
        # Show current file if already uploaded
        elif st.session_state.uploaded_file is not None:
            uploaded_file = st.session_state.uploaded_file
            st.subheader("📷 Current Image")
            try:
                if hasattr(uploaded_file, 'getvalue') and callable(getattr(uploaded_file, 'getvalue', None)):
                    image = Image.open(io.BytesIO(uploaded_file.getvalue()))
                else:
                    image = Image.open(uploaded_file)
                
                st.image(image, caption="Current image", use_container_width=True)
                
                # Process button
                process_key = f"detect_button_{st.session_state.upload_key}"
                if st.button("🔍 Detect Food Items", type="primary", key=process_key):
                    with st.spinner("Processing image..."):
                        try:
                            # Process the image
                            results = process_image(image, model)
                            st.session_state.processed_results = results
                            
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
                                    st.image(annotated_image, caption="Detected Food Items", use_container_width=True)
                                    
                                    # Download button for annotated image
                                    buf = io.BytesIO()
                                    annotated_image.save(buf, format='PNG')
                                    byte_im = buf.getvalue()
                                    
                                    download_key = f"download_button_{st.session_state.upload_key}"
                                    st.download_button(
                                        label="📥 Download Annotated Image",
                                        data=byte_im,
                                        file_name=f"annotated_food_detection.png",
                                        mime="image/png",
                                        key=download_key
                                    )
                            else:
                                st.error(f"❌ Error: {results.get('error', 'Unknown error')}")
                                
                        except Exception as e:
                            st.error(f"❌ Processing error: {str(e)}")
                            
            except Exception as e:
                st.error(f"❌ Error loading image: {str(e)}")
        
        # Help section
        st.markdown("---")
        st.markdown("**💡 Quick Start Guide:**")
        st.markdown("1. **URL Upload (Recommended)**: Paste any image URL - no clicking required!")
        st.markdown("2. **File Upload**: Traditional file browser upload")
        st.markdown("3. **Camera Upload**: Take a photo directly")
        st.markdown("")
        st.markdown("**🔧 If you have issues:**")
        st.markdown("- Use URL upload method (most reliable)")
        st.markdown("- Try different image URLs")
        st.markdown("- Use the Clear Upload button to reset")
    
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