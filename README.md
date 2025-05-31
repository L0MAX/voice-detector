# Accent Detector

A web application that analyzes speaker accents from video content for hiring purposes. Built with Streamlit and AssemblyAI.

## Features

- Accepts video uploads and URLs (Loom, direct MP4 links, YouTube)
- Extracts audio from videos
- Detects and classifies English accents
- Provides confidence scores for accent detection
- Generates brief summaries of accent analysis

## Live Demo

Visit the live application at: [Your Streamlit App URL]

## Local Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd accent-detector
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
```bash
# On macOS
brew install ffmpeg

# On Ubuntu/Debian
sudo apt-get install ffmpeg

# On Windows
# Download from https://ffmpeg.org/download.html
```

5. Set up environment variables:
Create a `.env` file in the root directory and add your API keys:
```
ASSEMBLYAI_API_KEY=your_key_here
```

6. Run the application locally:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account

2. Visit [Streamlit Cloud](https://streamlit.io/cloud)

3. Click "New app" and select your forked repository

4. Set the following:
   - Main file path: `app.py`
   - Add your AssemblyAI API key as a secret:
     - Name: `ASSEMBLYAI_API_KEY`
     - Value: Your API key

5. Click "Deploy"

## Usage Tips

For best results:
- Use videos under 5 minutes
- Ensure clear speech audio
- Avoid background noise
- Use supported video formats (MP4, MOV, AVI, MKV)

## Supported Accents

The tool can detect and classify the following English accents:
- American
- British
- Australian
- Indian
- Canadian
- Irish
- Scottish
- And more...

## Technical Details

This application uses:
- Streamlit for the web interface
- AssemblyAI for speech recognition and accent detection
- FFmpeg for video processing
- Custom accent analysis algorithms

## Limitations

- Only processes public video URLs
- Requires clear audio quality
- Limited to English language accent detection
- Processing time depends on video length

## License

MIT License 