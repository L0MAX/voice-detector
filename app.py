import streamlit as st
from utils import download_video, analyze_accent, cleanup_files
import os
import tempfile
from pathlib import Path
import shutil

# Page configuration
st.set_page_config(
    page_title="Accent Detector",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        border-color: #FF4B4B;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    h1 {
        color: #FF4B4B;
    }
    .accent-info {
        font-size: 1.2em;
        padding: 1em;
        border-radius: 5px;
        background-color: #f8f9fa;
        margin: 1em 0;
    }
    .stProgress > div > div {
        background-color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# App header
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.title("🎙️ Accent Detector")
    st.markdown("""
        <div style='text-align: center'>
        Analyze English accents from video content for hiring purposes.
        Upload a video or provide a URL to get started.
        </div>
    """, unsafe_allow_html=True)

# Add after imports
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB in bytes
MAX_VIDEO_LENGTH = 10 * 60  # 10 minutes in seconds

def validate_file_size(file):
    """Validate uploaded file size."""
    if file.size > MAX_FILE_SIZE:
        raise Exception(f"File size ({file.size / 1024 / 1024:.1f}MB) exceeds maximum limit (200MB)")

def validate_video_url(url: str):
    """Validate video URL format."""
    if not url:
        raise Exception("Please enter a video URL")
    
    valid_domains = ['loom.com', 'youtube.com', 'youtu.be']
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    
    # Check if it's a direct video link
    if any(url.lower().endswith(ext) for ext in valid_extensions):
        return
    
    # Check if it's from a supported platform
    if not any(domain in url.lower() for domain in valid_domains):
        raise Exception(
            "Unsupported video URL. Please use:\n"
            "- Direct video links (ending in .mp4, .mov, .avi, .mkv)\n"
            "- Loom videos\n"
            "- YouTube videos (public only)"
        )

# Main content in a container for better spacing
with st.container():
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📤 Upload Video", "🔗 Video URL"])

    with tab1:
        st.markdown("### Upload a Video File")
        st.markdown("""
            Upload a video file from your computer to analyze the speaker's accent.
            
            **Supported formats:** MP4, MOV, AVI, MKV
            
            **Tips for best results:**
            - Keep videos under 5 minutes
            - Ensure clear speech audio
            - Avoid background noise
        """)
        uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'mov', 'avi', 'mkv'])
        use_file = st.button("🔍 Analyze Uploaded Video", key="analyze_file")

    with tab2:
        st.markdown("### Enter Video URL")
        st.markdown("""
            Provide a URL to your video content.
            
            **Supported sources:**
            - Loom recordings
            - Direct MP4 links
            - YouTube videos (public only)
        """)
        url = st.text_input("Video URL:", placeholder="https://www.loom.com/share/... or https://example.com/video.mp4")
        use_url = st.button("🔍 Analyze URL", key="analyze_url")

def display_results(accent_info, confidence, summary):
    """Helper function to display analysis results."""
    st.markdown("### 📊 Analysis Results")
    
    # Display accent type
    st.markdown("<div class='accent-info'>", unsafe_allow_html=True)
    st.markdown(f"**Detected Accent:** {accent_info['accent']}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display confidence score
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Confidence Score:**")
        st.progress(confidence / 100)
    with col2:
        st.metric("", f"{confidence:.1f}%")
    
    # Display summary
    st.markdown("**Analysis Summary:**")
    st.info(summary)

# Handle file upload analysis
if use_file and uploaded_file is not None:
    try:
        # Validate file size first
        validate_file_size(uploaded_file)
        
        with st.spinner("📼 Processing video..."):
            # Save uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_path = Path(temp_dir) / "uploaded_video.mp4"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Convert to audio and analyze
            audio_path = download_video(str(temp_path))
            
            with st.spinner("🎯 Analyzing accent..."):
                accent_info, confidence, summary = analyze_accent(audio_path)
                
                if accent_info:
                    display_results(accent_info, confidence, summary)
                else:
                    st.error("Could not detect English accent. Please ensure clear English speech in the video.")
            
            # Cleanup
            cleanup_files(audio_path)
            cleanup_files(temp_path)
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("""
            **Please check:**
            - File size is under 200MB
            - Video file format is supported
            - File contains clear speech
            - Video length is reasonable (1-5 minutes recommended)
        """)

# Handle URL analysis
if use_url and url:
    try:
        # Validate URL first
        validate_video_url(url)
        
        with st.spinner("🌐 Downloading video..."):
            audio_path = download_video(url)
            
            with st.spinner("🎯 Analyzing accent..."):
                accent_info, confidence, summary = analyze_accent(audio_path)
                
                if accent_info:
                    display_results(accent_info, confidence, summary)
                else:
                    st.error("Could not detect English accent. Please ensure clear English speech in the video.")
            
            # Cleanup
            cleanup_files(audio_path)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("""
            **Please check:**
            - Video URL is publicly accessible
            - URL points to a supported platform
            - Video contains clear speech
            - Video length is reasonable (1-5 minutes recommended)
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Built with ❤️ by Donatus using Streamlit and AssemblyAI</p>
        <p style='font-size: 0.8em; color: #666;'>
            For hiring and recruitment purposes only. 
            Please ensure you have necessary permissions to analyze video content.
        </p>
    </div>
""", unsafe_allow_html=True) 