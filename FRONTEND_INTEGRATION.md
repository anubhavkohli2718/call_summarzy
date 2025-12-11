# Frontend Integration Guide

## CORS Configuration

The API is configured to accept requests from any origin. If you're still getting CORS errors:

1. **Redeploy on Railway** - The latest CORS configuration needs to be deployed
2. **Check browser console** - Look for specific CORS error messages
3. **Verify API is running** - Test with curl first

## Frontend Examples

### React/Next.js Example

```jsx
import React, { useState } from 'react';

function AudioTranscriber() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'https://web-production-4f6b5.up.railway.app';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/transcribe`, {
        method: 'POST',
        mode: 'cors',  // Important for CORS
        body: formData,
        // Don't set Content-Type header - browser will set it automatically with boundary
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="audio/*"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit" disabled={!file || loading}>
          {loading ? 'Transcribing...' : 'Transcribe'}
        </button>
      </form>

      {error && <div style={{color: 'red'}}>Error: {error}</div>}

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

export default AudioTranscriber;
```

### Vanilla JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Audio Transcription</title>
</head>
<body>
  <input type="file" id="audioFile" accept="audio/*">
  <button onclick="transcribe()">Transcribe</button>
  <div id="result"></div>

  <script>
    const API_URL = 'https://web-production-4f6b5.up.railway.app';

    async function transcribe() {
      const fileInput = document.getElementById('audioFile');
      const file = fileInput.files[0];
      
      if (!file) {
        alert('Please select an audio file');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch(`${API_URL}/transcribe`, {
          method: 'POST',
          mode: 'cors',
          body: formData
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResult(result);
      } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').innerHTML = 
          `<p style="color: red;">Error: ${error.message}</p>`;
      }
    }

    function displayResult(result) {
      const resultDiv = document.getElementById('result');
      resultDiv.innerHTML = `
        <h2>Summary</h2>
        <p>${result.summary}</p>
        
        <h2>Action Items</h2>
        <ul>
          ${result.action_items.map(item => `
            <li>
              <strong>${item.assignee}:</strong> ${item.description}
              ${item.date ? ` (Due: ${item.date})` : ''}
            </li>
          `).join('')}
        </ul>
        
        <h2>Transcription</h2>
        ${result.transcription_with_speakers.map(seg => `
          <p><strong>${seg.speaker}:</strong> ${seg.text}</p>
        `).join('')}
      `;
    }
  </script>
</body>
</html>
```

### Vue.js Example

```vue
<template>
  <div>
    <input type="file" @change="handleFileChange" accept="audio/*">
    <button @click="transcribe" :disabled="!file || loading">
      {{ loading ? 'Transcribing...' : 'Transcribe' }}
    </button>

    <div v-if="error" style="color: red;">Error: {{ error }}</div>

    <div v-if="result">
      <h2>Summary</h2>
      <p>{{ result.summary }}</p>

      <h2>Action Items</h2>
      <ul>
        <li v-for="(item, i) in result.action_items" :key="i">
          <strong>{{ item.assignee }}:</strong> {{ item.description }}
          <span v-if="item.date"> (Due: {{ item.date }})</span>
        </li>
      </ul>

      <h2>Transcription</h2>
      <p v-for="(seg, i) in result.transcription_with_speakers" :key="i">
        <strong>{{ seg.speaker }}:</strong> {{ seg.text }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      file: null,
      result: null,
      loading: false,
      error: null,
      API_URL: 'https://web-production-4f6b5.up.railway.app'
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    async transcribe() {
      if (!this.file) return;

      this.loading = true;
      this.error = null;

      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const response = await fetch(`${this.API_URL}/transcribe`, {
          method: 'POST',
          mode: 'cors',
          body: formData
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        this.result = await response.json();
      } catch (error) {
        this.error = error.message;
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## Important Notes

1. **Don't set Content-Type header** - When using FormData, let the browser set it automatically
2. **Use `mode: 'cors'`** - Explicitly enable CORS in fetch requests
3. **Handle errors** - Always wrap API calls in try-catch
4. **Show loading state** - Audio transcription can take time

## Testing CORS

Test if CORS is working:

```javascript
// In browser console
fetch('https://web-production-4f6b5.up.railway.app/health', {
  method: 'GET',
  mode: 'cors'
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

If this works, CORS is configured correctly.

## Common CORS Errors

1. **"No 'Access-Control-Allow-Origin' header"** - Server needs redeployment
2. **"Preflight request failed"** - OPTIONS request not handled (should be fixed now)
3. **"Credentials not allowed"** - Remove `credentials: 'include'` if not using cookies

