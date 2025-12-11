#!/usr/bin/env python3
"""Test name extraction and mapping"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import extract_names_from_text, map_names_to_speakers

# Test transcription from the audio
test_text = """Thank you for calling. No group. This is Fania. How many help you? Hi, Tania. This is Anthony. I'm calling from added. I was looking to speak for Gina. Okay. Let me see if she's available. Do you mind holding this moment? Sure. No problem. Thank you for holding this, Gina. Hi, Gina. This is Anthony."""

# Create mock segments
segments = [
    {"speaker": "Speaker 1", "text": "Thank you for calling. No group. This is Fania.", "start": 0.0, "end": 5.0},
    {"speaker": "Speaker 1", "text": "How many help you?", "start": 5.0, "end": 6.0},
    {"speaker": "Speaker 2", "text": "Hi, Tania. This is Anthony.", "start": 6.0, "end": 8.0},
    {"speaker": "Speaker 2", "text": "I'm calling from added. I was looking to speak for Gina.", "start": 8.0, "end": 12.0},
    {"speaker": "Speaker 1", "text": "Thank you for holding this, Gina.", "start": 15.0, "end": 18.0},
    {"speaker": "Speaker 1", "text": "Hi, Gina. This is Anthony.", "start": 18.0, "end": 20.0},
]

print("Testing name extraction...")
names = extract_names_from_text(test_text)
print(f"Names found: {names}")

print("\nTesting name mapping...")
name_map = map_names_to_speakers(segments, test_text)
print(f"Speaker name mapping: {name_map}")

print("\nApplying names to segments...")
for seg in segments:
    speaker_id = seg.get("speaker", "")
    if speaker_id in name_map:
        seg["speaker"] = name_map[speaker_id]
    print(f"{seg['speaker']}: {seg['text']}")

