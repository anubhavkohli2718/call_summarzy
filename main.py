from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audio Transcription API", version="1.0.0")

# Enable CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store the loaded model
whisper_model = None

def load_whisper_model():
    """Load the Whisper model on startup"""
    global whisper_model
    if whisper_model is None:
        logger.info("Loading Whisper model...")
        # Using base model - you can change to 'small', 'medium', 'large', etc.
        # base is a good balance between speed and accuracy
        whisper_model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully")
    return whisper_model

@app.on_event("startup")
async def startup_event():
    """Load the model when the application starts"""
    load_whisper_model()

@app.get("/")
async def root():
    return {
        "message": "Audio Transcription API",
        "status": "running",
        "supported_languages": ["en", "es"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": whisper_model is not None
    }

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """
    Transcribe an audio file using Whisper model.
    
    Args:
        file: Audio file to transcribe (supports: mp3, wav, m4a, flac, etc.)
        language: Optional language code ('en' for English, 'es' for Spanish).
                 If not provided, Whisper will auto-detect the language.
    
    Returns:
        JSON response with transcription, language detected, and metadata
    """
    if whisper_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate file type
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mp4', '.mpeg'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate language if provided
    if language and language not in ['en', 'es']:
        raise HTTPException(
            status_code=400,
            detail="Language must be 'en' (English) or 'es' (Spanish), or omit for auto-detection"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio
            logger.info(f"Transcribing audio file: {file.filename}")
            
            # Prepare transcription options
            transcribe_options = {
                "task": "transcribe",
                "verbose": False
            }
            
            # Set language if specified, otherwise auto-detect
            if language:
                transcribe_options["language"] = language
            else:
                # Auto-detect language (Whisper will detect automatically)
                transcribe_options["language"] = None
            
            # Perform transcription
            result = whisper_model.transcribe(temp_file_path, **transcribe_options)
            
            # Extract results
            detected_language = result.get("language", "unknown")
            transcription_text = result.get("text", "").strip()
            segments = result.get("segments", [])
            
            # Prepare response
            response = {
                "success": True,
                "transcription": transcription_text,
                "language_detected": detected_language,
                "language_requested": language if language else "auto",
                "segments": [
                    {
                        "id": seg.get("id"),
                        "start": seg.get("start"),
                        "end": seg.get("end"),
                        "text": seg.get("text", "").strip()
                    }
                    for seg in segments
                ],
                "metadata": {
                    "filename": file.filename,
                    "file_size": len(content),
                    "duration": segments[-1].get("end", 0) if segments else 0
                }
            }
            
            logger.info(f"Transcription completed. Language: {detected_language}, Length: {len(transcription_text)} chars")
            
            return JSONResponse(content=response)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

