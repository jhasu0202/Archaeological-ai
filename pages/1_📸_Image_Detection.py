import streamlit as st
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from utils.detection_utils import DetectionManager
from utils.ui_utils import apply_custom_css

st.set_page_config(
    page_title="HeritageLens AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hero banner */
.hero-banner {
    background: #3B2A1A;
    border-radius: 12px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-banner h1 {
    color: #F5E6C8;
    font-size: 2.4rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}
.hero-banner p {
    color: #C9A97A;
    font-size: 1.1rem;
}

/* Info cards */
.info-card {
    background: #FFFDF9;
    border: 1px solid #E8D8C0;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    color: #2C1A0E;
}
.info-card h3, .info-card h4 {
    color: #5C3A1E;
    margin-bottom: 0.5rem;
}
.info-card p, .info-card li {
    color: #3D2410;
    line-height: 1.7;
}

/* Feature grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.feature-card {
    background: #FFFDF9;
    border: 1px solid #E8D8C0;
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
}
.feature-card .f-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.feature-card h4 { color: #5C3A1E; margin-bottom: 0.3rem; font-size: 1rem; }
.feature-card p  { color: #3D2410; font-size: 0.9rem; line-height: 1.5; }

/* Heritage class rows */
.class-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid #F0E0CC;
}
.class-row:last-child { border-bottom: none; }
.class-icon { font-size: 1.8rem; width: 44px; text-align: center; }
.class-name { color: #3B2A1A; font-weight: 600; font-size: 0.95rem; }
.class-desc { color: #6B4C30; font-size: 0.85rem; margin-top: 2px; }

/* Step list */
.step-item {
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    padding: 0.6rem 0;
}
.step-num {
    background: #3B2A1A;
    color: #F5E6C8;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 600;
    flex-shrink: 0;
    margin-top: 2px;
}
.step-text strong { color: #3B2A1A; }
.step-text span   { color: #6B4C30; font-size: 0.88rem; display: block; margin-top: 2px; }

/* Section headings */
.section-heading {
    color: #3B2A1A;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 1.8rem 0 0.8rem;
    padding-bottom: 0.3rem;
    border-bottom: 2px solid #C9A97A;
}

/* Footer */
.footer {
    text-align: center;
    color: #9B7B5B;
    padding: 2rem 0 1rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if 'detection_manager' not in st.session_state:
    try:
        st.session_state.detection_manager = DetectionManager()
    except Exception as e:
        st.error("⚠️ Model file (best.pt) not found. Please add it to the project root.")
        st.stop()

if 'detection_results' not in st.session_state:
    st.session_state.detection_results = []

if 'video_detection_active' not in st.session_state:
    st.session_state.video_detection_active = False

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1>🏛️ HeritageLens AI</h1>
    <p>Discover and preserve cultural heritage through deep learning</p>
</div>
""", unsafe_allow_html=True)

# ── Welcome ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">🌟 Welcome</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-card">
    <p>HeritageLens AI uses <strong>YOLOv11</strong> deep learning to automatically detect and analyse
    heritage sites, archaeological structures, and cultural landmarks in images and videos.
    Whether you're an archaeologist, historian, or heritage enthusiast — our AI tool identifies
    cultural heritage with high accuracy.</p>
</div>
""", unsafe_allow_html=True)

# ── Features ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">🎯 Key features</div>', unsafe_allow_html=True)
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="f-icon">📸</div>
        <h4>Image detection</h4>
        <p>Upload photos and get bounding boxes with confidence scores instantly.</p>
    </div>
    <div class="feature-card">
        <div class="f-icon">🎥</div>
        <h4>Video analysis</h4>
        <p>Analyse local videos or YouTube links with real-time frame detection.</p>
    </div>
    <div class="feature-card">
        <div class="f-icon">📊</div>
        <h4>Dashboard</h4>
        <p>Interactive charts, class breakdowns, and downloadable PDF reports.</p>
    </div>
    <div class="feature-card">
        <div class="f-icon">📚</div>
        <h4>Learn</h4>
        <p>Explore cultural significance, preservation tips, and AI explainers.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Heritage classes ───────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">🏺 Heritage classes detected</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-card">
    <div class="class-row">
        <div class="class-icon">🗿</div>
        <div>
            <div class="class-name">Stones / stone pillars / stone structures</div>
            <div class="class-desc">Megaliths, temple pillars, ancient stone constructions and architectural elements</div>
        </div>
    </div>
    <div class="class-row">
        <div class="class-icon">🌾</div>
        <div>
            <div class="class-name">Crops / farmland</div>
            <div class="class-desc">Agricultural landscapes, traditional farming areas and irrigation systems</div>
        </div>
    </div>
    <div class="class-row">
        <div class="class-icon">🏔️</div>
        <div>
            <div class="class-name">Non-archaeological</div>
            <div class="class-desc">Natural formations — deserts, water bodies, mountains and geographical features</div>
        </div>
    </div>
    <div class="class-row">
        <div class="class-icon">🏛️</div>
        <div>
            <div class="class-name">Heritage sites</div>
            <div class="class-desc">Temples, palaces, forts, museums and major cultural monuments</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Getting started ────────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">🚀 Getting started</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-card">
    <div class="step-item">
        <div class="step-num">1</div>
        <div class="step-text"><strong>Image Detection</strong>
        <span>Navigate to the Image Detection page, upload your photos, and click Analyse.</span></div>
    </div>
    <div class="step-item">
        <div class="step-num">2</div>
        <div class="step-text"><strong>Video Detection</strong>
        <span>Go to Video Detection, upload a local video file or paste a YouTube URL.</span></div>
    </div>
    <div class="step-item">
        <div class="step-num">3</div>
        <div class="step-text"><strong>Summary Dashboard</strong>
        <span>View combined stats, interactive charts, and download a full PDF report.</span></div>
    </div>
    <div class="step-item">
        <div class="step-num">4</div>
        <div class="step-text"><strong>Learn About Heritage</strong>
        <span>Explore each class's cultural significance and preservation best practices.</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Technology ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">🔬 Technology</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-card">
    <h4>Powered by YOLOv11</h4>
    <p>Our custom-trained model is fine-tuned specifically for heritage sites and archaeological
    structures. Key technologies include:</p>
    <ul style="margin-top: 0.6rem; padding-left: 1.4rem;">
        <li>YOLOv11 deep learning model</li>
        <li>PyTorch + Ultralytics framework</li>
        <li>OpenCV for image processing</li>
        <li>Streamlit for the interactive UI</li>
        <li>Plotly for data visualisation</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    🏛️ HeritageLens AI — preserving heritage through technology<br>
    Built with ❤️ for archaeologists, historians, and heritage enthusiasts worldwide
</div>
""", unsafe_allow_html=True)
