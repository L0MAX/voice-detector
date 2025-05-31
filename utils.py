import os
import tempfile
from typing import Dict, Tuple
import yt_dlp
import assemblyai as aai
from dotenv import load_dotenv
import ffmpeg
import shutil
import mimetypes

# Try to import magic, but don't fail if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

# Loading of environment variables
load_dotenv()

# Check for API key
if not os.getenv("ASSEMBLYAI_API_KEY"):
    raise Exception(
        "AssemblyAI API key not found. Please set the ASSEMBLYAI_API_KEY environment variable."
    )

# Configuring AssemblyAI client
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def is_url(path: str) -> bool:
    """Check if the given path is a URL."""
    return path.startswith(('http://', 'https://', 'www.'))

def get_mime_type(file_path: str) -> str:
    """
    Get MIME type of a file using multiple methods.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: MIME type of the file
    """
    if MAGIC_AVAILABLE:
        return magic.from_file(file_path, mime=True)
    
    # Fallback to mimetypes library
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type
    
    # If all else fails, guess based on extension
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
    }
    return mime_map.get(ext, 'application/octet-stream')

def validate_video_file(file_path: str) -> None:
    """
    Validate that the file is a video file.
    
    Args:
        file_path (str): Path to the file
        
    Raises:
        Exception: If file is not a valid video
    """
    if not os.path.exists(file_path):
        raise Exception("File not found")
        
    # Get mime type
    mime_type = get_mime_type(file_path)
    
    if not mime_type.startswith('video/'):
        raise Exception(f"Invalid file type: {mime_type}. Please upload a video file.")

def convert_video_to_audio(video_path: str) -> str:
    """
    Convert a local video file to audio using ffmpeg.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        str: Path to the converted audio file
    """
    try:
        # Validate video file first
        validate_video_file(video_path)
        
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
        error_message = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
        if "Invalid data found when processing input" in error_message:
            raise Exception("Invalid or corrupted video file")
        raise Exception(f"FFmpeg error: {error_message}")
    except Exception as e:
        raise Exception(f"Error converting video to audio: {str(e)}")

def download_video(path: str) -> str:
    """
    Process video from URL or local path and extract audio.
    
    Args:
        path (str): URL or local path of the video
        
    Returns:
        str: Path to the audio file
    
    Raises:
        Exception: If video processing fails
    """
    if not path:
        raise Exception("No video path or URL provided")
        
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
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'youtube_include_dash_manifest': False,
        'geo_bypass': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(path, download=True)
            if info is None:
                raise Exception("Could not extract video information")
                
            # Check video duration if available
            if 'duration' in info and info['duration'] > 600:  # 10 minutes
                raise Exception("Video is too long. Please use videos under 10 minutes.")
                
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
        
    Raises:
        Exception: If accent analysis fails
    """
    if not os.path.exists(audio_path):
        raise Exception("Audio file not found")
        
    try:
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
        
        # Check if transcription was successful
        if not transcript or not transcript.language_identification:
            return None, 0.0, "Could not detect language or accent. Please ensure clear speech in the video."
        
        # Get the primary language and its confidence
        primary_lang = transcript.language_identification[0]
        
        # Only proceed if English is detected
        if not primary_lang.language_code.startswith('en-'):
            return None, 0.0, f"Non-English speech detected ({primary_lang.language_code})"
        
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
        
        # Generate detailed summary
        clarity = "very clear" if confidence > 0.9 else "clear" if confidence > 0.7 else "moderate"
        summary = (
            f"Detected a {accent} English accent with {confidence:.1%} confidence. "
            f"The speech quality is {clarity}. "
            f"This analysis is based on the speaker's pronunciation patterns and speech characteristics."
        )
        
        accent_info = {
            'accent': accent,
            'language_code': primary_lang.language_code,
            'raw_confidence': confidence
        }
        
        return accent_info, confidence * 100, summary
        
    except Exception as e:
        raise Exception(f"Error analyzing accent: {str(e)}")

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