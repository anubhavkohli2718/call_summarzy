# Troubleshooting Guide

## 502 Bad Gateway Error

**Error:** `POST https://web-production-4f6b5.up.railway.app/transcribe net::ERR_FAILED 502 (Bad Gateway)`

### What This Means
The server is down, crashed, or not responding properly. This is different from CORS - the server isn't even reachable.

### Solutions

#### 1. Check Railway Deployment Status
1. Go to Railway dashboard
2. Check if your service is running (green status)
3. Look at the latest deployment logs
4. Check for any error messages

#### 2. Restart/Redeploy Service
1. In Railway dashboard, click on your service
2. Click "Redeploy" or "Restart"
3. Wait for deployment to complete (~2-3 minutes)

#### 3. Check Railway Logs
Look for errors like:
- FFmpeg not found
- Model loading errors
- Port binding issues
- Memory errors

#### 4. Verify Health Endpoint
```bash
curl https://web-production-4f6b5.up.railway.app/health
```

If this returns 502, the server is definitely down.

#### 5. Common Causes
- **FFmpeg missing** - Check if FFmpeg is installed (should be fixed with nixpacks.toml)
- **Model download failed** - Whisper model failed to download
- **Memory limit** - Server ran out of memory
- **Port conflict** - Port $PORT not set correctly
- **Crash on startup** - Check logs for Python errors

## CORS Error

**Error:** `No 'Access-Control-Allow-Origin' header is present`

### Solutions

1. **Redeploy Railway** - Latest CORS config needs to be deployed
2. **Clear browser cache** - Hard refresh (Ctrl+Shift+R)
3. **Check OPTIONS request** - Test preflight request:
   ```bash
   curl -X OPTIONS https://web-production-4f6b5.up.railway.app/transcribe \
     -H "Origin: http://localhost:61063" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```

## Flutter/Dart Specific Issues

### 502 Error in Flutter Web
1. Check if server is running (test with curl)
2. Verify Railway deployment is successful
3. Check Railway logs for crashes
4. Restart Railway service

### CORS in Flutter Web
1. Make sure Railway has latest code deployed
2. Use proper headers in http request
3. Don't manually set Content-Type for multipart

### File Upload Issues
```dart
// Correct way
var request = http.MultipartRequest('POST', uri);
request.files.add(await http.MultipartFile.fromPath('file', file.path));

// Don't manually set Content-Type header
```

## Quick Diagnostic Steps

1. **Test Health Endpoint**
   ```bash
   curl https://web-production-4f6b5.up.railway.app/health
   ```
   Expected: `{"status":"healthy","model_loaded":true}`

2. **Test Root Endpoint**
   ```bash
   curl https://web-production-4f6b5.up.railway.app/
   ```
   Expected: API info JSON

3. **Test OPTIONS (CORS)**
   ```bash
   curl -X OPTIONS https://web-production-4f6b5.up.railway.app/transcribe \
     -H "Origin: http://localhost:61063" \
     -v
   ```
   Expected: CORS headers in response

4. **Check Railway Logs**
   - Go to Railway dashboard
   - Click on your service
   - View "Logs" tab
   - Look for errors or warnings

## Server Status Check

Run this to check server status:

```bash
# Health check
curl -s https://web-production-4f6b5.up.railway.app/health | python3 -m json.tool

# If 502, server is down
# If 200, server is up but might have other issues
```

## After Fixing

Once server is back up:
1. Test health endpoint
2. Test transcription with curl
3. Test from Flutter app
4. Check browser console for any remaining errors

