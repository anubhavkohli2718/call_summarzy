#!/bin/bash
# Startup script for Railway
# This ensures PORT environment variable is properly handled

PORT=${PORT:-8000}
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=int('$PORT'))"

