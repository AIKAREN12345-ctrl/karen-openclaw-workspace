import requests
import json
import sys

def test_ollama():
    """Test Ollama API connectivity"""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'qwen2.5:14b',
                'prompt': 'Say "Ollama is working" and nothing else.',
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 20
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Ollama working: {result.get('response', 'No response')[:100]}")
            return True
        else:
            print(f"[ERROR] Ollama error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ollama connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)
