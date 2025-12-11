# API Endpoints Guide - Production

## Production URL
```
https://web-production-4f6b5.up.railway.app
```

---

## 1. Health Check Endpoint

### Request
```http
GET https://web-production-4f6b5.up.railway.app/health
```

### Sample Response JSON
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### cURL Example
```bash
curl https://web-production-4f6b5.up.railway.app/health
```

### Python Example
```python
import requests

response = requests.get("https://web-production-4f6b5.up.railway.app/health")
print(response.json())
# Output: {'status': 'healthy', 'model_loaded': True}
```

---

## 2. Root Endpoint

### Request
```http
GET https://web-production-4f6b5.up.railway.app/
```

### Sample Response JSON
```json
{
  "message": "Audio Transcription API",
  "status": "running",
  "supported_languages": ["en", "es"]
}
```

### cURL Example
```bash
curl https://web-production-4f6b5.up.railway.app/
```

---

## 3. Transcribe Audio Endpoint (Main)

### Request
```http
POST https://web-production-4f6b5.up.railway.app/transcribe
Content-Type: multipart/form-data
```

### Parameters
- `file` (required): Audio file (mp3, wav, m4a, flac, ogg, webm, mp4, mpeg)
- `language` (optional query parameter): `en` for English, `es` for Spanish. Omit for auto-detection.

### Sample Response JSON
```json
{
  "success": true,
  "transcription": "Thank you for calling. No group. This is Fania. How many help you? Hi, Tania. This is Anthony. I'm calling from added. I was looking to speak for Gina. Okay. Let me see if she's available. Do you mind holding this moment? Sure. No problem. Thank you for holding this, Gina. Hi, Gina. This is Anthony. I'm calling from added. You called today and the call got disconnected. I just wanted to check in with you. You were inquiring about the terminals and the offer that I discussed with you earlier.",
  "summary": "Call participants: Anthony, Fania. Topics discussed: order, shipment, payment, contract, service, meeting. Key decisions: go ahead and just hook them up and start using them now; give us one at no charge; do I just need to call you to hook them up or the pretty self explanatory for me to be able to hook.",
  "action_items": [
    {
      "assignee": "Fania",
      "description": "see if she's available",
      "speaker": "Anthony",
      "timestamp": 11.16,
      "date": null,
      "time": null
    },
    {
      "assignee": "Anthony",
      "description": "confirm that",
      "speaker": "Anthony",
      "timestamp": 138.56,
      "date": null,
      "time": null
    },
    {
      "assignee": "Anthony",
      "description": "just quickly ask my team to process that for you and you should be receiving that in three to four days",
      "speaker": "Anthony",
      "timestamp": 166.56,
      "date": "three to four days",
      "time": null
    },
    {
      "assignee": "Fania",
      "description": "be able to easily use them",
      "speaker": "Anthony",
      "timestamp": 189.56,
      "date": null,
      "time": null
    },
    {
      "assignee": "Anthony",
      "description": "process that from here",
      "speaker": "Anthony",
      "timestamp": 200.56,
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
      "speaker": "Fania",
      "text": "No group.",
      "start": 2.16,
      "end": 3.16
    },
    {
      "speaker": "Fania",
      "text": "This is Fania.",
      "start": 3.16,
      "end": 4.16
    },
    {
      "speaker": "Fania",
      "text": "How many help you?",
      "start": 4.16,
      "end": 5.16
    },
    {
      "speaker": "Fania",
      "text": "Hi, Tania.",
      "start": 5.16,
      "end": 6.16
    },
    {
      "speaker": "Anthony",
      "text": "This is Anthony.",
      "start": 6.16,
      "end": 7.16
    },
    {
      "speaker": "Anthony",
      "text": "I'm calling from added.",
      "start": 7.16,
      "end": 8.16
    },
    {
      "speaker": "Anthony",
      "text": "I was looking to speak for Gina.",
      "start": 8.16,
      "end": 10.16
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
      "speaker": "Fania",
      "start": 2.16,
      "end": 3.16,
      "text": "No group."
    },
    {
      "id": 2,
      "speaker": "Fania",
      "start": 3.16,
      "end": 4.16,
      "text": "This is Fania."
    },
    {
      "id": 3,
      "speaker": "Fania",
      "start": 4.16,
      "end": 5.16,
      "text": "How many help you?"
    },
    {
      "id": 4,
      "speaker": "Fania",
      "start": 5.16,
      "end": 6.16,
      "text": "Hi, Tania."
    },
    {
      "id": 5,
      "speaker": "Anthony",
      "start": 6.16,
      "end": 7.16,
      "text": "This is Anthony."
    },
    {
      "id": 6,
      "speaker": "Anthony",
      "start": 7.16,
      "end": 8.16,
      "text": "I'm calling from added."
    },
    {
      "id": 7,
      "speaker": "Anthony",
      "start": 8.16,
      "end": 10.16,
      "text": "I was looking to speak for Gina."
    }
  ],
  "metadata": {
    "filename": "test-audio.mp3",
    "file_size": 824301,
    "duration": 206.56,
    "speaker_diarization": false,
    "total_speakers": 2,
    "total_action_items": 5
  }
}
```

### cURL Examples

**Auto-detect language:**
```bash
curl -X POST "https://web-production-4f6b5.up.railway.app/transcribe" \
  -F "file=@your_audio.mp3"
```

**Specify English:**
```bash
curl -X POST "https://web-production-4f6b5.up.railway.app/transcribe?language=en" \
  -F "file=@your_audio.mp3"
```

**Specify Spanish:**
```bash
curl -X POST "https://web-production-4f6b5.up.railway.app/transcribe?language=es" \
  -F "file=@your_audio.mp3"
```

### Python Example
```python
import requests
import json

url = "https://web-production-4f6b5.up.railway.app/transcribe"

# Upload audio file
with open("audio.mp3", "rb") as audio_file:
    files = {"file": audio_file}
    params = {"language": "en"}  # Optional: "en" or "es"
    
    response = requests.post(url, files=files, params=params)
    
    if response.status_code == 200:
        result = response.json()
        
        # Pretty print the JSON
        print(json.dumps(result, indent=2))
        
        # Access specific fields
        print("\n=== SUMMARY ===")
        print(result["summary"])
        
        print("\n=== ACTION ITEMS ===")
        for i, item in enumerate(result["action_items"], 1):
            print(f"{i}. {item['assignee']}: {item['description']}")
            if item.get("date"):
                print(f"   Date: {item['date']}")
        
        print("\n=== SPEAKERS ===")
        speakers = set(s["speaker"] for s in result["transcription_with_speakers"])
        print(f"Participants: {', '.join(speakers)}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
```

### JavaScript/TypeScript Example
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://web-production-4f6b5.up.railway.app/transcribe?language=en', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Full Response:', JSON.stringify(data, null, 2));
  
  console.log('\n=== SUMMARY ===');
  console.log(data.summary);
  
  console.log('\n=== ACTION ITEMS ===');
  data.action_items.forEach((item, i) => {
    console.log(`${i + 1}. ${item.assignee}: ${item.description}`);
    if (item.date) {
      console.log(`   Date: ${item.date}`);
    }
  });
  
  console.log('\n=== SPEAKERS ===');
  const speakers = [...new Set(data.transcription_with_speakers.map(s => s.speaker))];
  console.log(`Participants: ${speakers.join(', ')}`);
})
.catch(error => console.error('Error:', error));
```

### React Example
```jsx
import React, { useState } from 'react';

function AudioTranscriber() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTranscribe = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        'https://web-production-4f6b5.up.railway.app/transcribe',
        {
          method: 'POST',
          body: formData
        }
      );

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="audio/*"
        onChange={(e) => handleTranscribe(e.target.files[0])}
      />
      
      {loading && <p>Processing...</p>}
      
      {result && (
        <div>
          <h2>Summary</h2>
          <p>{result.summary}</p>
          
          <h2>Action Items</h2>
          <ul>
            {result.action_items.map((item, i) => (
              <li key={i}>
                <strong>{item.assignee}:</strong> {item.description}
                {item.date && <span> (Due: {item.date})</span>}
              </li>
            ))}
          </ul>
          
          <h2>Transcription</h2>
          {result.transcription_with_speakers.map((seg, i) => (
            <p key={i}>
              <strong>{seg.speaker}:</strong> {seg.text}
            </p>
          ))}
        </div>
      )}
    </div>
  );
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

## Response Fields Explained

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether transcription was successful |
| `transcription` | string | Full transcription text without speaker labels |
| `summary` | string | AI-generated summary with participants, topics, and decisions |
| `action_items` | array | Extracted action items with assignees and dates |
| `language_detected` | string | Language detected by Whisper (e.g., "en", "es") |
| `language_requested` | string | Language requested or "auto" |
| `transcription_with_speakers` | array | Simplified format with speaker labels |
| `segments` | array | Detailed segments with IDs and timestamps |
| `metadata` | object | Additional metadata about the call |

### Action Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `assignee` | string | Person responsible (extracted name or "Speaker X") |
| `description` | string | What needs to be done |
| `speaker` | string | Who mentioned the action |
| `timestamp` | number | When it was mentioned (seconds) |
| `date` | string/null | Date mentioned (e.g., "three to four days") |
| `time` | string/null | Time mentioned (e.g., "2:00 PM") |

---

## Quick Test Script

Save this as `test_production.py`:

```python
import requests
import json

PRODUCTION_URL = "https://web-production-4f6b5.up.railway.app"

# Test health
print("Testing health endpoint...")
health = requests.get(f"{PRODUCTION_URL}/health")
print("Health:", json.dumps(health.json(), indent=2))

# Test transcription (replace with your audio file)
print("\nTesting transcription endpoint...")
with open("test-audio.mp3", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{PRODUCTION_URL}/transcribe", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("\n=== SUMMARY ===")
        print(result["summary"])
        print("\n=== ACTION ITEMS ===")
        for item in result["action_items"]:
            print(f"- {item['assignee']}: {item['description']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
```

Run with:
```bash
python test_production.py
```

