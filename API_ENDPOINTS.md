# API Endpoints Documentation

## Base URL
```
http://localhost:8000  (local)
https://your-railway-app.railway.app  (production)
```

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running and the model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Root Endpoint
**GET** `/`

Get basic API information.

**Response:**
```json
{
  "message": "Audio Transcription API",
  "status": "running",
  "supported_languages": ["en", "es"]
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

### 3. Transcribe Audio
**POST** `/transcribe`

Transcribe an audio file with speaker identification, summary, and action items extraction.

**Request:**
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `file` (required): Audio file (mp3, wav, m4a, flac, ogg, webm, mp4, mpeg)
  - `language` (optional): Language code (`en` for English, `es` for Spanish). Omit for auto-detection.

**Response:**
```json
{
  "success": true,
  "transcription": "Full transcription text...",
  "summary": "Call participants: Anthony, Fania. Topics discussed: order, shipment...",
  "action_items": [
    {
      "assignee": "Anthony",
      "description": "process that from here",
      "speaker": "Anthony",
      "timestamp": 166.6,
      "date": "three to four days",
      "time": null
    }
  ],
  "language_detected": "en",
  "language_requested": "auto",
  "transcription_with_speakers": [...],
  "segments": [...],
  "metadata": {...}
}
```

**Examples:**

**Using curl:**
```bash
# Auto-detect language
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3"

# Specify English
curl -X POST "http://localhost:8000/transcribe?language=en" \
  -F "file=@audio.mp3"

# Specify Spanish
curl -X POST "http://localhost:8000/transcribe?language=es" \
  -F "file=@audio.mp3"
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/transcribe"
files = {"file": open("audio.mp3", "rb")}
params = {"language": "en"}  # Optional

response = requests.post(url, files=files, params=params)
result = response.json()

print("Summary:", result["summary"])
print("Action Items:", result["action_items"])
```

**Using JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/transcribe?language=en', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Summary:', data.summary);
  console.log('Action Items:', data.action_items);
});
```

**Using JavaScript (axios):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

axios.post('http://localhost:8000/transcribe', formData, {
  params: { language: 'en' },
  headers: { 'Content-Type': 'multipart/form-data' }
})
.then(response => {
  console.log('Summary:', response.data.summary);
  console.log('Action Items:', response.data.action_items);
});
```

---

## Response Fields Explained

### Summary
Automatically generated summary containing:
- Call participants (extracted names)
- Topics discussed (order, shipment, payment, etc.)
- Key decisions made during the call

### Action Items
Array of actionable items extracted from the call:
- **assignee**: Person responsible (extracted name or "Speaker X")
- **description**: What needs to be done
- **speaker**: Who mentioned the action
- **timestamp**: When it was mentioned (seconds)
- **date**: Date mentioned (e.g., "three to four days", "end of this month")
- **time**: Time mentioned (e.g., "2:00 PM")

### Transcription with Speakers
Simplified format showing speaker and text:
```json
{
  "speaker": "Anthony",
  "text": "I will process that.",
  "start": 166.6,
  "end": 170.0
}
```

### Segments
Detailed format with segment IDs:
```json
{
  "id": 42,
  "speaker": "Anthony",
  "start": 166.6,
  "end": 170.0,
  "text": "I will process that."
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Unsupported file type. Allowed types: mp3, wav, m4a, flac, ogg, webm, mp4, mpeg"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Transcription failed: [error message]"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Model not loaded"
}
```

---

## Features

✅ **Speaker Identification**: Automatically identifies and names speakers from the call
✅ **Call Summary**: Generates intelligent summary with participants, topics, and decisions
✅ **Action Items**: Extracts actionable items with assignees and dates/times
✅ **Multi-language**: Supports English and Spanish (auto-detection)
✅ **Timestamps**: All segments include precise timestamps
✅ **Multiple Formats**: Supports various audio formats

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider adding rate limiting based on your needs.

---

## Notes

- First request after server startup may be slower as the model initializes
- Large audio files will take longer to process
- Speaker names are extracted from the transcription (e.g., "This is Anthony" → Speaker name: "Anthony")
- If no names are detected, speakers are labeled as "Speaker 1", "Speaker 2", etc.

