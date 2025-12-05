import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from utils.detection_utils import DetectionManager
from utils.ui_utils import create_detection_charts, create_summary_text, display_metrics, generate_pdf_report

# Page configuration
st.set_page_config(
    page_title="Image Detection - HeritageLens AI",
    page_icon="📸",
    layout="wide"
)

# Apply custom CSS
from utils.ui_utils import apply_custom_css
apply_custom_css()

st.markdown("""
<div class="main-header">
    <h1>📸 Image Detection</h1>
    <p>Upload images to detect heritage sites and archaeological structures</p>
</div>
""", unsafe_allow_html=True)

# Initialize detection manager
if 'detection_manager' not in st.session_state:
    st.session_state.detection_manager = DetectionManager()

detection_manager = st.session_state.detection_manager

# Check if model is loaded
if detection_manager.model is None:
    st.error("❌ Model failed to load. Please check if the model file 'best.pt' exists.")
    st.stop()

# File uploader
st.markdown("## 📁 Upload Images")
uploaded_files = st.file_uploader(
    "Choose image files",
    type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
    accept_multiple_files=True,
    help="Upload one or more images to analyze for heritage objects"
)

def process_images(uploaded_files, detection_manager):
    """Process uploaded images and perform detection"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    all_detections = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing image {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        # Read image
        image = Image.open(uploaded_file)
        image_array = np.array(image)
        
        # Convert PIL to OpenCV format
        if len(image_array.shape) == 3:
            image_cv = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_cv = image_array
        
        # Perform detection
        detections = detection_manager.detect_objects(image_cv)
        
        # Debug information
        if detections:
            st.info(f"Found {len(detections)} objects in {uploaded_file.name}")
        else:
            st.warning(f"No objects detected in {uploaded_file.name}")
        
        # Draw detections
        annotated_image = detection_manager.draw_detections(image_cv, detections)
        
        # Convert back to RGB for display
        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        
        # Store results
        result = {
            'filename': uploaded_file.name,
            'original_image': image_array,
            'annotated_image': annotated_image_rgb,
            'detections': detections,
            'image_cv': image_cv
        }
        results.append(result)
        all_detections.extend(detections)
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Store results in session state
    st.session_state.image_results = results
    st.session_state.image_detections = all_detections
    
    # Calculate statistics
    stats = detection_manager.get_class_statistics([all_detections])
    st.session_state.image_stats = stats
    
    status_text.text("✅ Analysis complete!")
    progress_bar.empty()
    status_text.empty()
    
    st.success(f"Successfully analyzed {len(uploaded_files)} image(s)!")

def display_image_results():
    """Display the results of image detection"""
    
    results = st.session_state.image_results
    stats = st.session_state.image_stats
    
    # Get detection manager from session state
    detection_manager = st.session_state.detection_manager
    
    st.markdown("## 📊 Detection Results")
    
    # Display metrics
    display_metrics(stats)
    
    # Summary text
    summary_text = create_summary_text(stats)
    st.markdown(f"""
    <div class="info-card">
        <h4>📝 Summary</h4>
        <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("## 📈 Visualizations")
    create_detection_charts(stats)
    
    # Individual image results
    st.markdown("## 🖼️ Detected Images")
    
    for i, result in enumerate(results):
        with st.expander(f"📷 {result['filename']} - {len(result['detections'])} detections"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Image**")
                st.image(result['original_image'], use_column_width=True)
            
            with col2:
                st.markdown("**Detected Objects**")
                st.image(result['annotated_image'], use_column_width=True)
            
            # Detection details
            if result['detections']:
                st.markdown("**Detection Details:**")
                detection_data = []
                for j, detection in enumerate(result['detections']):
                    detection_data.append({
                        'Object': j + 1,
                        'Class': detection['class_name'],
                        'Confidence': f"{detection['confidence']:.2%}",
                        'Bounding Box': f"({detection['bbox'][0]:.0f}, {detection['bbox'][1]:.0f}, {detection['bbox'][2]:.0f}, {detection['bbox'][3]:.0f})"
                    })
                
                st.table(detection_data)
                
                # Show cropped detections
                crops = detection_manager.crop_detections(result['image_cv'], result['detections'])
                if crops:
                    st.markdown("**Cropped Detections:**")
                    cols = st.columns(min(len(crops), 4))
                    for idx, crop in enumerate(crops):
                        if idx < len(cols):
                            with cols[idx]:
                                # Convert BGR to RGB for display
                                crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                                st.image(crop_rgb, caption=f"Detection {idx + 1}", use_column_width=True)
    
    # Download options
    st.markdown("## 💾 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate PDF Report"):
            generate_pdf_download(stats, summary_text)
    
    with col2:
        if st.button("🔄 Clear Results"):
            clear_image_results()

def generate_pdf_download(stats, summary_text):
    """Generate and download PDF report"""
    try:
        # Collect up to 6 annotated sample images to embed in PDF
        samples = []
        if 'image_results' in st.session_state:
            for res in st.session_state.image_results[:6]:
                # annotated_image is already RGB
                samples.append(res['annotated_image'])

        pdf_data = generate_pdf_report(stats, summary_text, samples=samples)
        
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_data,
            file_name="heritage_detection_report.pdf",
            mime="application/pdf"
        )
        st.success("PDF report generated successfully!")
        
    except Exception as e:
        st.error(f"Error generating PDF report: {str(e)}")

def clear_image_results():
    """Clear image detection results"""
    if 'image_results' in st.session_state:
        del st.session_state.image_results
    if 'image_detections' in st.session_state:
        del st.session_state.image_detections
    if 'image_stats' in st.session_state:
        del st.session_state.image_stats
    st.success("Results cleared!")
    st.rerun()

# Main execution code
if uploaded_files:
    # Process images
    if st.button("🔍 Analyze Images", type="primary"):
        process_images(uploaded_files, detection_manager)

# Display results if available
if 'image_results' in st.session_state and st.session_state.image_results:
    display_image_results()