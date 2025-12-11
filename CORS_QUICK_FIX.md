# CORS Error - Quick Fix Guide

## The Problem
```
Access to fetch at 'https://web-production-4f6b5.up.railway.app/transcribe' 
from origin 'http://localhost:61063' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present
```

## Solution

### Step 1: Redeploy on Railway
The CORS configuration has been updated. You need to redeploy:

1. Go to Railway dashboard
2. Click on your service
3. Click "Redeploy" or trigger a new deployment
4. Wait for deployment to complete

### Step 2: Test CORS Headers

After redeployment, test if CORS is working:

```bash
# Test OPTIONS preflight
curl -X OPTIONS https://web-production-4f6b5.up.railway.app/transcribe \
  -H "Origin: http://localhost:61063" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

You should see headers like:
```
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: POST, OPTIONS
```

### Step 3: Update Your Frontend Code

Make sure your fetch request includes `mode: 'cors'`:

```javascript
fetch('https://web-production-4f6b5.up.railway.app/transcribe', {
  method: 'POST',
  mode: 'cors',  // ← Important!
  body: formData
})
```

**Important:** Don't set `Content-Type` header when using FormData - the browser sets it automatically.

### Step 4: Test in Browser

Open browser console and test:

```javascript
// Simple test
fetch('https://web-production-4f6b5.up.railway.app/health', {
  method: 'GET',
  mode: 'cors'
})
.then(r => r.json())
.then(console.log)
```

If this works, CORS is fixed!

## What Was Fixed

1. ✅ CORS middleware configured to allow all origins
2. ✅ Explicit OPTIONS handler added for preflight requests
3. ✅ Proper CORS headers in responses

## Still Having Issues?

1. **Clear browser cache** - Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
2. **Check Railway logs** - Look for startup errors
3. **Verify deployment** - Make sure latest code is deployed
4. **Test with curl** - Verify API works without browser

## Example Working Code

```javascript
const formData = new FormData();
formData.append('file', audioFile);

const response = await fetch(
  'https://web-production-4f6b5.up.railway.app/transcribe',
  {
    method: 'POST',
    mode: 'cors',  // Required
    body: formData  // Don't set Content-Type header
  }
);

const result = await response.json();
console.log('Summary:', result.summary);
console.log('Action Items:', result.action_items);
```

