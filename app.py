import streamlit as st
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# ✅ FIXED: Files are in root, not inside utils/ folder
from detection_utils import DetectionManager
from ui_utils import apply_custom_css

# Page configuration
st.set_page_config(
    page_title="HeritageLens AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# Initialize session state
if 'detection_manager' not in st.session_state:
    try:
        st.session_state.detection_manager = DetectionManager()
    except Exception as e:
        st.error("Model file (best.pt) not found. Please upload it.")
        st.stop()

if 'detection_results' not in st.session_state:
    st.session_state.detection_results = []

if 'video_detection_active' not in st.session_state:
    st.session_state.video_detection_active = False

# Main home page content
st.markdown("""
<div class="main-header">
    <h1>🏛️ HeritageLens AI</h1>
    <p>Discover Heritage Through AI</p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="info-card">
    <h3>🌟 Welcome to HeritageLens AI</h3>
    <p>HeritageLens AI is an innovative application that uses cutting-edge YOLOv11 deep learning technology 
    to automatically detect and analyze heritage sites, archaeological structures, and cultural landmarks 
    in images and videos. Whether you're an archaeologist, historian, educator, or heritage enthusiast, 
    our AI-powered tool helps you identify and understand cultural heritage with unprecedented accuracy.</p>
</div>
""", unsafe_allow_html=True)

# Navigation instructions
st.markdown("## 🚀 How to Use This App")

st.markdown("""
<div class="info-card">
    <h4>📱 Navigation</h4>
    <p>Use the sidebar on the left to navigate between different sections:</p>
    <ul>
        <li><strong>🏠 Home</strong> - This welcome page with app overview</li>
        <li><strong>📸 Image Detection</strong> - Upload and analyze images for heritage objects</li>
        <li><strong>🎥 Video Detection</strong> - Analyze videos or YouTube links with real-time detection</li>
        <li><strong>📊 Summary Dashboard</strong> - View comprehensive analysis and statistics</li>
        <li><strong>📚 Learn About Heritage</strong> - Educational content about heritage classes</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Features section
st.markdown("## 🎯 Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-card">
        <h4>📸 Image Detection</h4>
        <p>Upload single or multiple images to detect heritage objects with bounding boxes and confidence scores.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <h4>🎥 Video Analysis</h4>
        <p>Analyze local videos or YouTube links with real-time detection and comprehensive summaries.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h4>📊 Interactive Dashboard</h4>
        <p>View detailed statistics, charts, and visual summaries of your detection results.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <h4>📚 Educational Content</h4>
        <p>Learn about different heritage classes and their cultural significance.</p>
    </div>
    """, unsafe_allow_html=True)

# Detection classes
st.markdown("## 🏺 Heritage Classes Detected")

classes_data = [
    {
        "name": "Stones / Stone Pillars / Stone Structures",
        "description": "Ancient stone constructions, pillars, and architectural elements",
        "icon": "🗿"
    },
    {
        "name": "Crops / Farmland",
        "description": "Agricultural landscapes and farming areas",
        "icon": "🌾"
    },
    {
        "name": "Non-archaeological",
        "description": "Natural landscapes like deserts, water bodies, and mountains",
        "icon": "🏔️"
    },
    {
        "name": "Heritage Sites",
        "description": "Temples, palaces, forts, museums, and cultural monuments",
        "icon": "🏛️"
    }
]

for i, class_info in enumerate(classes_data):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<h2>{class_info['icon']}</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h4>{class_info['name']}</h4>
            <p>{class_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)

# Getting started
st.markdown("## 🎯 Getting Started")

st.markdown("""
<div class="info-card">
    <h4>Ready to explore heritage through AI?</h4>
    <ol>
        <li><strong>Image Detection:</strong> Navigate to the Image Detection page and upload your photos</li>
        <li><strong>Video Analysis:</strong> Use the Video Detection page for local videos or YouTube links</li>
        <li><strong>View Results:</strong> Check the Summary Dashboard for detailed analysis</li>
        <li><strong>Learn More:</strong> Explore the Learn About Heritage section for educational content</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Technology section
st.markdown("## 🔬 Technology")

st.markdown("""
<div class="info-card">
    <h4>Powered by Advanced AI</h4>
    <p>HeritageLens AI is built on YOLOv11 (You Only Look Once version 11), one of the most advanced 
    real-time object detection models. Our custom-trained model has been specifically fine-tuned to 
    recognize heritage sites and archaeological structures with high accuracy and confidence.</p>

    <p><strong>Key Technologies:</strong></p>
    <ul>
        <li>YOLOv11 Deep Learning Model</li>
        <li>PyTorch Framework</li>
        <li>OpenCV for Image Processing</li>
        <li>Streamlit for Interactive UI</li>
        <li>Plotly for Data Visualization</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🏛️ HeritageLens AI - Preserving Heritage Through Technology</p>
    <p>Built with ❤️ for archaeologists, historians, and heritage enthusiasts</p>
</div>
""", unsafe_allow_html=True)
