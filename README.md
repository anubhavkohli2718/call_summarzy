# Audio Transcription API

A FastAPI-based backend service that transcribes audio files using OpenAI's Whisper model. Supports automatic language detection for English and Spanish, or explicit language specification.

## Features

- 🎤 Audio transcription using self-hosted Whisper model
- 🌍 Auto-detection of English and Spanish languages
- 📝 Manual language specification (en/es)
- 🎯 Speaker diarization (identifies different speakers)
- 🚀 Ready for Railway deployment
- 📊 Detailed transcription with timestamps and segments
- 📋 JSON output with speaker labels for each segment

## Supported Audio Formats

- MP3
- WAV
- M4A
- FLAC
- OGG
- WebM
- MP4
- MPEG

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API and whether the model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Root Endpoint
```
GET /
```
Returns basic API information.

**Response:**
```json
{
  "message": "Audio Transcription API",
  "status": "running",
  "supported_languages": ["en", "es"]
}
```

### Transcribe Audio
```
POST /transcribe
```

**Parameters:**
- `file` (multipart/form-data, required): Audio file to transcribe
- `language` (optional query parameter): Language code - `en` for English, `es` for Spanish. If omitted, language will be auto-detected.

**Response:**
```json
{
  "success": true,
  "transcription": "Full transcription text...",
  "summary": "Call participants: Anthony, Fania. Topics discussed: order, shipment, payment. Key decisions: process order, ship in 3-4 days.",
  "action_items": [
    {
      "assignee": "Anthony",
      "description": "process that from here",
      "speaker": "Anthony",
      "timestamp": 166.6,
      "date": "three to four days",
      "time": null
    },
    {
      "assignee": "Fania",
      "description": "call you to set those up",
      "speaker": "Fania",
      "timestamp": 189.6,
      "date": null,
      "time": null
    }
  ],
  "language_detected": "en",
  "language_requested": "auto",
  "transcription_with_speakers": [
    {
      "speaker": "Fania",
      "text": "Thank you for calling.",
      "start": 0.0,
      "end": 2.16
    },
    {
      "speaker": "Anthony",
      "text": "Hi, this is Anthony.",
      "start": 6.0,
      "end": 8.5
    }
  ],
  "segments": [
    {
      "id": 0,
      "speaker": "Fania",
      "start": 0.0,
      "end": 2.16,
      "text": "Thank you for calling."
    },
    {
      "id": 1,
      "speaker": "Anthony",
      "start": 6.0,
      "end": 8.5,
      "text": "Hi, this is Anthony."
    }
  ],
  "metadata": {
    "filename": "audio.mp3",
    "file_size": 123456,
    "duration": 206.56,
    "speaker_diarization": false,
    "total_speakers": 2,
    "total_action_items": 5
  }
}
```

**Response Fields:**
- `success`: Boolean indicating if transcription was successful
- `transcription`: Full transcription text without speaker labels
- `summary`: AI-generated summary of the call including participants, topics, and key decisions
- `action_items`: Array of action items extracted from the call with:
  - `assignee`: Person responsible for the action (extracted name or "Speaker X")
  - `description`: Description of the action item
  - `speaker`: Speaker who mentioned the action
  - `timestamp`: Time in seconds when action was mentioned
  - `date`: Date mentioned (if any, e.g., "three to four days", "end of this month")
  - `time`: Time mentioned (if any, e.g., "2:00 PM")
- `language_detected`: Language detected by Whisper
- `language_requested`: Language requested or "auto"
- `transcription_with_speakers`: Simplified array with speaker labels
- `segments`: Detailed segments with IDs and timestamps
- `metadata`: Additional metadata about the call

## Local Development

### Prerequisites

- Python 3.9 or higher
- FFmpeg installed on your system

**Installing FFmpeg:**
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd audio_Call_ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Testing the API

Using curl:
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@your_audio_file.mp3" \
  -F "language=en"
```

Using Python:
```python
import requests

url = "http://localhost:8000/transcribe"
files = {"file": open("audio.mp3", "rb")}
params = {"language": "en"}  # Optional

response = requests.post(url, files=files, params=params)
print(response.json())
```

## Railway Deployment

### Prerequisites

- Railway account
- Railway CLI (optional, can use web interface)

### Deployment Steps

1. **Create a new Railway project:**
   - Go to [Railway](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo" or "Empty Project"

2. **Configure the project:**
   - Railway will automatically detect the `Procfile` and `requirements.txt`
   - The `railway.json` file provides additional configuration

3. **Set environment variables (if needed):**
   - Railway will automatically set the `PORT` environment variable
   - For speaker diarization: Set `HF_TOKEN` with your Hugging Face token
     - Get a token from [Hugging Face](https://huggingface.co/settings/tokens)
     - Accept the terms for [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - Note: Without `HF_TOKEN`, the API will use a fallback method to assign speakers

4. **Deploy:**
   - If using GitHub, push your code and Railway will auto-deploy
   - If using CLI: `railway up`

### Important Notes for Railway

- The Whisper model will be downloaded on first startup (this may take a few minutes)
- The `base` model is used by default (good balance of speed and accuracy)
- For faster transcription, consider using `tiny` or `small` models
- For better accuracy, consider using `medium` or `large` models
- Model size affects memory requirements and startup time

### Changing the Whisper Model

To use a different model size, edit `main.py` and change:
```python
whisper_model = whisper.load_model("base")
```

Available models (from smallest to largest):
- `tiny` - Fastest, least accurate
- `base` - Good balance (default)
- `small` - Better accuracy
- `medium` - High accuracy
- `large` - Best accuracy, slowest

## Model Information

The Whisper model will be automatically downloaded on first use. The model files are cached locally, so subsequent startups will be faster.

- **Model Size**: ~150MB (base model)
- **Supported Languages**: 99+ languages (auto-detection)
- **Primary Focus**: English and Spanish (as specified)

## Performance Considerations

- First request after startup may be slower as the model initializes
- Transcription speed depends on:
  - Audio file length
  - Model size selected
  - Server CPU/RAM resources
- For production, consider:
  - Using a larger Railway instance
  - Implementing request queuing for high traffic
  - Caching frequently transcribed content

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file type, invalid language)
- `500`: Server error (transcription failure)
- `503`: Service unavailable (model not loaded)

## License

MIT License

## Support

For issues or questions, please open an issue on the repository.

