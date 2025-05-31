# Accent Detector

A web application that analyzes speaker accents from video URLs. This tool helps evaluate spoken English accents for hiring purposes.

## Features

- Accepts public video URLs (Loom or direct MP4 links)
- Extracts audio from videos
- Detects and classifies English accents
- Provides confidence scores for accent detection
- Generates brief summaries of accent analysis

## Setup

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

4. Set up environment variables:
Create a `.env` file in the root directory and add your API keys:
```
ASSEMBLYAI_API_KEY=your_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Open the application in your web browser (default: http://localhost:8501)
2. Paste a public video URL into the input field
3. Click "Analyze Accent" to process the video
4. View the results, including:
   - Detected accent classification
   - Confidence score
   - Brief analysis summary

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
- yt-dlp for video download and audio extraction
- Custom accent analysis algorithms

## Limitations

- Only processes public video URLs
- Requires clear audio quality for accurate detection
- Limited to English language accent detection
- Processing time depends on video length

## License

MIT License 