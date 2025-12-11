"""
Simple test script for the Audio Transcription API
Run this after starting the server locally
"""
import requests
import sys

def test_transcribe(audio_file_path, language=None):
    """
    Test the transcription endpoint
    
    Args:
        audio_file_path: Path to the audio file
        language: Optional language code ('en' or 'es')
    """
    url = "http://localhost:8000/transcribe"
    
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'file': (audio_file_path, f, 'audio/mpeg')}
            params = {}
            if language:
                params['language'] = language
            
            print(f"Uploading {audio_file_path}...")
            response = requests.post(url, files=files, params=params)
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Transcription successful!")
                print(f"\nLanguage detected: {result['language_detected']}")
                print(f"Language requested: {result['language_requested']}")
                
                # Display Summary
                print(f"\n{'='*60}")
                print("CALL SUMMARY:")
                print(f"{'='*60}\n")
                print(result.get('summary', 'No summary available'))
                
                # Display Action Items
                print(f"\n{'='*60}")
                print("ACTION ITEMS:")
                print(f"{'='*60}\n")
                action_items = result.get('action_items', [])
                if action_items:
                    for i, item in enumerate(action_items, 1):
                        print(f"{i}. Assignee: {item.get('assignee', 'Unknown')}")
                        print(f"   Description: {item.get('description', '')}")
                        if item.get('date'):
                            print(f"   Date: {item.get('date')}")
                        if item.get('time'):
                            print(f"   Time: {item.get('time')}")
                        print(f"   Mentioned at: {item.get('timestamp', 0):.1f}s")
                        print()
                else:
                    print("No action items detected.")
                
                print(f"\n{'='*60}")
                print("TRANSCRIPTION WITH SPEAKER LABELS:")
                print(f"{'='*60}\n")
                
                # Display transcription with speakers (first 10 segments)
                if 'transcription_with_speakers' in result:
                    for item in result['transcription_with_speakers'][:10]:
                        speaker = item.get('speaker', 'Unknown')
                        text = item.get('text', '')
                        start_time = item.get('start', 0)
                        print(f"[{start_time:.1f}s] {speaker}: {text}")
                    if len(result['transcription_with_speakers']) > 10:
                        print(f"\n... and {len(result['transcription_with_speakers']) - 10} more segments")
                
                print(f"\n{'='*60}")
                print("METADATA:")
                print(f"{'='*60}")
                print(f"Duration: {result['metadata']['duration']:.2f} seconds")
                print(f"File size: {result['metadata']['file_size']} bytes")
                print(f"Total speakers: {result['metadata'].get('total_speakers', 'N/A')}")
                print(f"Total action items: {result['metadata'].get('total_action_items', 0)}")
                print(f"Speaker diarization: {'Enabled' if result['metadata'].get('speaker_diarization', False) else 'Disabled (using fallback)'}")
                
                # Print JSON format
                import json
                print(f"\n{'='*60}")
                print("JSON OUTPUT (first 500 chars):")
                print(f"{'='*60}\n")
                json_str = json.dumps(result, indent=2)
                print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                
    except FileNotFoundError:
        print(f"❌ Error: File '{audio_file_path}' not found")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <audio_file_path> [language]")
        print("Example: python test_api.py audio.mp3 en")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else None
    
    test_transcribe(audio_file, lang)

