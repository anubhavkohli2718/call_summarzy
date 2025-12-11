#!/usr/bin/env python3
"""
Test Railway timeout issue
"""
import requests
import time
import sys

def test_timeout(url):
    """Test if request times out"""
    print(f"Testing: {url}")
    print("=" * 60)
    
    try:
        # Test health endpoint first
        print("1. Testing health endpoint...")
        health_response = requests.get(f"{url}/health", timeout=10)
        print(f"   ✅ Health: {health_response.status_code}")
        print(f"   Response: {health_response.json()}")
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        root_response = requests.get(url, timeout=10)
        print(f"   ✅ Root: {root_response.status_code}")
        
        # Test transcription with timeout monitoring
        print("\n3. Testing transcription (monitoring for timeout)...")
        print("   Uploading test-audio.mp3...")
        print("   Railway has 60-second timeout limit")
        print("   If this hangs, Railway is killing the connection")
        
        start_time = time.time()
        
        with open("test-audio.mp3", "rb") as f:
            files = {"file": ("test-audio.mp3", f, "audio/mpeg")}
            
            try:
                response = requests.post(
                    f"{url}/transcribe",
                    files=files,
                    timeout=120  # Client timeout (but Railway may kill earlier)
                )
                
                elapsed = time.time() - start_time
                print(f"\n   ✅ Request completed in {elapsed:.2f} seconds")
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Success!")
                    print(f"   Transcription length: {len(result.get('transcription', ''))}")
                    return True
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    print(f"   Response: {response.text[:500]}")
                    return False
                    
            except requests.exceptions.Timeout:
                elapsed = time.time() - start_time
                print(f"\n   ❌ TIMEOUT after {elapsed:.2f} seconds")
                print(f"   This confirms Railway's 60-second timeout limit")
                print(f"   Solution: Use 'tiny' model or implement async processing")
                return False
                
    except FileNotFoundError:
        print("❌ Error: test-audio.mp3 not found")
        return False
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print(f"\n❌ Error after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://web-production-fac69.up.railway.app"
    test_timeout(url)

