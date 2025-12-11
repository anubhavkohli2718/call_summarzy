# Quick Start Guide

## API Endpoints Quick Reference

### Base URL
- **Local:** `http://localhost:8000`
- **Production:** Your Railway deployment URL

---

## 1. Health Check
```bash
GET /health
```

**Quick Test:**
```bash
curl http://localhost:8000/health
```

---

## 2. Transcribe Audio
```bash
POST /transcribe
```

### Basic Usage (Auto-detect language)
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@your_audio.mp3"
```

### With Language Specification
```bash
# English
curl -X POST "http://localhost:8000/transcribe?language=en" \
  -F "file=@your_audio.mp3"

# Spanish
curl -X POST "http://localhost:8000/transcribe?language=es" \
  -F "file=@your_audio.mp3"
```

### Python Example
```python
import requests

url = "http://localhost:8000/transcribe"
files = {"file": open("audio.mp3", "rb")}
response = requests.post(url, files=files)

result = response.json()
print("Summary:", result["summary"])
print("Action Items:", result["action_items"])
```

### JavaScript Example
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/transcribe', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Summary:', data.summary);
  console.log('Action Items:', data.action_items);
  console.log('Speakers:', data.transcription_with_speakers);
});
```

---

## Response Structure

```json
{
  "success": true,
  "transcription": "Full text...",
  "summary": "Call summary...",
  "action_items": [
    {
      "assignee": "Speaker Name",
      "description": "Action description",
      "speaker": "Speaker Name",
      "timestamp": 123.45,
      "date": "three to four days",
      "time": null
    }
  ],
  "transcription_with_speakers": [...],
  "segments": [...],
  "metadata": {...}
}
```

---

## Key Features

✅ **Speaker Names**: Automatically extracts names (e.g., "Anthony", "Fania")
✅ **Call Summary**: AI-generated summary with participants and topics
✅ **Action Items**: Extracts tasks with assignees and dates
✅ **Timestamps**: Precise timing for each segment
✅ **Multi-language**: English and Spanish support

---

## Supported Audio Formats

- MP3, WAV, M4A, FLAC, OGG, WebM, MP4, MPEG

---

For detailed documentation, see [API_ENDPOINTS.md](./API_ENDPOINTS.md)

