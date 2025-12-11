from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
from typing import Optional, List, Dict
import logging
import re
from datetime import datetime

# Optional imports for speaker diarization
try:
    from pyannote.audio import Pipeline
    import torch
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pyannote.audio not available. Speaker diarization will use fallback method.")

# Optional imports for name extraction
# Note: spaCy removed due to compatibility issues - using regex-only approach
SPACY_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audio Transcription API", version="1.0.0")

# Enable CORS for all origins
# In production, you may want to restrict this to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - adjust for production if needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Global variables to store the loaded models
whisper_model = None
diarization_pipeline = None
nlp_model = None

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

def load_diarization_pipeline():
    """Load the speaker diarization pipeline"""
    global diarization_pipeline
    if not PYANNOTE_AVAILABLE:
        return None
    
    if diarization_pipeline is None:
        try:
            logger.info("Loading speaker diarization pipeline...")
            # Using pyannote.audio pipeline for speaker diarization
            # This requires a Hugging Face token - set via HF_TOKEN environment variable
            hf_token = os.getenv("HF_TOKEN")
            if hf_token:
                diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=hf_token
                )
                # Move to GPU if available
                if torch.cuda.is_available():
                    diarization_pipeline.to(torch.device("cuda"))
                logger.info("Speaker diarization pipeline loaded successfully")
            else:
                logger.warning("HF_TOKEN not set. Speaker diarization will use fallback method.")
        except Exception as e:
            logger.warning(f"Could not load diarization pipeline: {str(e)}. Speaker diarization will use fallback method.")
    return diarization_pipeline

def load_nlp_model():
    """Load spaCy NLP model for name extraction"""
    global nlp_model
    if not SPACY_AVAILABLE:
        return None
    
    if nlp_model is None:
        try:
            logger.info("Loading spaCy NLP model...")
            # Try to load English model, fallback to small if medium/large not available
            try:
                nlp_model = spacy.load("en_core_web_sm")
            except (OSError, Exception) as e:
                try:
                    nlp_model = spacy.load("en_core_web_md")
                except (OSError, Exception):
                    logger.warning(f"spaCy English model not available: {str(e)}. Using regex fallback.")
                    nlp_model = None
            if nlp_model:
                logger.info("spaCy NLP model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {str(e)}. Name extraction will use regex fallback.")
            nlp_model = None
    return nlp_model

@app.on_event("startup")
async def startup_event():
    """Load the models when the application starts"""
    load_whisper_model()
    load_diarization_pipeline()
    load_nlp_model()

def extract_names_from_text(text: str) -> List[str]:
    """
    Extract person names from text using NER or regex patterns
    
    Args:
        text: Text to extract names from
    
    Returns:
        List of unique names found
    """
    import re
    names = set()
    
    # Common words to exclude
    excluded_words = {
        'thank', 'you', 'okay', 'sure', 'yes', 'no', 'this', 'that', 'the', 'a', 'an',
        'and', 'or', 'but', 'for', 'with', 'from', 'to', 'of', 'in', 'on', 'at', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'cannot', 'must', 'shall', 'hi', 'hello', 'hey', 'bye', 'goodbye'
    }
    
    # Try using spaCy NER first
    nlp = load_nlp_model()
    if nlp:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    # Filter out common false positives
                    if len(name) > 1 and name.lower() not in excluded_words:
                        # Check if it looks like a name (starts with capital, reasonable length)
                        if name[0].isupper() and 2 <= len(name.split()[0]) <= 20:
                            names.add(name)
        except Exception as e:
            logger.warning(f"spaCy NER failed: {str(e)}")
    
    # Also use regex patterns to catch names mentioned in common phrases
    # More comprehensive patterns
    patterns = [
        # Self-introduction patterns
        r"(?:This is|I'm|I am|My name is|It's|It is|Call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        # Greeting patterns
        r"(?:Hi|Hello|Hey),?\s+([A-Z][a-z]+)",
        # Name-first patterns
        r"([A-Z][a-z]+),?\s+(?:this is|I'm|I am|speaking|here)",
        # Calling/asking for someone - improved pattern
        r"(?:calling|speaking|looking|asking|to speak)\s+(?:for|with|to speak with|to speak for)?\s+([A-Z][a-z]+)",
        # "looking to speak for [Name]" pattern
        r"looking\s+to\s+speak\s+(?:for|with)\s+([A-Z][a-z]+)",
        # Direct address
        r"([A-Z][a-z]+),?\s+(?:you|your|yours)",
        # "Thank you for holding, [Name]" pattern
        r"(?:thank you for holding|holding for|putting through),?\s+([A-Z][a-z]+)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ""
            name = match.strip()
            # Validate name
            if (len(name) > 1 and 
                name.lower() not in excluded_words and
                name[0].isupper() and
                2 <= len(name.split()[0]) <= 20):
                names.add(name)
    
    return sorted(list(names))

def map_names_to_speakers(segments: List[Dict], transcription_text: str) -> Dict[str, str]:
    """
    Map detected names to speaker IDs based on context
    
    Args:
        segments: List of segments with speaker labels
        transcription_text: Full transcription text
    
    Returns:
        Dictionary mapping speaker IDs to names (e.g., {"Speaker 1": "Anthony", "Speaker 2": "Gina"})
    """
    import re
    
    # Extract all names from transcription
    all_names = extract_names_from_text(transcription_text)
    
    if not all_names:
        logger.info("No names detected in transcription")
        return {}
    
    logger.info(f"Detected names: {all_names}")
    
    # Create mapping: speaker_id -> name
    speaker_name_map = {}
    
    # Track which names have been assigned
    assigned_names = set()
    
    # Strong self-introduction patterns (high confidence) - prioritize these
    self_intro_patterns = [
        r"(?:This is|I'm|I am|My name is|It's|It is|Call me)\s+([A-Z][a-z]+)",
        r"([A-Z][a-z]+),?\s+(?:this is|I'm|I am|speaking)",
    ]
    
    # Process segments in order to catch first introductions
    for seg in segments:
        text = seg.get("text", "").strip()
        speaker = seg.get("speaker", "")
        
        if not text or not speaker or speaker in speaker_name_map:
            continue
        
        text_lower = text.lower()
        
        # First, check for strong self-introduction patterns (highest priority)
        for pattern in self_intro_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                name = match.strip()
                
                if name in all_names and name not in assigned_names:
                    speaker_name_map[speaker] = name
                    assigned_names.add(name)
                    logger.info(f"Mapped {speaker} -> {name} (self-introduction: '{text[:50]}...')")
                    break
        
        # Only check greeting patterns if speaker not already mapped
        if speaker not in speaker_name_map:
            # Check for "Hi, [Name]" followed by "This is [OtherName]" - the OtherName is the speaker
            # Pattern: "Hi, Tania. This is Anthony" -> Anthony is the speaker
            greeting_followed_by_intro = re.search(
                r"(?:Hi|Hello|Hey),?\s+([A-Z][a-z]+)[^.]*?(?:This is|I'm|I am)\s+([A-Z][a-z]+)",
                text, re.IGNORECASE
            )
            if greeting_followed_by_intro:
                intro_name = greeting_followed_by_intro.group(2).strip()
                if intro_name in all_names and intro_name not in assigned_names:
                    speaker_name_map[speaker] = intro_name
                    assigned_names.add(intro_name)
                    logger.info(f"Mapped {speaker} -> {intro_name} (greeting + self-intro: '{text[:50]}...')")
                    continue
            
            # Check for standalone "Hi, [Name]" - only if it's clearly self-intro
            greeting_match = re.search(r"(?:Hi|Hello|Hey),?\s+([A-Z][a-z]+)", text, re.IGNORECASE)
            if greeting_match:
                name = greeting_match.group(1).strip()
                if name in all_names and name not in assigned_names:
                    # Only if the segment clearly indicates self-intro
                    if any(phrase in text_lower for phrase in ["this is", "i'm", "i am", "my name"]):
                        speaker_name_map[speaker] = name
                        assigned_names.add(name)
                        logger.info(f"Mapped {speaker} -> {name} (greeting + self-intro: '{text[:50]}...')")
    
    # For remaining names, try to assign based on context
    # Look for patterns like "calling for [Name]", "looking for [Name]", "speaking with [Name]"
    # These usually refer to the other person
    for name in all_names:
        if name in assigned_names:
            continue
        
        # Find segments mentioning this name
        for seg in segments:
            text = seg.get("text", "").strip()
            speaker = seg.get("speaker", "")
            text_lower = text.lower()
            
            if name.lower() in text_lower and speaker not in speaker_name_map:
                # Check for patterns that suggest this is the person being called/asked for
                calling_patterns = [
                    f"calling for {name.lower()}",
                    f"looking for {name.lower()}",
                    f"looking to speak for {name.lower()}",
                    f"looking to speak with {name.lower()}",
                    f"speaking with {name.lower()}",
                    f"speak for {name.lower()}",
                    f"speak with {name.lower()}",
                ]
                
                # If it's a calling pattern, assign to the OTHER speaker (not the one saying it)
                if any(pattern in text_lower for pattern in calling_patterns):
                    # Find the other speaker
                    all_speakers = set(seg.get("speaker", "") for seg in segments)
                    other_speakers = [s for s in all_speakers if s != speaker and s]
                    if other_speakers:
                        # Assign to the first other speaker found
                        other_speaker = other_speakers[0]
                        if other_speaker not in speaker_name_map:
                            speaker_name_map[other_speaker] = name
                            assigned_names.add(name)
                            logger.info(f"Mapped {other_speaker} -> {name} (called/asked for)")
                            break
    
    logger.info(f"Final speaker name mapping: {speaker_name_map}")
    return speaker_name_map

def generate_call_summary(transcription_text: str, segments_with_speakers: List[Dict]) -> str:
    """
    Generate a summary of the call based on transcription
    
    Args:
        transcription_text: Full transcription text
        segments_with_speakers: List of segments with speaker labels
    
    Returns:
        Summary string
    """
    # Extract key information from the call
    summary_parts = []
    
    # Identify main topics discussed
    topics_keywords = {
        "order": ["order", "ordered", "ordering"],
        "shipment": ["ship", "shipped", "shipping", "delivery", "deliver"],
        "payment": ["payment", "pay", "paid", "cost", "price", "charge"],
        "contract": ["contract", "agreement", "terms"],
        "service": ["service", "support", "help", "assistance"],
        "meeting": ["meeting", "call", "discuss", "talk"],
    }
    
    topics_mentioned = []
    for topic, keywords in topics_keywords.items():
        if any(keyword in transcription_text.lower() for keyword in keywords):
            topics_mentioned.append(topic)
    
    # Identify speakers
    speakers = set()
    for seg in segments_with_speakers:
        speaker = seg.get("speaker", "")
        if speaker and speaker not in ["Unknown", ""]:
            speakers.add(speaker)
    
    # Build summary
    if speakers:
        summary_parts.append(f"Call participants: {', '.join(sorted(speakers))}")
    
    if topics_mentioned:
        summary_parts.append(f"Topics discussed: {', '.join(topics_mentioned)}")
    
    # Extract key decisions or outcomes
    decision_patterns = [
        r"(?:we will|we'll|going to|will)\s+([^.]{10,100})",
        r"(?:agreed|decided|confirmed)\s+(?:to|that|on)\s+([^.]{10,100})",
        r"(?:action|next step|follow up).{0,50}(?:is|will be|to)\s+([^.]{10,100})",
    ]
    
    decisions = []
    for pattern in decision_patterns:
        matches = re.findall(pattern, transcription_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ""
            decision = match.strip()
            if len(decision) > 10 and decision not in decisions:
                decisions.append(decision[:200])  # Limit length
    
    if decisions:
        summary_parts.append(f"Key decisions: {'; '.join(decisions[:3])}")  # Limit to 3
    
    # Generate concise summary
    if summary_parts:
        summary = ". ".join(summary_parts) + "."
    else:
        # Fallback: create a basic summary from first and last parts
        words = transcription_text.split()
        if len(words) > 50:
            summary = f"Call transcript covering {len(segments_with_speakers)} segments. "
            summary += f"Main discussion: {' '.join(words[:30])}... {' '.join(words[-20:])}"
        else:
            summary = transcription_text[:500] + "..." if len(transcription_text) > 500 else transcription_text
    
    return summary

def extract_action_items(segments_with_speakers: List[Dict], transcription_text: str) -> List[Dict]:
    """
    Extract action items from the call with speaker, dates, and times
    
    Args:
        segments_with_speakers: List of segments with speaker labels
        transcription_text: Full transcription text
    
    Returns:
        List of action items with speaker, description, date, and time
    """
    action_items = []
    
    # Patterns for action items
    action_patterns = [
        # "I will [action]"
        (r"(?:I will|I'll|I'm going to|I need to|I should|I must)\s+([^.]{10,150})", "self"),
        # "You will [action]" or "You need to [action]"
        (r"(?:you will|you'll|you need to|you should|you must|please)\s+([^.]{10,150})", "other"),
        # "We will [action]"
        (r"(?:we will|we'll|we need to|we should|we must)\s+([^.]{10,150})", "both"),
        # "Action: [description]"
        (r"(?:action|task|todo|follow up|next step).{0,30}[:is]?\s+([^.]{10,150})", "unknown"),
        # "Let me [action]"
        (r"let me\s+([^.]{10,150})", "self"),
        # "Can you [action]"
        (r"can you\s+([^.]{10,150})", "other"),
    ]
    
    # Date/time patterns
    date_patterns = [
        r"(?:on|by|before|after|until)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",  # MM/DD/YYYY
        r"(?:on|by|before|after|until)\s+(\w+\s+\d{1,2},?\s+\d{4})",  # Month DD, YYYY
        r"(?:on|by|before|after|until)\s+(\w+\s+\d{1,2})",  # Month DD
        r"(?:on|by|before|after|until)\s+(today|tomorrow|next week|next month)",
        r"(?:end of|beginning of)\s+(\w+)",  # end of month, beginning of week
    ]
    
    time_patterns = [
        r"(?:at|by|before|after)\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
        r"(?:at|by|before|after)\s+(\d{1,2}\s*(?:AM|PM|am|pm))",
    ]
    
    # Find action items in segments
    for seg in segments_with_speakers:
        text = seg.get("text", "").strip()
        speaker = seg.get("speaker", "Unknown")
        
        if not text:
            continue
        
        # Check for action patterns
        for pattern, assignee_type in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                
                action_text = match.strip()
                if len(action_text) < 10 or len(action_text) > 200:
                    continue
                
                # Extract date if mentioned
                date_mentioned = None
                for date_pattern in date_patterns:
                    date_match = re.search(date_pattern, text, re.IGNORECASE)
                    if date_match:
                        date_mentioned = date_match.group(1) if date_match.groups() else date_match.group(0)
                        break
                
                # Extract time if mentioned
                time_mentioned = None
                for time_pattern in time_patterns:
                    time_match = re.search(time_pattern, text, re.IGNORECASE)
                    if time_match:
                        time_mentioned = time_match.group(1) if time_match.groups() else time_match.group(0)
                        break
                
                # Determine assignee based on pattern type
                assignee = speaker
                if assignee_type == "other":
                    # Find the other speaker
                    all_speakers = set(seg.get("speaker", "") for seg in segments_with_speakers)
                    other_speakers = [s for s in all_speakers if s != speaker and s and s != "Unknown"]
                    if other_speakers:
                        assignee = other_speakers[0]
                elif assignee_type == "both":
                    assignee = "Both"
                
                # Create action item
                action_item = {
                    "assignee": assignee,
                    "description": action_text,
                    "speaker": speaker,
                    "timestamp": seg.get("start", 0),
                }
                
                if date_mentioned:
                    action_item["date"] = date_mentioned
                if time_mentioned:
                    action_item["time"] = time_mentioned
                
                # Avoid duplicates
                is_duplicate = False
                for existing in action_items:
                    if (existing["description"].lower() == action_text.lower() or
                        existing["description"].lower() in action_text.lower() or
                        action_text.lower() in existing["description"].lower()):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    action_items.append(action_item)
                    break  # Only take first match per segment
    
    return action_items

def assign_speakers_to_segments(segments: List[Dict], diarization_result) -> List[Dict]:
    """
    Assign speaker labels to transcription segments based on time overlap
    
    Args:
        segments: List of transcription segments from Whisper
        diarization_result: Speaker diarization result from pyannote
    
    Returns:
        List of segments with speaker labels
    """
    if diarization_result is None:
        # If diarization is not available, use a simple heuristic:
        # Alternate speakers based on gaps between segments
        # Larger gaps likely indicate speaker change
        if not segments:
            return segments
        
        speaker_id = 0
        prev_end = 0
        gap_threshold = 1.0  # 1 second gap suggests speaker change
        
        for i, seg in enumerate(segments):
            seg_start = seg.get("start", 0)
            gap = seg_start - prev_end
            
            # If there's a significant gap, likely a new speaker
            if gap > gap_threshold and i > 0:
                speaker_id = (speaker_id + 1) % 2
            
            seg["speaker"] = f"Speaker {speaker_id + 1}"
            prev_end = seg.get("end", 0)
        
        return segments
    
    # Create a mapping of time ranges to speakers
    speaker_segments = []
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        speaker_segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    
    # Assign speakers to transcription segments based on time overlap
    for seg in segments:
        seg_start = seg.get("start", 0)
        seg_end = seg.get("end", 0)
        seg_mid = (seg_start + seg_end) / 2
        
        # Find the speaker segment that contains the midpoint of this transcription segment
        assigned_speaker = None
        for spk_seg in speaker_segments:
            if spk_seg["start"] <= seg_mid <= spk_seg["end"]:
                assigned_speaker = spk_seg["speaker"]
                break
        
        # If no exact match, find the closest speaker segment
        if assigned_speaker is None:
            min_distance = float('inf')
            for spk_seg in speaker_segments:
                # Calculate overlap
                overlap_start = max(seg_start, spk_seg["start"])
                overlap_end = min(seg_end, spk_seg["end"])
                if overlap_start < overlap_end:
                    overlap = overlap_end - overlap_start
                    if overlap > min_distance:
                        min_distance = overlap
                        assigned_speaker = spk_seg["speaker"]
        
        # Default to Speaker 1 if no match found
        if assigned_speaker is None:
            assigned_speaker = "SPEAKER_00"
        
        # Convert speaker ID to readable format (SPEAKER_00 -> Speaker 1)
        speaker_num = int(assigned_speaker.split("_")[-1]) + 1
        seg["speaker"] = f"Speaker {speaker_num}"
    
    return segments

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

@app.options("/transcribe")
async def transcribe_options():
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600",
        }
    )

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
            
            # Perform speaker diarization
            diarization_result = None
            try:
                pipeline = load_diarization_pipeline()
                if pipeline is not None:
                    logger.info("Running speaker diarization...")
                    diarization_result = pipeline(temp_file_path)
                    logger.info("Speaker diarization completed")
            except Exception as e:
                logger.warning(f"Speaker diarization failed: {str(e)}. Continuing without speaker labels.")
            
            # Assign speakers to segments
            segments_with_speakers = assign_speakers_to_segments(segments, diarization_result)
            
            # Extract names and map them to speakers
            speaker_name_map = map_names_to_speakers(segments_with_speakers, transcription_text)
            all_names = extract_names_from_text(transcription_text)
            
            # Replace speaker labels with actual names where available
            # Also check each segment individually for "This is [Name]" patterns
            import re
            for seg in segments_with_speakers:
                speaker_id = seg.get("speaker", "")
                text = seg.get("text", "").strip()
                
                # Check if this segment contains a self-introduction
                # Pattern: "This is [Name]" or "I'm [Name]" - this speaker IS that name
                intro_match = re.search(r"(?:This is|I'm|I am|My name is)\s+([A-Z][a-z]+)", text, re.IGNORECASE)
                if intro_match:
                    name = intro_match.group(1).strip()
                    # If this name is in our detected names, assign it to this speaker
                    if name in all_names:
                        # Update the speaker name map for this speaker ID
                        speaker_name_map[speaker_id] = name
                        seg["speaker"] = name
                        logger.info(f"Segment-level mapping: {speaker_id} -> {name} (from '{text[:50]}...')")
                        continue
                
                # Otherwise, use the mapped name if available
                if speaker_id in speaker_name_map:
                    seg["speaker"] = speaker_name_map[speaker_id]
            
            # Build transcription with speaker labels
            transcription_with_speakers = []
            for seg in segments_with_speakers:
                transcription_with_speakers.append({
                    "speaker": seg.get("speaker", "Unknown"),
                    "text": seg.get("text", "").strip(),
                    "start": seg.get("start"),
                    "end": seg.get("end")
                })
            
            # Generate call summary
            call_summary = ""
            try:
                logger.info("Generating call summary...")
                call_summary = generate_call_summary(transcription_text, segments_with_speakers)
                logger.info(f"Summary generated: {len(call_summary)} chars")
            except Exception as e:
                logger.error(f"Error generating summary: {str(e)}", exc_info=True)
                call_summary = f"Error generating summary: {str(e)}"
            
            # Extract action items
            action_items = []
            try:
                logger.info("Extracting action items...")
                action_items = extract_action_items(segments_with_speakers, transcription_text)
                logger.info(f"Action items extracted: {len(action_items)}")
            except Exception as e:
                logger.error(f"Error extracting action items: {str(e)}", exc_info=True)
                action_items = []
            
            # Prepare response
            response = {
                "success": True,
                "transcription": transcription_text,
                "summary": call_summary,
                "action_items": action_items,
                "language_detected": detected_language,
                "language_requested": language if language else "auto",
                "transcription_with_speakers": transcription_with_speakers,
                "segments": [
                    {
                        "id": seg.get("id"),
                        "speaker": seg.get("speaker", "Unknown"),
                        "start": seg.get("start"),
                        "end": seg.get("end"),
                        "text": seg.get("text", "").strip()
                    }
                    for seg in segments_with_speakers
                ],
                "metadata": {
                    "filename": file.filename,
                    "file_size": len(content),
                    "duration": segments[-1].get("end", 0) if segments else 0,
                    "speaker_diarization": diarization_result is not None,
                    "total_speakers": len(set(seg.get("speaker", "") for seg in segments_with_speakers)),
                    "total_action_items": len(action_items)
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

