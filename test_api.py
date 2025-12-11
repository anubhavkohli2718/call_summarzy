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
                print(f"\nTranscription:\n{result['transcription']}")
                print(f"\nDuration: {result['metadata']['duration']:.2f} seconds")
                print(f"File size: {result['metadata']['file_size']} bytes")
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

