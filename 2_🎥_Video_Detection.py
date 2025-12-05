import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import os
import time
import subprocess
import requests
import sys
from pathlib import Path
from pytube import YouTube

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from utils.detection_utils import DetectionManager
from utils.ui_utils import create_detection_charts, create_summary_text, display_metrics, generate_pdf_report

# Page configuration
st.set_page_config(
    page_title="Video Detection - HeritageLens AI",
    page_icon="🎥",
    layout="wide"
)

# Apply custom CSS
from utils.ui_utils import apply_custom_css
apply_custom_css()

st.markdown("""
<div class="main-header">
    <h1>🎥 Video Detection</h1>
    <p>Analyze videos or YouTube links for heritage site detection</p>
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

# Video input options
st.markdown("## 📹 Video Input Options")

input_option = st.radio(
    "Choose video input method:",
    ["Upload Local Video", "YouTube Link"],
    horizontal=True
)

def handle_local_video_upload():
    """Handle local video file upload"""
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'mov', 'avi', 'mkv', 'wmv'],
        help="Upload a video file to analyze for heritage objects"
    )
    
    if uploaded_file is not None:
        # Save uploaded file to temporary location
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        tfile.close()
        
        return tfile.name
    
    return None

def handle_youtube_video():
    """Handle YouTube video URL input for direct processing"""
    youtube_url = st.text_input(
        "Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste a YouTube video URL to analyze directly (no download required)"
    )
    
    if youtube_url:
        try:
            # Validate URL format
            if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
                st.error("Please enter a valid YouTube URL")
                return None
            
            # Store YouTube URL for direct processing
            st.session_state.youtube_url = youtube_url
            st.success("✅ YouTube URL ready for direct processing!")
            return "youtube_direct"
                    
        except Exception as e:
            st.error(f"Error processing YouTube URL: {str(e)}")
            return None
    
    return None

def display_video_controls(video_path, detection_manager):
    """Display video detection controls and results"""
    
    st.markdown("## 🎮 Detection Controls")
    
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
    
    # Display current status
    if st.session_state.get('video_detection_active', False):
        st.info("🔴 Detection in progress... Click 'Stop Detection' to view results.")
        
        # Show live detection if available
        if 'current_frame' in st.session_state:
            st.image(st.session_state.current_frame, caption="Live Detection", use_column_width=True)
    
    # Check if processing just completed
    elif 'video_detections' in st.session_state and st.session_state.video_detections and \
         'video_stats' not in st.session_state:
        # Processing just finished, calculate stats
        detection_manager = st.session_state.detection_manager
        stats = detection_manager.get_class_statistics([st.session_state.video_detections])
        st.session_state.video_stats = stats
        st.session_state.video_results = True
        
        total_detections = len(st.session_state.video_detections)
        st.success(f"✅ Video processing completed! Found {total_detections} objects. Results displayed below.")

def start_video_detection(video_path, detection_manager):
    """Start video detection process"""
    
    if not os.path.exists(video_path):
        st.error("Video file not found!")
        return
    
    # Initialize video capture
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        st.error("Error opening video file!")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    st.session_state.video_detection_active = True
    st.session_state.video_detections = []
    st.session_state.video_start_time = time.time()
    st.session_state.video_fps = fps
    st.session_state.video_duration = duration
    st.session_state.processed_frames = []
    
    # Create placeholders for live display
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
            
            # Process every 5th frame to balance performance and accuracy
            if frame_count % 5 == 0:
                # Perform detection
                annotated_frame, detections = detection_manager.process_video_frame(frame)
                
                # Store detections
                st.session_state.video_detections.extend(detections)
                
                # Store processed frame for video output
                st.session_state.processed_frames.append(annotated_frame)
                
                # Convert frame for display
                display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                st.session_state.current_frame = display_frame
                
                # Update display
                frame_placeholder.image(display_frame, caption="Live Detection", use_column_width=True)
                
                processed_frames += 1
                
                # Update progress
                progress = min(frame_count / max(total_frames, 1), 1.0)
                progress_placeholder.progress(progress)
                
                # Update stats
                current_time = time.time() - st.session_state.video_start_time
                stats_text = f"""
                **Detection Stats:**
                - Processed Frames: {processed_frames}
                - Total Detections: {len(st.session_state.video_detections)}
                - Elapsed Time: {current_time:.1f}s
                - Progress: {progress*100:.1f}%
                """
                stats_placeholder.markdown(stats_text)
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.01)
    
    except Exception as e:
        st.error(f"Error during video detection: {str(e)}")
    
    finally:
        cap.release()
        st.session_state.video_detection_active = False
        
        # Calculate final statistics
        if st.session_state.video_detections:
            stats = detection_manager.get_class_statistics([st.session_state.video_detections])
            st.session_state.video_stats = stats
            st.session_state.video_results = True
    
    st.success("Video detection completed!")

def start_youtube_detection(detection_manager):
    """Start YouTube video detection using direct stream processing"""
    
    youtube_url = st.session_state.get('youtube_url')
    if not youtube_url:
        st.error("No YouTube URL provided!")
        return
    
    try:
        # Initialize video processing
        st.session_state.video_detection_active = True
        st.session_state.video_detections = []
        st.session_state.video_start_time = time.time()
        st.session_state.processed_frames = []
        
        # Create placeholders for live display
        frame_placeholder = st.empty()
        progress_placeholder = st.empty()
        stats_placeholder = st.empty()
        
        # Use yt-dlp to get video stream URL and info
        with st.spinner("Connecting to YouTube video..."):
            try:
                # First get video info
                info_result = subprocess.run([
                    'yt-dlp', '--dump-json', '--no-playlist', youtube_url
                ], capture_output=True, text=True, timeout=30)
                
                if info_result.returncode == 0:
                    import json
                    video_info = json.loads(info_result.stdout)
                    video_duration = video_info.get('duration', 0)
                    video_title = video_info.get('title', 'Unknown')
                    
                    st.info(f"📹 Video: {video_title} ({video_duration}s)")
                
                # Get video stream URL
                result = subprocess.run([
                    'yt-dlp', '--get-url', '--format', 'best[ext=mp4]/best', youtube_url
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    stream_url = result.stdout.strip()
                    st.success("✅ Connected to YouTube video stream!")
                else:
                    st.error("Failed to get video stream. Please check the URL.")
                    return
                    
            except subprocess.TimeoutExpired:
                st.error("Timeout connecting to YouTube. Please try again.")
                return
            except FileNotFoundError:
                st.error("yt-dlp not found. Please install yt-dlp: pip install yt-dlp")
                return
        
        # Process video frames
        frame_count = 0
        processed_frames = 0
        
        # Create video capture from stream URL
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            st.error("Failed to open video stream!")
            return
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1000
        duration = total_frames / fps if fps > 0 else 0
        
        st.info(f"📹 Video Info: {total_frames} frames, {fps:.1f} FPS, {duration:.1f}s duration")
        
        # Set a maximum processing time (5 minutes for YouTube videos)
        max_processing_time = 300  # 5 minutes
        start_time = time.time()
        
        try:
            while (st.session_state.get('video_detection_active', False) and 
                   cap.isOpened() and 
                   (time.time() - start_time) < max_processing_time):
                
                ret, frame = cap.read()
                
                if not ret:
                    # If we can't read more frames, try to continue for a bit longer
                    # This handles cases where the stream might have temporary interruptions
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Process every 2nd frame for better coverage (changed from 3rd)
                if frame_count % 2 == 0:
                    # Perform detection
                    annotated_frame, detections = detection_manager.process_video_frame(frame)
                    
                    # Store detections
                    st.session_state.video_detections.extend(detections)
                    
                    # Store processed frame for video output
                    st.session_state.processed_frames.append(annotated_frame)
                    
                    # Convert frame for display
                    display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    st.session_state.current_frame = display_frame
                    
                    # Update display
                    frame_placeholder.image(display_frame, caption="Live YouTube Detection", use_column_width=True)
                    
                    processed_frames += 1
                    
                    # Update progress (ensure it doesn't exceed 1.0)
                    progress = min(frame_count / max(total_frames, 1), 1.0)
                    progress_placeholder.progress(progress)
                    
                    # Update stats
                    current_time = time.time() - st.session_state.video_start_time
                    progress_percent = progress * 100
                    stats_text = f"""
                    **YouTube Detection Stats:**
                    - Processed Frames: {processed_frames}
                    - Total Detections: {len(st.session_state.video_detections)}
                    - Elapsed Time: {current_time:.1f}s
                    - Progress: {progress_percent:.1f}%
                    - Video Duration: {duration:.1f}s
                    """
                    stats_placeholder.markdown(stats_text)
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
        
        except Exception as e:
            st.error(f"Error during YouTube video processing: {str(e)}")
        
        finally:
            cap.release()
            st.session_state.video_detection_active = False
            
            # Calculate final statistics
            if st.session_state.video_detections:
                stats = detection_manager.get_class_statistics([st.session_state.video_detections])
                st.session_state.video_stats = stats
                st.session_state.video_results = True
                st.session_state.video_duration = time.time() - st.session_state.video_start_time
                st.session_state.video_fps = fps  # Store the actual FPS
        
        # Show completion message with statistics
        total_detections = len(st.session_state.video_detections)
        processing_time = time.time() - st.session_state.video_start_time
        st.success(f"✅ YouTube video detection completed! Found {total_detections} objects in {processing_time:.1f}s")
        
        # Clear the live detection display
        frame_placeholder.empty()
        progress_placeholder.empty()
        stats_placeholder.empty()
        
    except Exception as e:
        st.error(f"Error processing YouTube video: {str(e)}")
        st.session_state.video_detection_active = False

def stop_video_detection():
    """Stop video detection process"""
    st.session_state.video_detection_active = False
    st.info("Detection stopped. Processing results...")
    
    # Calculate final statistics
    if 'video_detections' in st.session_state and st.session_state.video_detections:
        detection_manager = st.session_state.detection_manager
        stats = detection_manager.get_class_statistics([st.session_state.video_detections])
        st.session_state.video_stats = stats
        st.session_state.video_results = True
        
        # Show completion message
        total_detections = len(st.session_state.video_detections)
        st.success(f"✅ Detection stopped! Found {total_detections} objects. Results displayed below.")

def reset_video_detection():
    """Reset video detection state"""
    keys_to_remove = [
        'video_detection_active', 'video_detections', 'video_stats', 
        'video_results', 'current_frame', 'video_start_time',
        'video_fps', 'video_duration', 'youtube_url', 'processed_frames'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Video detection reset!")
    st.rerun()

def display_video_results():
    """Display video detection results"""
    
    if 'video_stats' not in st.session_state:
        st.warning("No video detection results available.")
        return
    
    stats = st.session_state.video_stats
    duration = st.session_state.get('video_duration', 0)
    
    st.markdown("## 📊 Video Detection Results")
    
    # Show completion banner
    st.markdown("""
    <div class="info-card" style="background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%); border-left: 5px solid #28a745;">
        <h4>✅ Video Analysis Complete!</h4>
        <p>Your video has been successfully analyzed. Below are the comprehensive results and insights.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display metrics
    display_metrics(stats)
    
    # Summary text with duration
    summary_text = create_summary_text(stats, duration)
    st.markdown(f"""
    <div class="info-card">
        <h4>📝 Video Analysis Summary</h4>
        <p>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Video statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Video Duration", f"{duration:.1f} seconds")
    
    with col2:
        fps = st.session_state.get('video_fps', 0)
        st.metric("Frame Rate", f"{fps:.1f} FPS")
    
    with col3:
        processed_frames = len(st.session_state.get('video_detections', []))
        st.metric("Detections Found", processed_frames)
    
    # Detailed breakdown
    st.markdown("## 🔍 Detailed Detection Breakdown")
    
    if stats and stats.get('class_counts'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Detection Count by Class")
            for class_name, count in stats['class_counts'].items():
                percentage = (count / stats['total_detections']) * 100
                st.metric(
                    label=class_name,
                    value=count,
                    delta=f"{percentage:.1f}% of total"
                )
        
        with col2:
            st.markdown("### 📈 Average Confidence by Class")
            if stats.get('class_confidence_avg'):
                for class_name, avg_conf in stats['class_confidence_avg'].items():
                    st.metric(
                        label=class_name,
                        value=f"{avg_conf:.1%}",
                        delta="Average confidence"
                    )
    
    # Charts
    st.markdown("## 📈 Detection Visualizations")
    create_detection_charts(stats)
    
    # Sample detections
    if 'processed_frames' in st.session_state and st.session_state.processed_frames:
        st.markdown("## 🎬 Sample Detection Frames")
        st.markdown("Here are some sample frames from your video showing the detected objects:")
        
        # Show a few sample frames
        sample_frames = st.session_state.processed_frames[::max(1, len(st.session_state.processed_frames)//6)]
        
        cols = st.columns(min(len(sample_frames), 3))
        for idx, frame in enumerate(sample_frames[:6]):  # Show max 6 frames
            if idx < len(cols):
                with cols[idx % 3]:
                    # Convert BGR to RGB for display
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(frame_rgb, caption=f"Frame {idx + 1}", use_column_width=True)
    
    # Download options
    st.markdown("## 💾 Download Results")
    
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
    """Generate and download PDF report for video"""
    try:
        # Add video-specific information to summary
        video_summary = f"Video Analysis Report\n\nDuration: {duration:.1f} seconds\n\n{summary_text}"

        # Collect a few processed frames to embed
        samples = []
        frames = st.session_state.get('processed_frames', [])
        if frames:
            # Convert BGR to RGB for embedding in PDF
            step = max(1, len(frames)//6)
            for f in frames[::step][:6]:
                samples.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))

        pdf_data = generate_pdf_report(stats, video_summary, samples=samples)
        
        st.download_button(
            label="📥 Download Video Analysis Report",
            data=pdf_data,
            file_name="heritage_video_analysis_report.pdf",
            mime="application/pdf"
        )
        st.success("Video analysis PDF report generated successfully!")
        
    except Exception as e:
        st.error(f"Error generating PDF report: {str(e)}")

def download_processed_video():
    """Create and download processed video with detections"""
    try:
        if 'processed_frames' not in st.session_state or not st.session_state.processed_frames:
            st.warning("No processed video frames available for download.")
            return
        
        processed_frames = st.session_state.processed_frames
        
        if not processed_frames:
            st.warning("No processed frames to create video.")
            return
        
        # Create temporary video file
        temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video_path.close()
        
        # Get video properties
        height, width = processed_frames[0].shape[:2]
        fps = 10  # Reduced FPS for processed video
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path.name, fourcc, fps, (width, height))
        
        # Write frames to video
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, frame in enumerate(processed_frames):
            out.write(frame)
            progress = (i + 1) / len(processed_frames)
            progress_bar.progress(progress)
            status_text.text(f"Creating video: {i + 1}/{len(processed_frames)} frames")
        
        out.release()
        progress_bar.empty()
        status_text.empty()
        
        # Read the video file for download
        with open(temp_video_path.name, 'rb') as video_file:
            video_data = video_file.read()
        
        # Clean up temporary file
        os.unlink(temp_video_path.name)
        
        # Provide download button
        st.download_button(
            label="📥 Download Processed Video",
            data=video_data,
            file_name="heritage_detection_video.mp4",
            mime="video/mp4"
        )
        
        st.success("✅ Processed video ready for download!")
        
    except Exception as e:
        st.error(f"Error creating processed video: {str(e)}")

# Main execution code
video_path = None

if input_option == "Upload Local Video":
    video_path = handle_local_video_upload()
else:
    video_path = handle_youtube_video()

# Video detection controls
if video_path:
    display_video_controls(video_path, detection_manager)

# Display results if detection is complete or if we have results
if ('video_results' in st.session_state and st.session_state.video_results) or \
   ('video_stats' in st.session_state and st.session_state.video_stats):
    display_video_results()