import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import os
from PIL import Image as PILImage
import matplotlib.pyplot as plt

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@300;400;600&display=swap');
    
    /* Main app styling */
    .main {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        font-family: 'Source Sans Pro', sans-serif;
        color: #2c3e50;
    }
    
    /* Ensure text visibility */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #2c3e50 !important;
        font-weight: 600;
    }
    
    .main p, .main div, .main span {
        color: #2c3e50 !important;
    }
    
    /* Streamlit main content area */
    .stApp > div > div > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #2c3e50 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        border: 3px solid #ffffff;
    }
    
    .main-header h1 {
        color: #ffffff !important;
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
        letter-spacing: 2px;
    }
    
    .main-header p {
        color: #ecf0f1 !important;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1rem 0 0 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        letter-spacing: 1px;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #8b4513;
        margin: 1rem 0;
    }
    
    .detection-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #8b4513 0%, #cd853f 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #654321 0%, #a0522d 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Sidebar navigation styling */
    .stSidebar {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Metric styling */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem;
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        background: #8b4513;
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: white;
        border-radius: 10px;
        border: 2px dashed #8b4513;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #155724 !important;
    }
    
    .stError {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #721c24 !important;
    }
    
    .stInfo {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        color: #0c5460 !important;
    }
    
    .stWarning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        color: #856404 !important;
    }
    
    /* Ensure all Streamlit text is visible */
    .stMarkdown, .stText, .stSelectbox, .stTextInput, .stTextArea {
        color: #2c3e50 !important;
    }
    
    /* Make sure tables are visible */
    .stDataFrame, .stTable {
        color: #2c3e50 !important;
    }
    
    /* Additional visibility improvements */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #2c3e50 !important;
        font-weight: 600;
    }
    
    .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #2c3e50 !important;
    }
    
    /* Streamlit widgets */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label {
        color: #2c3e50 !important;
        font-weight: 600;
    }
    
    /* Radio buttons and checkboxes */
    .stRadio label, .stCheckbox label {
        color: #2c3e50 !important;
    }
    
    /* Metrics */
    .metric-container {
        background: white;
        border: 2px solid #2c3e50;
        color: #2c3e50 !important;
    }
    
    .metric-container > div {
        color: #2c3e50 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def setup_sidebar_navigation():
    """Setup sidebar navigation menu"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 10px; margin-bottom: 1rem; border: 2px solid #ffffff;">
            <h2 style="color: #ffffff !important; font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); letter-spacing: 1px; margin: 0;">🏛️ HeritageLens AI</h2>
            <p style="color: #ecf0f1 !important; font-size: 1rem; font-weight: 600; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8); letter-spacing: 0.5px; margin: 0.5rem 0 0 0;">Discover Heritage Through AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title=None,
            options=["Home", "Image Detection", "Video Detection", "Summary Dashboard", "Learn About Heritage"],
            icons=["house", "image", "camera-video", "bar-chart", "book"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "white",
                    "background-color": "transparent",
                },
                "nav-link-selected": {
                    "background-color": "rgba(255, 255, 255, 0.2)",
                    "border-radius": "10px",
                },
            }
        )
    
    return selected

def create_detection_charts(stats: Dict):
    """Create interactive charts for detection statistics"""
    if not stats or stats['total_detections'] == 0:
        st.warning("No detection data available for visualization.")
        return
    
    # Bar chart for class counts
    if stats['class_counts']:
        fig_bar = px.bar(
            x=list(stats['class_counts'].keys()),
            y=list(stats['class_counts'].values()),
            title="Detection Count by Class",
            labels={'x': 'Heritage Class', 'y': 'Number of Detections'},
            color=list(stats['class_counts'].values()),
            color_continuous_scale='YlOrBr'
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Source Sans Pro", size=12)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Pie chart for distribution
    if len(stats['class_counts']) > 1:
        fig_pie = px.pie(
            values=list(stats['class_counts'].values()),
            names=list(stats['class_counts'].keys()),
            title="Detection Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Source Sans Pro", size=12)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Confidence histogram
    if stats.get('all_detections'):
        confidences = [d['confidence'] for d in stats['all_detections']]
        fig_hist = px.histogram(
            x=confidences,
            title="Confidence Score Distribution",
            labels={'x': 'Confidence Score', 'y': 'Frequency'},
            nbins=20,
            color_discrete_sequence=['#8b4513']
        )
        fig_hist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Source Sans Pro", size=12)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

def create_summary_text(stats: Dict, duration: float = None) -> str:
    """Generate a summary text from detection statistics"""
    if not stats or stats['total_detections'] == 0:
        return "No objects were detected in the provided content."
    
    total = stats['total_detections']
    avg_conf = stats['confidence_avg']
    
    # Find most common class
    most_common = max(stats['class_counts'].items(), key=lambda x: x[1]) if stats['class_counts'] else None
    
    summary = f"In the analyzed content"
    if duration:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        summary += f" ({minutes}m {seconds}s of footage)"
    
    summary += f", {total} heritage objects were detected with an average confidence of {avg_conf:.1%}."
    
    if most_common:
        percentage = (most_common[1] / total) * 100
        summary += f" The most common detection was {most_common[0]} ({percentage:.0f}% of all detections)."
    
    # Add class breakdown
    if len(stats['class_counts']) > 1:
        summary += " The detection breakdown includes: "
        class_breakdown = []
        for class_name, count in stats['class_counts'].items():
            percentage = (count / total) * 100
            class_breakdown.append(f"{class_name} ({percentage:.0f}%)")
        summary += ", ".join(class_breakdown) + "."
    
    return summary

def generate_pdf_report(stats: Dict, summary_text: str, samples: List = None):
    """Generate a PDF report of the detection results with charts and sample images.

    Args:
        stats: statistics dict from DetectionManager.get_class_statistics
        summary_text: formatted summary paragraph
        samples: optional list of numpy RGB arrays (sample annotated images/frames)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#8b4513'),
        alignment=1  # Center alignment
    )
    story.append(Paragraph("HeritageLens AI Detection Report", title_style))
    story.append(Spacer(1, 20))
    
    # Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Statistics table
    if stats and stats['total_detections'] > 0:
        story.append(Paragraph("Detection Statistics", styles['Heading2']))
        
        data = [['Metric', 'Value']]
        data.append(['Total Detections', str(stats['total_detections'])])
        data.append(['Average Confidence', f"{stats['confidence_avg']:.1%}"])
        
        for class_name, count in stats['class_counts'].items():
            data.append([f'{class_name} Count', str(count)])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b4513')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

    # Charts section (generated with matplotlib to avoid extra deps)
    if stats and stats.get('class_counts'):
        story.append(Paragraph("Visualizations", styles['Heading2']))

        temp_imgs = []
        try:
            # Bar chart - class counts
            fig1, ax1 = plt.subplots(figsize=(6, 3))
            classes = list(stats['class_counts'].keys())
            counts = list(stats['class_counts'].values())
            ax1.bar(range(len(classes)), counts, color="#b8860b")
            ax1.set_title('Detection Count by Class')
            ax1.set_ylabel('Count')
            ax1.set_xticks(range(len(classes)))
            ax1.set_xticklabels([c[:18] + ('…' if len(c) > 18 else '') for c in classes], rotation=45, ha='right')
            fig1.tight_layout()
            tmp1 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig1.savefig(tmp1.name, dpi=160)
            plt.close(fig1)
            temp_imgs.append(tmp1.name)
            story.append(RLImage(tmp1.name, width=6*inch, height=3*inch))
            story.append(Spacer(1, 12))

            # Pie chart - distribution
            if len(classes) > 1:
                fig2, ax2 = plt.subplots(figsize=(4.5, 4.5))
                ax2.pie(counts, labels=[c[:22] + ('…' if len(c) > 22 else '') for c in classes], autopct='%1.0f%%', startangle=140)
                ax2.set_title('Detection Distribution')
                fig2.tight_layout()
                tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                fig2.savefig(tmp2.name, dpi=160)
                plt.close(fig2)
                temp_imgs.append(tmp2.name)
                story.append(RLImage(tmp2.name, width=4.5*inch, height=4.5*inch))
                story.append(Spacer(1, 12))

            # Confidence histogram
            if stats.get('all_detections'):
                confidences = [d['confidence'] for d in stats['all_detections']]
                if confidences:
                    fig3, ax3 = plt.subplots(figsize=(6, 3))
                    ax3.hist(confidences, bins=20, color="#8b4513")
                    ax3.set_title('Confidence Score Distribution')
                    ax3.set_xlabel('Confidence')
                    ax3.set_ylabel('Frequency')
                    fig3.tight_layout()
                    tmp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    fig3.savefig(tmp3.name, dpi=160)
                    plt.close(fig3)
                    temp_imgs.append(tmp3.name)
                    story.append(RLImage(tmp3.name, width=6*inch, height=3*inch))
                    story.append(Spacer(1, 12))
        except Exception:
            # If chart generation fails, continue without charts
            pass

    # Sample detections section
    if samples:
        story.append(Paragraph("Sample Detections", styles['Heading2']))
        # Add up to 6 sample images
        for idx, np_img in enumerate(samples[:6]):
            try:
                # Ensure image is RGB numpy array; convert to PIL and save
                pil_img = PILImage.fromarray(np_img)
                tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                pil_img.save(tmp_img.name)
                story.append(RLImage(tmp_img.name, width=6*inch, height=3.375*inch))  # 16:9-ish block
                story.append(Spacer(1, 8))
            except Exception:
                continue
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer.getvalue()

def display_metrics(stats: Dict):
    """Display key metrics in a nice format"""
    if not stats or stats['total_detections'] == 0:
        st.info("No detection data available.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Detections",
            value=stats['total_detections'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Average Confidence",
            value=f"{stats['confidence_avg']:.1%}",
            delta=None
        )
    
    with col3:
        unique_classes = len(stats['class_counts'])
        st.metric(
            label="Classes Detected",
            value=unique_classes,
            delta=None
        )
    
    with col4:
        if stats['class_counts']:
            most_common = max(stats['class_counts'].items(), key=lambda x: x[1])
            st.metric(
                label="Most Common",
                value=most_common[0][:15] + "..." if len(most_common[0]) > 15 else most_common[0],
                delta=f"{most_common[1]} detections"
            )
