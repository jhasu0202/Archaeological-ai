import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import os
import time
import subprocess
import json
import sys
from pathlib import Path
from pytube import YouTube

sys.path.append(str(Path(__file__).parent.parent))

from utils.detection_utils import DetectionManager
from utils.ui_utils import create_detection_charts, create_summary_text, display_metrics, generate_pdf_report, apply_custom_css

st.set_page_config(
    page_title="Video Detection - HeritageLens AI",
    page_icon="🎥",
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
.success-card { background: #F0FAF0; border: 1px solid #A8D5A2; border-left: 4px solid #3D7A38; border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
.success-card h4 { color: #2A5225; margin-bottom: 0.3rem; }
.success-card p  { color: #3A6335; }
.section-heading { color: #3B2A1A; font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 0.7rem; padding-bottom: 0.3rem; border-bottom: 2px solid #C9A97A; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1>🎥 Video Detection</h1>
    <p>Analyse videos or YouTube links for heritage site detection</p>
</div>
""", unsafe_allow_html=True)

if 'detection_manager' not in st.session_state:
    st.session_state.detection_manager = DetectionManager()

detection_manager = st.session_state.detection_manager

if detection_manager.model is None:
    st.error("❌ Model failed to load. Please check if the model file 'best.pt' exists.")
    st.stop()

st.markdown('<div class="section-heading">📹 Video Input</div>', unsafe_allow_html=True)
input_option = st.radio(
    "Choose video input method:",
    ["Upload Local Video", "YouTube Link"],
    horizontal=True
)

def handle_local_video_upload():
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'mov', 'avi', 'mkv', 'wmv'],
        help="Upload a video file to analyse for heritage objects"
    )
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        tfile.close()
        return tfile.name
    return None

def handle_youtube_video():
    youtube_url = st.text_input(
        "Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste a YouTube video URL to analyse"
    )
    if youtube_url:
        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            st.error("Please enter a valid YouTube URL")
            return None
        st.session_state.youtube_url = youtube_url
        st.success("✅ YouTube URL ready for processing!")
        return "youtube_direct"
    return None

def display_video_controls(video_path, detection_manager):
    st.markdown('<div class="section-heading">🎮 Detection Controls</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶️ Start Detection", type="primary"):
            if video_path == "youtube_direct":
                start_youtube_detection(detection_manager)
            else:
                start_video_detection(video_path, detection_manager)
    with col2:
        if st.button("⏹️ Stop Detection"):
            stop_video_detection()
    with col3:
        if st.button("🔄 Reset"):
            reset_video_detection()

    if st.session_state.get('video_detection_active', False):
        st.info("🔴 Detection in progress... Click Stop Detection to view results.")
        if 'current_frame' in st.session_state:
            st.image(st.session_state.current_frame, caption="Live Detection", use_column_width=True)
    elif 'video_detections' in st.session_state and st.session_state.video_detections and \
         'video_stats' not in st.session_state:
        detection_manager = st.session_state.detection_manager
        stats = detection_manager.get_class_statistics([st.session_state.video_detections])
        st.session_state.video_stats = stats
        st.session_state.video_results = True
        total_detections = len(st.session_state.video_detections)
        st.success(f"✅ Processing complete! Found {total_detections} objects.")

def start_video_detection(video_path, detection_manager):
    if not os.path.exists(video_path):
        st.error("Video file not found!")
        return
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Error opening video file!")
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    st.session_state.video_detection_active = True
    st.session_state.video_detections = []
    st.session_state.video_start_time = time.time()
    st.session_state.video_fps = fps
    st.session_state.video_duration = duration
    st.session_state.processed_frames = []
    frame_placeholder = st.empty()
    progress_placeholder = st.empty()
    stats_placeholder = st.empty()
    frame_count = 0
    processed_frames = 0
    try:
        while st.session_state.get('video_detection_active', False) and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % 5 == 0:
                annotated_frame, detections = detection_manager.process_video_frame(frame)
                st.session_state.video_detections.extend(detections)
                st.session_state.processed_frames.append(annotated_frame)
                display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                st.session_state.current_frame = display_frame
                frame_placeholder.image(display_frame, caption="Live Detection", use_column_width=True)
                processed_frames += 1
                progress = min(frame_count / max(total_frames, 1), 1.0)
                progress_placeholder.progress(progress)
                current_time = time.time() - st.session_state.video_start_time
                stats_placeholder.markdown(f"**Frames processed:** {processed_frames} | **Detections:** {len(st.session_state.video_detections)} | **Time:** {current_time:.1f}s")
            time.sleep(0.01)
    except Exception as e:
        st.error(f"Error during video detection: {str(e)}")
    finally:
        cap.release()
        st.session_state.video_detection_active = False
        if st.session_state.video_detections:
            stats = detection_manager.get_class_statistics([st.session_state.video_detections])
            st.session_state.video_stats = stats
            st.session_state.video_results = True
    st.success("✅ Video detection complete!")

def start_youtube_detection(detection_manager):
    youtube_url = st.session_state.get('youtube_url')
    if not youtube_url:
        st.error("No YouTube URL provided!")
        return
    try:
        st.session_state.video_detection_active = True
        st.session_state.video_detections = []
        st.session_state.video_start_time = time.time()
        st.session_state.processed_frames = []
        frame_placeholder = st.empty()
        progress_placeholder = st.empty()
        stats_placeholder = st.empty()
        with st.spinner("Connecting to YouTube video..."):
            try:
                info_result = subprocess.run(['yt-dlp', '--dump-json', '--no-playlist', youtube_url], capture_output=True, text=True, timeout=30)
                if info_result.returncode == 0:
                    video_info = json.loads(info_result.stdout)
                    video_duration = video_info.get('duration', 0)
                    video_title = video_info.get('title', 'Unknown')
                    st.info(f"📹 {video_title} ({video_duration}s)")
                result = subprocess.run(['yt-dlp', '--get-url', '--format', 'best[ext=mp4]/best', youtube_url], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    stream_url = result.stdout.strip()
                    st.success("✅ Connected to video stream!")
                else:
                    st.error("Failed to get video stream. Please check the URL.")
                    return
            except subprocess.TimeoutExpired:
                st.error("Timeout connecting to YouTube. Please try again.")
                return
            except FileNotFoundError:
                st.error("yt-dlp not found. Please install: pip install yt-dlp")
                return
        frame_count = 0
        processed_frames = 0
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            st.error("Failed to open video stream!")
            return
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1000
        duration = total_frames / fps if fps > 0 else 0
        max_processing_time = 300
        start_time = time.time()
        try:
            while (st.session_state.get('video_detection_active', False) and cap.isOpened() and (time.time() - start_time) < max_processing_time):
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                frame_count += 1
                if frame_count % 2 == 0:
                    annotated_frame, detections = detection_manager.process_video_frame(frame)
                    st.session_state.video_detections.extend(detections)
                    st.session_state.processed_frames.append(annotated_frame)
                    display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    st.session_state.current_frame = display_frame
                    frame_placeholder.image(display_frame, caption="Live YouTube Detection", use_column_width=True)
                    processed_frames += 1
                    progress = min(frame_count / max(total_frames, 1), 1.0)
                    progress_placeholder.progress(progress)
                    current_time = time.time() - st.session_state.video_start_time
                    stats_placeholder.markdown(f"**Frames:** {processed_frames} | **Detections:** {len(st.session_state.video_detections)} | **Time:** {current_time:.1f}s")
                time.sleep(0.01)
        except Exception as e:
            st.error(f"Error during YouTube detection: {str(e)}")
        finally:
            cap.release()
            st.session_state.video_detection_active = False
            if st.session_state.video_detections:
                stats = detection_manager.get_class_statistics([st.session_state.video_detections])
                st.session_state.video_stats = stats
                st.session_state.video_results = True
                st.session_state.video_duration = time.time() - st.session_state.video_start_time
                st.session_state.video_fps = fps
        total_detections = len(st.session_state.video_detections)
        processing_time = time.time() - st.session_state.video_start_time
        st.success(f"✅ YouTube detection complete! Found {total_detections} objects in {processing_time:.1f}s")
        frame_placeholder.empty()
        progress_placeholder.empty()
        stats_placeholder.empty()
    except Exception as e:
        st.error(f"Error processing YouTube video: {str(e)}")
        st.session_state.video_detection_active = False

def stop_video_detection():
    st.session_state.video_detection_active = False
    st.info("Detection stopped. Processing results...")
    if 'video_detections' in st.session_state and st.session_state.video_detections:
        detection_manager = st.session_state.detection_manager
        stats = detection_manager.get_class_statistics([st.session_state.video_detections])
        st.session_state.video_stats = stats
        st.session_state.video_results = True
        total_detections = len(st.session_state.video_detections)
        st.success(f"✅ Found {total_detections} objects. Results displayed below.")

def reset_video_detection():
    keys_to_remove = ['video_detection_active', 'video_detections', 'video_stats', 'video_results', 'current_frame', 'video_start_time', 'video_fps', 'video_duration', 'youtube_url', 'processed_frames']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Reset complete!")
    st.rerun()

def display_video_results():
    if 'video_stats' not in st.session_state:
        st.warning("No video detection results available.")
        return
    stats = st.session_state.video_stats
    duration = st.session_state.get('video_duration', 0)

    st.markdown('<div class="section-heading">📊 Video Detection Results</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="success-card">
        <h4>✅ Video Analysis Complete</h4>
        <p>Your video has been analysed successfully. See the results and insights below.</p>
    </div>
    """, unsafe_allow_html=True)

    display_metrics(stats)

    summary_text = create_summary_text(stats, duration)
    st.markdown(f"""
    <div class="info-card">
        <h4>📝 Video Analysis Summary</h4>
        <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Video Duration", f"{duration:.1f}s")
    with col2:
        fps = st.session_state.get('video_fps', 0)
        st.metric("Frame Rate", f"{fps:.1f} FPS")
    with col3:
        st.metric("Detections Found", len(st.session_state.get('video_detections', [])))

    st.markdown('<div class="section-heading">🔍 Detection Breakdown</div>', unsafe_allow_html=True)
    if stats and stats.get('class_counts'):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Count by class**")
            for class_name, count in stats['class_counts'].items():
                percentage = (count / stats['total_detections']) * 100
                st.metric(label=class_name, value=count, delta=f"{percentage:.1f}% of total")
        with col2:
            st.markdown("**Average confidence by class**")
            if stats.get('class_confidence_avg'):
                for class_name, avg_conf in stats['class_confidence_avg'].items():
                    st.metric(label=class_name, value=f"{avg_conf:.1%}")

    st.markdown('<div class="section-heading">📈 Visualisations</div>', unsafe_allow_html=True)
    create_detection_charts(stats)

    if 'processed_frames' in st.session_state and st.session_state.processed_frames:
        st.markdown('<div class="section-heading">🎬 Sample Detection Frames</div>', unsafe_allow_html=True)
        sample_frames = st.session_state.processed_frames[::max(1, len(st.session_state.processed_frames)//6)]
        cols = st.columns(3)
        for idx, frame in enumerate(sample_frames[:6]):
            with cols[idx % 3]:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, caption=f"Frame {idx + 1}", use_column_width=True)

    st.markdown('<div class="section-heading">💾 Download Results</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Generate PDF Report"):
            generate_video_pdf_download(stats, summary_text, duration)
    with col2:
        if st.button("🎥 Download Processed Video"):
            download_processed_video()
    with col3:
        if st.button("🔄 Clear Results"):
            reset_video_detection()

def generate_video_pdf_download(stats, summary_text, duration):
    try:
        video_summary = f"Video Analysis Report\n\nDuration: {duration:.1f} seconds\n\n{summary_text}"
        samples = []
        frames = st.session_state.get('processed_frames', [])
        if frames:
            step = max(1, len(frames)//6)
            for f in frames[::step][:6]:
                samples.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        pdf_data = generate_pdf_report(stats, video_summary, samples=samples)
        st.download_button(label="📥 Download Video Report", data=pdf_data, file_name="heritage_video_report.pdf", mime="application/pdf")
        st.success("PDF report generated!")
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")

def download_processed_video():
    try:
        if 'processed_frames' not in st.session_state or not st.session_state.processed_frames:
            st.warning("No processed frames available.")
            return
        processed_frames = st.session_state.processed_frames
        temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video_path.close()
        height, width = processed_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path.name, fourcc, 10, (width, height))
        progress_bar = st.progress(0)
        for i, frame in enumerate(processed_frames):
            out.write(frame)
            progress_bar.progress((i + 1) / len(processed_frames))
        out.release()
        progress_bar.empty()
        with open(temp_video_path.name, 'rb') as video_file:
            video_data = video_file.read()
        os.unlink(temp_video_path.name)
        st.download_button(label="📥 Download Processed Video", data=video_data, file_name="heritage_detection_video.mp4", mime="video/mp4")
        st.success("✅ Processed video ready!")
    except Exception as e:
        st.error(f"Error creating video: {str(e)}")

video_path = None
if input_option == "Upload Local Video":
    video_path = handle_local_video_upload()
else:
    video_path = handle_youtube_video()

if video_path:
    display_video_controls(video_path, detection_manager)

if ('video_results' in st.session_state and st.session_state.video_results) or \
   ('video_stats' in st.session_state and st.session_state.video_stats):
    display_video_results()
