#!/usr/bin/env python3
"""
Test script for production API
Usage: python test_production.py [audio_file.mp3]
"""
import requests
import json
import sys

PRODUCTION_URL = "https://web-production-4f6b5.up.railway.app"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    try:
        response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n" + "=" * 60)
    print("Testing Root Endpoint")
    print("=" * 60)
    try:
        response = requests.get(f"{PRODUCTION_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_transcribe(audio_file_path, language=None):
    """Test transcription endpoint"""
    print("\n" + "=" * 60)
    print("Testing Transcription Endpoint")
    print("=" * 60)
    
    if not audio_file_path:
        print("No audio file provided. Skipping transcription test.")
        return False
    
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'file': (audio_file_path, f, 'audio/mpeg')}
            params = {}
            if language:
                params['language'] = language
            
            print(f"Uploading {audio_file_path}...")
            print(f"Language: {language if language else 'auto-detect'}")
            
            response = requests.post(
                f"{PRODUCTION_URL}/transcribe",
                files=files,
                params=params,
                timeout=300  # 5 minutes for large files
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ Transcription successful!")
                print(f"\n{'='*60}")
                print("SUMMARY")
                print(f"{'='*60}")
                print(result.get('summary', 'N/A'))
                
                print(f"\n{'='*60}")
                print("ACTION ITEMS")
                print(f"{'='*60}")
                action_items = result.get('action_items', [])
                if action_items:
                    for i, item in enumerate(action_items, 1):
                        print(f"\n{i}. Assignee: {item.get('assignee', 'Unknown')}")
                        print(f"   Description: {item.get('description', '')}")
                        if item.get('date'):
                            print(f"   Date: {item.get('date')}")
                        if item.get('time'):
                            print(f"   Time: {item.get('time')}")
                        print(f"   Mentioned at: {item.get('timestamp', 0):.1f}s")
                else:
                    print("No action items detected.")
                
                print(f"\n{'='*60}")
                print("SPEAKERS")
                print(f"{'='*60}")
                speakers = set()
                for seg in result.get('transcription_with_speakers', []):
                    speakers.add(seg.get('speaker', 'Unknown'))
                print(f"Participants: {', '.join(sorted(speakers))}")
                
                print(f"\n{'='*60}")
                print("METADATA")
                print(f"{'='*60}")
                metadata = result.get('metadata', {})
                print(f"Duration: {metadata.get('duration', 0):.2f} seconds")
                print(f"File size: {metadata.get('file_size', 0)} bytes")
                print(f"Total speakers: {metadata.get('total_speakers', 0)}")
                print(f"Total action items: {metadata.get('total_action_items', 0)}")
                
                print(f"\n{'='*60}")
                print("SAMPLE TRANSCRIPTION (first 5 segments)")
                print(f"{'='*60}")
                for seg in result.get('transcription_with_speakers', [])[:5]:
                    print(f"[{seg.get('start', 0):.1f}s] {seg.get('speaker', 'Unknown')}: {seg.get('text', '')}")
                
                # Save full response to file
                output_file = "transcription_result.json"
                with open(output_file, 'w') as out:
                    json.dump(result, out, indent=2)
                print(f"\n✅ Full response saved to: {output_file}")
                
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                return False
                
    except FileNotFoundError:
        print(f"❌ Error: File '{audio_file_path}' not found")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out. File may be too large.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Production API Test Script")
    print(f"Testing: {PRODUCTION_URL}\n")
    
    # Test health and root endpoints
    health_ok = test_health()
    root_ok = test_root()
    
    # Test transcription if audio file provided
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    language = sys.argv[2] if len(sys.argv) > 2 else None
    
    if audio_file:
        transcribe_ok = test_transcribe(audio_file, language)
    else:
        print("\n" + "=" * 60)
        print("No audio file provided for transcription test")
        print("Usage: python test_production.py <audio_file.mp3> [language]")
        print("Example: python test_production.py test-audio.mp3 en")
        transcribe_ok = None
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Root Endpoint: {'✅ PASS' if root_ok else '❌ FAIL'}")
    if transcribe_ok is not None:
        print(f"Transcription: {'✅ PASS' if transcribe_ok else '❌ FAIL'}")

