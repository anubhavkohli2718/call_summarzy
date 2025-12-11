# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variable
ENV PORT=8000

# Run the application
# Railway sets PORT environment variable, but we need to read it in Python
CMD python -c "import os; port = int(os.getenv('PORT', '8000')); import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=port)"

