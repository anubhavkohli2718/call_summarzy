# Production Deployment Guide

## Production URL
```
https://web-production-4f6b5.up.railway.app
```

## API Endpoints

### Health Check
```bash
curl https://web-production-4f6b5.up.railway.app/health
```

### Transcribe Audio
```bash
curl -X POST "https://web-production-4f6b5.up.railway.app/transcribe" \
  -F "file=@your_audio.mp3"
```

## Usage Examples

### Python
```python
import requests

PRODUCTION_URL = "https://web-production-4f6b5.up.railway.app"

# Transcribe audio
files = {"file": open("audio.mp3", "rb")}
response = requests.post(f"{PRODUCTION_URL}/transcribe", files=files)

if response.status_code == 200:
    result = response.json()
    print("Summary:", result["summary"])
    print("Action Items:", result["action_items"])
    print("Speakers:", [s["speaker"] for s in result["transcription_with_speakers"]])
else:
    print("Error:", response.status_code, response.text)
```

### JavaScript/TypeScript
```javascript
const PRODUCTION_URL = "https://web-production-4f6b5.up.railway.app";

async function transcribeAudio(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(`${PRODUCTION_URL}/transcribe`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    console.log('Summary:', data.summary);
    console.log('Action Items:', data.action_items);
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### React Example
```jsx
import React, { useState } from 'react';

function AudioTranscriber() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://web-production-4f6b5.up.railway.app/transcribe', {
        method: 'POST',
        body: formData
      });

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
      <input type="file" accept="audio/*" onChange={handleFileUpload} />
      {loading && <p>Processing...</p>}
      {result && (
        <div>
          <h3>Summary</h3>
          <p>{result.summary}</p>
          <h3>Action Items</h3>
          <ul>
            {result.action_items.map((item, i) => (
              <li key={i}>
                <strong>{item.assignee}:</strong> {item.description}
                {item.date && <span> (Due: {item.date})</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

### cURL with Language
```bash
# English
curl -X POST "https://web-production-4f6b5.up.railway.app/transcribe?language=en" \
  -F "file=@audio.mp3"

# Spanish
curl -X POST "https://web-production-4f6b5.up.railway.app/transcribe?language=es" \
  -F "file=@audio.mp3"
```

## Testing the Production API

### Quick Test Script
```python
import requests

url = "https://web-production-4f6b5.up.railway.app"

# Test health
health = requests.get(f"{url}/health")
print("Health:", health.json())

# Test transcription (replace with your audio file)
# files = {"file": open("test-audio.mp3", "rb")}
# response = requests.post(f"{url}/transcribe", files=files)
# print("Transcription:", response.json())
```

## Response Format

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
  "transcription_with_speakers": [...],
  "segments": [...],
  "metadata": {...}
}
```

## Notes

- First request may take longer as the model initializes
- Large audio files will take more time to process
- The API supports CORS for web applications
- Rate limiting: Currently no limits, but monitor usage

## Error Handling

```python
import requests

try:
    response = requests.post(
        "https://web-production-4f6b5.up.railway.app/transcribe",
        files={"file": open("audio.mp3", "rb")},
        timeout=300  # 5 minutes for large files
    )
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    print("Request timed out. File may be too large.")
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
```

