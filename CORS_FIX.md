# CORS Configuration Fix

## Issue
CORS (Cross-Origin Resource Sharing) errors when accessing the API from a frontend application.

## Solution

The CORS middleware is already configured in `main.py`, but if you're still getting errors, try these solutions:

### Option 1: Verify CORS is Working

Test the API with a preflight request:

```bash
curl -X OPTIONS https://web-production-4f6b5.up.railway.app/transcribe \
  -H "Origin: http://localhost:61063" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

You should see CORS headers in the response.

### Option 2: Update CORS Configuration (if needed)

If you want to restrict to specific origins, update `main.py`:

```python
# For specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:61063",
        "http://localhost:3000",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### Option 3: Frontend Configuration

Make sure your frontend is sending requests correctly:

**JavaScript/Fetch:**
```javascript
fetch('https://web-production-4f6b5.up.railway.app/transcribe', {
  method: 'POST',
  mode: 'cors',  // Important!
  credentials: 'include',  // If using cookies
  headers: {
    // Don't set Content-Type for FormData - browser will set it automatically
  },
  body: formData
})
```

**Axios:**
```javascript
axios.post('https://web-production-4f6b5.up.railway.app/transcribe', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  },
  withCredentials: true  // If using cookies
})
```

### Option 4: Test CORS Headers

Check if CORS headers are present:

```bash
curl -I -X OPTIONS https://web-production-4f6b5.up.railway.app/transcribe \
  -H "Origin: http://localhost:61063" \
  -H "Access-Control-Request-Method: POST"
```

Look for:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: *`

## Current Configuration

The API is configured to allow all origins (`allow_origins=["*"]`), which should work for development. After redeployment, CORS should work correctly.

## Troubleshooting

1. **Clear browser cache** - Sometimes browsers cache CORS responses
2. **Check Railway logs** - Look for any errors during startup
3. **Verify deployment** - Make sure the latest code with CORS config is deployed
4. **Test with curl** - Verify the API works without CORS issues

## Testing

After fixing, test with:

```javascript
// In browser console
fetch('https://web-production-4f6b5.up.railway.app/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

