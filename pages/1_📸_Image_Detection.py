import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.detection_utils import DetectionManager
from utils.ui_utils import create_detection_charts, create_summary_text, display_metrics, generate_pdf_report, apply_custom_css

st.set_page_config(
    page_title="Image Detection - HeritageLens AI",
    page_icon="📸",
    layout="wide"
)

apply_custom_css()

st.markdown("""
<style>
.page-header { background: #3B2A1A; border-radius: 12px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; }
.page-header h1 { color: #F5E6C8; font-size: 2rem; font-weight: 600; margin-bottom: 0.3rem; }
.page-header p  { color: #C9A97A; font-size: 1rem; }
.info-card { background: #FFFDF9; border: 1px solid #E8D8C0; border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; color: #2C1A0E; }
.info-card h4 { color: #5C3A1E; margin-bottom: 0.4rem; }
.info-card p, .info-card li { color: #3D2410; line-height: 1.7; }
.section-heading { color: #3B2A1A; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 0.7rem; padding-bottom: 0.3rem; border-bottom: 2px solid #C9A97A; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1>📸 Image Detection</h1>
    <p>Upload images to detect heritage sites and archaeological structures</p>
</div>
""", unsafe_allow_html=True)

if 'detection_manager' not in st.session_state:
    st.session_state.detection_manager = DetectionManager()

detection_manager = st.session_state.detection_manager

if detection_manager.model is None:
    st.error("❌ Model failed to load. Please check if the model file 'best.pt' exists.")
    st.stop()

st.markdown('<div class="section-heading">📁 Upload Images</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Choose image files",
    type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
    accept_multiple_files=True,
    help="Upload one or more images to analyse for heritage objects"
)

def process_images(uploaded_files, detection_manager):
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    all_detections = []

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing image {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
        image = Image.open(uploaded_file)
        image_array = np.array(image)
        if len(image_array.shape) == 3:
            image_cv = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_cv = image_array
        detections = detection_manager.detect_objects(image_cv)
        if detections:
            st.info(f"Found {len(detections)} objects in {uploaded_file.name}")
        else:
            st.warning(f"No objects detected in {uploaded_file.name}")
        annotated_image = detection_manager.draw_detections(image_cv, detections)
        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
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

    st.session_state.image_results = results
    st.session_state.image_detections = all_detections
    stats = detection_manager.get_class_statistics([all_detections])
    st.session_state.image_stats = stats
    status_text.empty()
    progress_bar.empty()
    st.success(f"✅ Successfully analysed {len(uploaded_files)} image(s)!")

def display_image_results():
    results = st.session_state.image_results
    stats = st.session_state.image_stats
    detection_manager = st.session_state.detection_manager

    st.markdown('<div class="section-heading">📊 Detection Results</div>', unsafe_allow_html=True)
    display_metrics(stats)

    summary_text = create_summary_text(stats)
    st.markdown(f"""
    <div class="info-card">
        <h4>📝 Summary</h4>
        <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">📈 Visualisations</div>', unsafe_allow_html=True)
    create_detection_charts(stats)

    st.markdown('<div class="section-heading">🖼️ Detected Images</div>', unsafe_allow_html=True)
    for i, result in enumerate(results):
        with st.expander(f"📷 {result['filename']} — {len(result['detections'])} detections"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original image**")
                st.image(result['original_image'], use_column_width=True)
            with col2:
                st.markdown("**Detected objects**")
                st.image(result['annotated_image'], use_column_width=True)

            if result['detections']:
                st.markdown("**Detection details**")
                detection_data = []
                for j, detection in enumerate(result['detections']):
                    detection_data.append({
                        'Object': j + 1,
                        'Class': detection['class_name'],
                        'Confidence': f"{detection['confidence']:.2%}",
                        'Bounding Box': f"({detection['bbox'][0]:.0f}, {detection['bbox'][1]:.0f}, {detection['bbox'][2]:.0f}, {detection['bbox'][3]:.0f})"
                    })
                st.table(detection_data)

                crops = detection_manager.crop_detections(result['image_cv'], result['detections'])
                if crops:
                    st.markdown("**Cropped detections**")
                    cols = st.columns(min(len(crops), 4))
                    for idx, crop in enumerate(crops):
                        if idx < len(cols):
                            with cols[idx]:
                                crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                                st.image(crop_rgb, caption=f"Detection {idx + 1}", use_column_width=True)

    st.markdown('<div class="section-heading">💾 Download Results</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Generate PDF Report"):
            generate_pdf_download(stats, summary_text)
    with col2:
        if st.button("🔄 Clear Results"):
            clear_image_results()

def generate_pdf_download(stats, summary_text):
    try:
        samples = []
        if 'image_results' in st.session_state:
            for res in st.session_state.image_results[:6]:
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
    for key in ['image_results', 'image_detections', 'image_stats']:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Results cleared!")
    st.rerun()

if uploaded_files:
    if st.button("🔍 Analyse Images", type="primary"):
        process_images(uploaded_files, detection_manager)

if 'image_results' in st.session_state and st.session_state.image_results:
    display_image_results()
