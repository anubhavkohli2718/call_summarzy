# Railway Deployment Setup Guide

## FFmpeg Installation

This project requires FFmpeg for audio processing. Railway will automatically install it using the `nixpacks.toml` configuration file.

## Deployment Steps

### Option 1: Using Nixpacks (Recommended)

Railway will automatically detect `nixpacks.toml` and install FFmpeg.

1. Push your code to GitHub
2. Connect your GitHub repository to Railway
3. Railway will automatically:
   - Install Python 3.11
   - Install FFmpeg
   - Install Python dependencies
   - Start the server

### Option 2: Using Dockerfile

If Nixpacks doesn't work, Railway can use the Dockerfile:

1. In Railway dashboard, go to your service settings
2. Under "Build & Deploy", select "Dockerfile" as the build method
3. Railway will use the provided Dockerfile which includes FFmpeg

## Verifying FFmpeg Installation

After deployment, you can verify FFmpeg is installed by checking the health endpoint:

```bash
curl https://web-production-4f6b5.up.railway.app/health
```

If FFmpeg is missing, you'll see errors when trying to transcribe audio files.

## Troubleshooting

### FFmpeg Not Found Error

If you still get FFmpeg errors after deployment:

1. **Check Railway Build Logs**: Look for FFmpeg installation messages
2. **Redeploy**: Sometimes a redeploy fixes the issue
3. **Use Dockerfile**: Switch to Dockerfile method if Nixpacks isn't working

### Manual FFmpeg Installation (if needed)

If Railway's automatic installation doesn't work, you can add this to your build command in Railway settings:

```bash
apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
```

However, this requires using a Dockerfile or custom build script.

## Environment Variables

No special environment variables are required for FFmpeg. It's installed as a system package.

## Testing After Deployment

```bash
# Test health
curl https://web-production-4f6b5.up.railway.app/health

# Test transcription
curl -X POST "https://web-production-4f6b5.up.railway.app/transcribe" \
  -F "file=@test-audio.mp3"
```

If FFmpeg is properly installed, transcription should work without errors.

