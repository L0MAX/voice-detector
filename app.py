import streamlit as st
from utils import download_video, analyze_accent, cleanup_files
import os
import tempfile
from pathlib import Path

# my page config
st.set_page_config(
    page_title="Accent Detector",
    page_icon="🎙️",
    layout="centered"
)

# CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# the title and description
st.title("🎙️ Donatus Voice Accent Detector")
st.markdown("""
    Analyze speaker's English accent from a video. 
    
    **Two ways to input your video:**
    1. Upload a video file from your computer
    2. Provide a video URL
""")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload File", "Video URL"])

with tab1:
    st.markdown("### Upload Video File")
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'mov', 'avi', 'mkv'])
    use_file = st.button("Analyze Uploaded File")

with tab2:
    st.markdown("### Video URL")
    # Example expandable section
    with st.expander("See supported URL types"):
        st.markdown("""
            **Supported URL types:**
            1. Direct MP4 links (recommended): `https://example.com/video.mp4`
            2. Loom videos: `https://www.loom.com/share/...`
            3. YouTube videos (may be restricted)
            
            **Tips for direct MP4 links:**
            - Look for URLs that end with `.mp4`
            - Use your own hosted videos if possible
            - Check video hosting platforms that provide direct links
        """)
    
    url = st.text_input(
        "Enter video URL:", 
        placeholder="https://example.com/video.mp4 or https://www.loom.com/share/..."
    )
    use_url = st.button("Analyze URL")

# Function to process the analysis
def process_accent_analysis(audio_path):
    with st.spinner("Analyzing accent..."):
        # code to analyze the accent
        accent_info, confidence, summary = analyze_accent(audio_path)
        
        if accent_info:
            # code to display the results
            st.markdown("### Results")
            
            # type of the accent
            st.markdown(f"**Detected Accent:** {accent_info['accent']}")
            
            # the confidence score with progress bar
            st.markdown("**Confidence Score:**")
            st.progress(confidence / 100)
            st.text(f"{confidence:.1f}%")
            
            # summary box
            st.markdown("**Analysis Summary:**")
            st.info(summary)
        else:
            st.error("Could not detect English accent in the video. Please ensure the video contains clear English speech.")

# Handle file upload analysis
if use_file and uploaded_file is not None:
    try:
        with st.spinner("Processing uploaded file..."):
            # Save uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_path = Path(temp_dir) / "uploaded_video.mp4"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Convert to audio and analyze
            audio_path = download_video(str(temp_path))
            process_accent_analysis(audio_path)
            
            # Cleanup
            cleanup_files(audio_path)
            cleanup_files(temp_path)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("""
            Please ensure:
            - The video file is in a supported format
            - The video contains clear speech
            - The video is not too long (recommended: 1-5 minutes)
        """)

# Handle URL analysis
if use_url and url:
    try:
        with st.spinner("Downloading and processing video..."):
            # downloading video and extracting audio
            audio_path = download_video(url)
            process_accent_analysis(audio_path)
            
            # files cleanup
            cleanup_files(audio_path)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("""
            Please ensure:
            - The video URL is publicly accessible
            - The video contains clear speech
            - The video is not too long (recommended: 1-5 minutes)
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        Built with ❤️ by Donatus using Streamlit and AssemblyAI
    </div>
""", unsafe_allow_html=True) 