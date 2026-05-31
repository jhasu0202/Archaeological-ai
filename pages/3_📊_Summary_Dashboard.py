import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.ui_utils import create_detection_charts, create_summary_text, display_metrics, generate_pdf_report, apply_custom_css

st.set_page_config(page_title="Summary Dashboard - HeritageLens AI", page_icon="📊", layout="wide")
apply_custom_css()

st.markdown("""
<style>
.page-header { background: #3B2A1A; border-radius: 12px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; }
.page-header h1 { color: #F5E6C8; font-size: 2rem; font-weight: 600; margin-bottom: 0.3rem; }
.page-header p  { color: #C9A97A; font-size: 1rem; }
.info-card { background: #FFFDF9; border: 1px solid #E8D8C0; border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
.info-card h3, .info-card h4 { color: #5C3A1E; margin-bottom: 0.4rem; }
.info-card p, .info-card li { color: #3D2410; line-height: 1.7; }
.section-heading { color: #3B2A1A; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 0.7rem; padding-bottom: 0.3rem; border-bottom: 2px solid #C9A97A; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1>📊 Summary Dashboard</h1>
    <p>Comprehensive analysis and insights from your heritage detection sessions</p>
</div>
""", unsafe_allow_html=True)

def show_no_data_message():
    st.markdown("""
    <div class="info-card">
        <h3>📊 No Detection Data Yet</h3>
        <p>To view this dashboard, first analyse some images or videos using the detection pages.</p>
        <h4>Get started:</h4>
        <ul>
            <li>Go to <strong>Image Detection</strong> to upload and analyse photos</li>
            <li>Visit <strong>Video Detection</strong> to analyse videos or YouTube links</li>
            <li>Return here to view comprehensive insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def combine_statistics(image_stats, video_stats):
    all_detections = []
    if image_stats and image_stats.get('all_detections'):
        all_detections.extend(image_stats['all_detections'])
    if video_stats and video_stats.get('all_detections'):
        all_detections.extend(video_stats['all_detections'])
    if not all_detections:
        return {'total_detections': 0, 'class_counts': {}, 'confidence_avg': 0, 'class_confidence_avg': {}}
    class_counts = {}
    class_confidences = {}
    for detection in all_detections:
        cn = detection['class_name']
        cf = detection['confidence']
        class_counts[cn] = class_counts.get(cn, 0) + 1
        class_confidences.setdefault(cn, []).append(cf)
    confidence_avg = sum(d['confidence'] for d in all_detections) / len(all_detections)
    class_confidence_avg = {cn: sum(v)/len(v) for cn, v in class_confidences.items()}
    return {'total_detections': len(all_detections), 'class_counts': class_counts, 'confidence_avg': confidence_avg, 'class_confidence_avg': class_confidence_avg, 'all_detections': all_detections}

def display_combined_metrics(image_stats, video_stats, combined_stats):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total Detections", combined_stats['total_detections'])
    with col2: st.metric("From Images", image_stats.get('total_detections', 0) if image_stats else 0)
    with col3: st.metric("From Video", video_stats.get('total_detections', 0) if video_stats else 0)
    with col4: st.metric("Avg Confidence", f"{combined_stats['confidence_avg']:.1%}")
    with col5: st.metric("Classes Found", len(combined_stats['class_counts']))

def create_combined_summary(image_stats, video_stats, combined_stats):
    image_count = image_stats.get('total_detections', 0) if image_stats else 0
    video_count = video_stats.get('total_detections', 0) if video_stats else 0
    total = combined_stats['total_detections']
    summary = f"Combined analysis found {total} heritage objects. Images contributed {image_count} detections; video contributed {video_count}. "
    if combined_stats['class_counts']:
        most_common = max(combined_stats['class_counts'].items(), key=lambda x: x[1])
        pct = (most_common[1] / total) * 100
        summary += f"The most common class was {most_common[0]} ({pct:.0f}% of all detections)."
    return summary

def show_combined_charts(stats):
    create_detection_charts(stats)
    if stats and stats['total_detections'] > 0 and stats.get('class_confidence_avg'):
        st.markdown('<div class="section-heading">🔍 Count vs Confidence</div>', unsafe_allow_html=True)
        conf_data = [{'Class': cn, 'Average Confidence': ac, 'Count': stats['class_counts'].get(cn, 0)} for cn, ac in stats['class_confidence_avg'].items()]
        df_conf = pd.DataFrame(conf_data)
        fig = px.scatter(df_conf, x='Count', y='Average Confidence', size='Count', color='Class', title="Detection count vs average confidence by class")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

def show_individual_analysis(data_type, stats):
    if not stats or stats['total_detections'] == 0:
        st.info(f"No {data_type.lower()} detection data available.")
        return
    display_metrics(stats)
    create_detection_charts(stats)

def show_detailed_insights(stats, data_type):
    if not stats or stats['total_detections'] == 0:
        return
    st.markdown('<div class="section-heading">🔍 Detailed Insights</div>', unsafe_allow_html=True)
    if stats['class_confidence_avg']:
        st.markdown("**Class performance**")
        performance_data = []
        for cn, ac in stats['class_confidence_avg'].items():
            count = stats['class_counts'].get(cn, 0)
            performance_data.append({'Class': cn, 'Detections': count, 'Avg Confidence': ac, 'Score': count * ac})
        df_perf = pd.DataFrame(performance_data).sort_values('Score', ascending=False)
        st.dataframe(df_perf, use_container_width=True)
    if stats.get('all_detections'):
        confidences = [d['confidence'] for d in stats['all_detections']]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Highest Confidence", f"{max(confidences):.1%}")
            st.metric("Lowest Confidence", f"{min(confidences):.1%}")
        with col2:
            st.metric("Median Confidence", f"{np.median(confidences):.1%}")
            st.metric("Std Deviation", f"{np.std(confidences):.3f}")

def show_download_options(stats, summary_text, data_type):
    st.markdown('<div class="section-heading">💾 Download Options</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"📄 Generate {data_type} PDF Report"):
            try:
                pdf_data = generate_pdf_report(stats, summary_text)
                st.download_button(label=f"📥 Download {data_type} Report", data=pdf_data, file_name=f"heritage_{data_type.lower()}_report.pdf", mime="application/pdf")
                st.success(f"{data_type} PDF report generated!")
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    with col2:
        if st.button("🔄 Clear All Data"):
            for key in ['image_results', 'image_detections', 'image_stats', 'video_detections', 'video_stats', 'video_results', 'current_frame', 'video_detection_active']:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("All data cleared!")
            st.rerun()

def show_combined_dashboard():
    st.markdown('<div class="section-heading">🔄 Combined Analysis</div>', unsafe_allow_html=True)
    image_stats = st.session_state.image_stats
    video_stats = st.session_state.video_stats
    combined_stats = combine_statistics(image_stats, video_stats)
    display_combined_metrics(image_stats, video_stats, combined_stats)
    summary_text = create_combined_summary(image_stats, video_stats, combined_stats)
    st.markdown(f'<div class="info-card"><h4>📝 Combined Summary</h4><p>{summary_text}</p></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Combined Charts", "📸 Image Analysis", "🎥 Video Analysis"])
    with tab1: show_combined_charts(combined_stats)
    with tab2: show_individual_analysis("Image", image_stats)
    with tab3: show_individual_analysis("Video", video_stats)
    show_download_options(combined_stats, summary_text, "Combined")

def show_image_dashboard():
    st.markdown('<div class="section-heading">📸 Image Detection Analysis</div>', unsafe_allow_html=True)
    stats = st.session_state.image_stats
    display_metrics(stats)
    summary_text = create_summary_text(stats)
    st.markdown(f'<div class="info-card"><h4>📝 Summary</h4><p>{summary_text}</p></div>', unsafe_allow_html=True)
    create_detection_charts(stats)
    show_detailed_insights(stats, "Image")
    show_download_options(stats, summary_text, "Image")

def show_video_dashboard():
    st.markdown('<div class="section-heading">🎥 Video Detection Analysis</div>', unsafe_allow_html=True)
    stats = st.session_state.video_stats
    duration = st.session_state.get('video_duration', 0)
    display_metrics(stats)
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Video Duration", f"{duration:.1f}s")
    with col2: st.metric("Frame Rate", f"{st.session_state.get('video_fps', 0):.1f} FPS")
    with col3:
        rate = len(st.session_state.get('video_detections', [])) / duration if duration > 0 else 0
        st.metric("Detection Rate", f"{rate:.2f}/s")
    summary_text = create_summary_text(stats, duration)
    st.markdown(f'<div class="info-card"><h4>📝 Summary</h4><p>{summary_text}</p></div>', unsafe_allow_html=True)
    create_detection_charts(stats)
    show_detailed_insights(stats, "Video")
    show_download_options(stats, summary_text, "Video")

has_image_data = 'image_stats' in st.session_state and st.session_state.image_stats
has_video_data = 'video_stats' in st.session_state and st.session_state.video_stats

if not has_image_data and not has_video_data:
    show_no_data_message()
elif has_image_data and has_video_data:
    show_combined_dashboard()
elif has_image_data:
    show_image_dashboard()
else:
    show_video_dashboard()
