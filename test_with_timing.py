#!/usr/bin/env python3
"""
Test API with timing measurements
"""
import requests
import time
import json
import sys

def test_transcribe_with_timing(url, audio_file):
    """Test transcription endpoint and measure time"""
    print(f"Testing: {url}")
    print(f"Audio file: {audio_file}")
    print("=" * 60)
    
    # Measure total time
    start_time = time.time()
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': (audio_file, f, 'audio/mpeg')}
            
            print("Uploading file...")
            upload_start = time.time()
            
            response = requests.post(url, files=files, timeout=600)
            
            upload_end = time.time()
            total_time = upload_end - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ Success!")
                print(f"Total time: {total_time:.2f} seconds")
                print(f"Upload + Processing time: {upload_end - upload_start:.2f} seconds")
                
                print(f"\n{'='*60}")
                print("SUMMARY")
                print(f"{'='*60}")
                print(result.get('summary', 'N/A')[:300])
                
                print(f"\n{'='*60}")
                print("ACTION ITEMS")
                print(f"{'='*60}")
                action_items = result.get('action_items', [])
                print(f"Total: {len(action_items)}")
                for i, item in enumerate(action_items[:5], 1):
                    print(f"{i}. {item.get('assignee')}: {item.get('description')[:70]}")
                
                print(f"\n{'='*60}")
                print("METADATA")
                print(f"{'='*60}")
                metadata = result.get('metadata', {})
                print(f"Duration: {metadata.get('duration', 0):.2f} seconds")
                print(f"File size: {metadata.get('file_size', 0)} bytes")
                print(f"Total speakers: {metadata.get('total_speakers', 0)}")
                print(f"Total segments: {len(result.get('segments', []))}")
                
                # Calculate processing speed
                audio_duration = metadata.get('duration', 0)
                if audio_duration > 0:
                    speed_factor = audio_duration / total_time
                    print(f"\nProcessing speed: {speed_factor:.2f}x real-time")
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return False
                
    except FileNotFoundError:
        print(f"❌ File not found: {audio_file}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after {time.time() - start_time:.2f} seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_with_timing.py <audio_file> [url]")
        print("Example: python test_with_timing.py test-audio.mp3")
        print("Example: python test_with_timing.py test-audio.mp3 http://localhost:8000")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000/transcribe"
    
    test_transcribe_with_timing(url, audio_file)

