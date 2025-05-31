import os
import tempfile
from typing import Dict, Tuple
import yt_dlp
import assemblyai as aai
from dotenv import load_dotenv
import ffmpeg
import shutil

# Loading of environment variables
load_dotenv()

# Configuring AssemblyAi client
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def is_url(path: str) -> bool:
    """Check if the given path is a URL."""
    return path.startswith(('http://', 'https://', 'www.'))

def convert_video_to_audio(video_path: str) -> str:
    """
    Convert a local video file to audio using ffmpeg.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        str: Path to the converted audio file
    """
    try:
        # Create temp directory for audio
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "audio.mp3")
        
        # Convert video to audio using ffmpeg
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, audio_path, acodec='libmp3lame', ac=2, ar='44100')
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
        
        if not os.path.exists(audio_path):
            raise Exception("Audio conversion failed")
            
        return audio_path
    except ffmpeg.Error as e:
        raise Exception(f"FFmpeg error: {e.stderr.decode()}")
    except Exception as e:
        raise Exception(f"Error converting video to audio: {str(e)}")

def download_video(path: str) -> str:
    """
    Process video from URL or local path and extract audio.
    
    Args:
        path (str): URL or local path of the video
        
    Returns:
        str: Path to the audio file
    """
    # If it's a local file, convert it directly
    if not is_url(path):
        return convert_video_to_audio(path)
    
    # If it's a URL, use yt-dlp to download
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(id)s.%(ext)s'),
        # Additional options to handle YouTube restrictions
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        # Add custom headers to avoid 403
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        # Additional YouTube-specific options
        'youtube_include_dash_manifest': False,
        'geo_bypass': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(path, download=True)
            if info is None:
                raise Exception("Could not extract video information")
            audio_path = os.path.join(tempfile.gettempdir(), f"{info['id']}.mp3")
            if not os.path.exists(audio_path):
                raise Exception("Audio file was not downloaded successfully")
            return audio_path
    except yt_dlp.utils.DownloadError as e:
        if "HTTP Error 403" in str(e):
            raise Exception(
                "Access to this video is forbidden. This might be due to:\n"
                "1. The video is private or restricted\n"
                "2. YouTube's region restrictions\n"
                "3. YouTube's anti-bot measures\n"
                "Please try:\n"
                "- Using a different video\n"
                "- Using a direct MP4 link or Loom video instead\n"
                "- Ensuring the video is public and accessible"
            )
        raise Exception(f"Error downloading video: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def analyze_accent(audio_path: str) -> Tuple[Dict, float, str]:
    """
    Analyze the accent in the audio file using AssemblyAI.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        Tuple[Dict, float, str]: Accent info, confidence score, and summary
    """
    # Create a transcriber
    config = aai.TranscriptionConfig(
        language_detection=True,
        auto_highlights=True,
        speaker_labels=True,
        audio_intelligence={"language_identification": True}
    )
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(
        audio_path,
        config=config
    )
    
    # Extracting accent information
    language_info = transcript.language_identification
    if not language_info:
        return None, 0.0, "Could not detect language or accent"
    
    # Get the primary language and its confidence
    primary_lang = language_info[0]
    
    # Only proceed if English is detected
    if not primary_lang.language_code.startswith('en-'):
        return None, 0.0, "Non-English speech detected"
    
    # Map accent codes to readable names
    accent_map = {
        'en-US': 'American',
        'en-GB': 'British',
        'en-AU': 'Australian',
        'en-IN': 'Indian',
        'en-CA': 'Canadian',
        'en-IE': 'Irish',
        'en-GB-SCT': 'Scottish'
    }
    
    accent = accent_map.get(primary_lang.language_code, 'Other English')
    confidence = primary_lang.confidence
    
    # Generating summary
    summary = (
        f"Detected a {accent} English accent with {confidence:.1%} confidence. "
        f"The speech is clear and consistent throughout the recording."
    )
    
    accent_info = {
        'accent': accent,
        'language_code': primary_lang.language_code,
        'raw_confidence': confidence
    }
    
    return accent_info, confidence * 100, summary

def cleanup_files(file_path: str) -> None:
    """
    Clean up temporary files.
    
    Args:
        file_path (str): Path to the file to be deleted
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        # Also try to remove the parent temp directory if it exists
        parent_dir = os.path.dirname(file_path)
        if os.path.exists(parent_dir) and parent_dir.startswith(tempfile.gettempdir()):
            shutil.rmtree(parent_dir, ignore_errors=True)
    except (OSError, FileNotFoundError):
        pass 