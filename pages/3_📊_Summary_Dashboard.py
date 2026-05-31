import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from utils.ui_utils import create_detection_charts, create_summary_text, display_metrics, generate_pdf_report

# Page configuration
st.set_page_config(
    page_title="Summary Dashboard - HeritageLens AI",
    page_icon="📊",
    layout="wide"
)

# Apply custom CSS
from utils.ui_utils import apply_custom_css
apply_custom_css()

st.markdown("""
<div class="main-header">
    <h1>📊 Summary Dashboard</h1>
    <p>Comprehensive analysis and insights from your heritage detection sessions</p>
</div>
""", unsafe_allow_html=True)

def show_no_data_message():
    """Show message when no detection data is available"""
    st.markdown("""
    <div class="info-card">
        <h3>📊 No Detection Data Available</h3>
        <p>To view the summary dashboard, please first analyze some images or videos using the detection pages.</p>
        
        <h4>Get Started:</h4>
        <ul>
            <li>Go to <strong>Image Detection</strong> to upload and analyze photos</li>
            <li>Visit <strong>Video Detection</strong> to analyze videos or YouTube links</li>
            <li>Return here to view comprehensive analysis and insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_combined_dashboard():
    """Show combined dashboard with both image and video data"""
    
    st.markdown("## 🔄 Combined Analysis")
    
    # Combine statistics
    image_stats = st.session_state.image_stats
    video_stats = st.session_state.video_stats
    
    combined_stats = combine_statistics(image_stats, video_stats)
    
    # Overview metrics
    st.markdown("### 📈 Overview Metrics")
    display_combined_metrics(image_stats, video_stats, combined_stats)
    
    # Summary
    summary_text = create_combined_summary(image_stats, video_stats, combined_stats)
    st.markdown(f"""
    <div class="info-card">
        <h4>📝 Combined Analysis Summary</h4>
        <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for detailed analysis
    tab1, tab2, tab3 = st.tabs(["📊 Combined Charts", "📸 Image Analysis", "🎥 Video Analysis"])
    
    with tab1:
        show_combined_charts(combined_stats)
    
    with tab2:
        show_individual_analysis("Image", image_stats)
    
    with tab3:
        show_individual_analysis("Video", video_stats)
    
    # Download options
    show_download_options(combined_stats, summary_text, "Combined")

def show_image_dashboard():
    """Show dashboard for image detection results only"""
    
    st.markdown("## 📸 Image Detection Analysis")
    
    stats = st.session_state.image_stats
    
    # Overview metrics
    st.markdown("### 📈 Overview Metrics")
    display_metrics(stats)
    
    # Summary
    summary_text = create_summary_text(stats)
    st.markdown(f"""
    <div class="info-card">
        <h4>📝 Analysis Summary</h4>
        <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("### 📊 Detection Visualizations")
    create_detection_charts(stats)
    
    # Additional insights
    show_detailed_insights(stats, "Image")
    
    # Download options
    show_download_options(stats, summary_text, "Image")

def show_video_dashboard():
    """Show dashboard for video detection results only"""
    
    st.markdown("## 🎥 Video Detection Analysis")
    
    stats = st.session_state.video_stats
    duration = st.session_state.get('video_duration', 0)
    
    # Overview metrics
    st.markdown("### 📈 Overview Metrics")
    display_metrics(stats)
    
    # Video-specific metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Video Duration", f"{duration:.1f} seconds")
    
    with col2:
        fps = st.session_state.get('video_fps', 0)
        st.metric("Frame Rate", f"{fps:.1f} FPS")
    
    with col3:
        detection_rate = len(st.session_state.get('video_detections', [])) / duration if duration > 0 else 0
        st.metric("Detection Rate", f"{detection_rate:.2f} detections/sec")
    
    # Summary
    summary_text = create_summary_text(stats, duration)
    st.markdown(f"""
    <div class="info-card">
        <h4>📝 Video Analysis Summary</h4>
        <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("### 📊 Detection Visualizations")
    create_detection_charts(stats)
    
    # Additional insights
    show_detailed_insights(stats, "Video")
    
    # Download options
    show_download_options(stats, summary_text, "Video")

def combine_statistics(image_stats, video_stats):
    """Combine image and video statistics"""
    
    # Combine all detections
    all_detections = []
    if image_stats and image_stats.get('all_detections'):
        all_detections.extend(image_stats['all_detections'])
    if video_stats and video_stats.get('all_detections'):
        all_detections.extend(video_stats['all_detections'])
    
    if not all_detections:
        return {
            'total_detections': 0,
            'class_counts': {},
            'confidence_avg': 0,
            'class_confidence_avg': {}
        }
    
    # Calculate combined statistics
    class_counts = {}
    class_confidences = {}
    
    for detection in all_detections:
        class_name = detection['class_name']
        confidence = detection['confidence']
        
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        if class_name not in class_confidences:
            class_confidences[class_name] = []
        class_confidences[class_name].append(confidence)
    
    # Calculate averages
    total_confidence = sum(d['confidence'] for d in all_detections)
    confidence_avg = total_confidence / len(all_detections)
    
    class_confidence_avg = {}
    for class_name, confidences in class_confidences.items():
        class_confidence_avg[class_name] = sum(confidences) / len(confidences)
    
    return {
        'total_detections': len(all_detections),
        'class_counts': class_counts,
        'confidence_avg': confidence_avg,
        'class_confidence_avg': class_confidence_avg,
        'all_detections': all_detections
    }

def display_combined_metrics(image_stats, video_stats, combined_stats):
    """Display combined metrics for image and video data"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Detections",
            combined_stats['total_detections'],
            delta=None
        )
    
    with col2:
        image_count = image_stats.get('total_detections', 0) if image_stats else 0
        st.metric(
            "From Images",
            image_count,
            delta=None
        )
    
    with col3:
        video_count = video_stats.get('total_detections', 0) if video_stats else 0
        st.metric(
            "From Video",
            video_count,
            delta=None
        )
    
    with col4:
        st.metric(
            "Avg Confidence",
            f"{combined_stats['confidence_avg']:.1%}",
            delta=None
        )
    
    with col5:
        unique_classes = len(combined_stats['class_counts'])
        st.metric(
            "Classes Found",
            unique_classes,
            delta=None
        )

def create_combined_summary(image_stats, video_stats, combined_stats):
    """Create summary text for combined analysis"""
    
    image_count = image_stats.get('total_detections', 0) if image_stats else 0
    video_count = video_stats.get('total_detections', 0) if video_stats else 0
    total = combined_stats['total_detections']
    
    summary = f"Combined analysis of images and video content revealed {total} heritage objects. "
    summary += f"Image analysis contributed {image_count} detections, while video analysis found {video_count} objects. "
    
    if combined_stats['class_counts']:
        most_common = max(combined_stats['class_counts'].items(), key=lambda x: x[1])
        percentage = (most_common[1] / total) * 100
        summary += f"The most frequently detected class was {most_common[0]} ({percentage:.0f}% of all detections)."
    
    return summary

def show_combined_charts(stats):
    """Show charts for combined data"""
    create_detection_charts(stats)
    
    # Additional combined insights
    if stats and stats['total_detections'] > 0:
        st.markdown("### 🔍 Additional Insights")
        
        # Confidence distribution by class
        if stats.get('class_confidence_avg'):
            conf_data = []
            for class_name, avg_conf in stats['class_confidence_avg'].items():
                conf_data.append({
                    'Class': class_name,
                    'Average Confidence': avg_conf,
                    'Count': stats['class_counts'].get(class_name, 0)
                })
            
            df_conf = pd.DataFrame(conf_data)
            
            fig = px.scatter(
                df_conf,
                x='Count',
                y='Average Confidence',
                size='Count',
                color='Class',
                title="Detection Count vs Average Confidence by Class",
                labels={'Count': 'Number of Detections', 'Average Confidence': 'Average Confidence Score'}
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_individual_analysis(data_type, stats):
    """Show individual analysis for image or video data"""
    
    st.markdown(f"### {data_type} Analysis Details")
    
    if not stats or stats['total_detections'] == 0:
        st.info(f"No {data_type.lower()} detection data available.")
        return
    
    # Display metrics
    display_metrics(stats)
    
    # Show charts
    create_detection_charts(stats)

def show_detailed_insights(stats, data_type):
    """Show detailed insights and analysis"""
    
    if not stats or stats['total_detections'] == 0:
        return
    
    st.markdown("### 🔍 Detailed Insights")
    
    # Class performance analysis
    if stats['class_confidence_avg']:
        st.markdown("#### 📊 Class Performance Analysis")
        
        performance_data = []
        for class_name, avg_conf in stats['class_confidence_avg'].items():
            count = stats['class_counts'].get(class_name, 0)
            performance_data.append({
                'Class': class_name,
                'Detections': count,
                'Avg Confidence': avg_conf,
                'Performance Score': count * avg_conf  # Simple performance metric
            })
        
        df_perf = pd.DataFrame(performance_data)
        df_perf = df_perf.sort_values('Performance Score', ascending=False)
        
        st.dataframe(df_perf, use_container_width=True)
    
    # Confidence analysis
    if stats.get('all_detections'):
        st.markdown("#### 📈 Confidence Score Analysis")
        
        confidences = [d['confidence'] for d in stats['all_detections']]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Highest Confidence", f"{max(confidences):.1%}")
            st.metric("Lowest Confidence", f"{min(confidences):.1%}")
        
        with col2:
            st.metric("Median Confidence", f"{np.median(confidences):.1%}")
            st.metric("Standard Deviation", f"{np.std(confidences):.3f}")

def show_download_options(stats, summary_text, data_type):
    """Show download options for reports"""
    
    st.markdown("## 💾 Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"📄 Generate {data_type} PDF Report"):
            try:
                pdf_data = generate_pdf_report(stats, summary_text)
                
                st.download_button(
                    label=f"📥 Download {data_type} Report",
                    data=pdf_data,
                    file_name=f"heritage_{data_type.lower()}_report.pdf",
                    mime="application/pdf"
                )
                st.success(f"{data_type} PDF report generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating PDF report: {str(e)}")
    
    with col2:
        if st.button("🔄 Clear All Data"):
            clear_all_data()

def clear_all_data():
    """Clear all detection data"""
    keys_to_remove = [
        'image_results', 'image_detections', 'image_stats',
        'video_detections', 'video_stats', 'video_results',
        'current_frame', 'video_detection_active'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("All detection data cleared!")
    st.rerun()

# Main execution code
# Check for available data
has_image_data = 'image_stats' in st.session_state and st.session_state.image_stats
has_video_data = 'video_stats' in st.session_state and st.session_state.video_stats

if not has_image_data and not has_video_data:
    show_no_data_message()
else:
    # Display combined or individual results
    if has_image_data and has_video_data:
        show_combined_dashboard()
    elif has_image_data:
        show_image_dashboard()
    elif has_video_data:
        show_video_dashboard()