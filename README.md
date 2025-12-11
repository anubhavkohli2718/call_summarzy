# Audio Transcription API

A FastAPI-based backend service that transcribes audio files using OpenAI's Whisper model. Supports automatic language detection for English and Spanish, or explicit language specification.

## Features

- 🎤 Audio transcription using self-hosted Whisper model
- 🌍 Auto-detection of English and Spanish languages
- 📝 Manual language specification (en/es)
- 🚀 Ready for Railway deployment
- 📊 Detailed transcription with timestamps and segments

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

### Transcribe Audio
```
POST /transcribe
```

**Parameters:**
- `file` (multipart/form-data): Audio file to transcribe
- `language` (optional query parameter): Language code - `en` for English, `es` for Spanish. If omitted, language will be auto-detected.

**Response:**
```json
{
  "success": true,
  "transcription": "Full transcription text...",
  "language_detected": "en",
  "language_requested": "auto",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.2,
      "text": "Segment text..."
    }
  ],
  "metadata": {
    "filename": "audio.mp3",
    "file_size": 123456,
    "duration": 30.5
  }
}
```

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
   - No additional environment variables are required for basic operation

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

