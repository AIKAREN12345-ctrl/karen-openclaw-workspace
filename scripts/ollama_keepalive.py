# Ollama Keep-Alive Script
# Keeps qwen2.5:7b model loaded in memory for instant responses
# Runs every 10 minutes via cron
# 100% local - no API calls, no internet needed

import urllib.request
import urllib.error
import json
import sys
import os

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

def keep_model_alive():
    """Send a keep-alive ping to Ollama to keep model loaded."""
    try:
        data = json.dumps({
            "model": "qwen3:8b",
            "prompt": "ping",
            "stream": False,
            "options": {
                "num_predict": 1  # Minimal token generation
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'http://localhost:11434/api/generate',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        # Short timeout - we just want to ping, not wait for full response
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                print("[OK] Model is warm and ready")
                return True
            else:
                print(f"[WARN] Ollama responded with status: {response.status}")
                return False
                
    except urllib.error.URLError as e:
        print(f"[ERROR] Ollama not running: {e}")
        print("        Start with: ollama run qwen3:8b")
        return False
    except TimeoutError:
        print("[TIMEOUT] Ollama is starting up (this is normal)")
        return True  # Model is loading, which is what we want
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def check_model_status():
    """Check if model is already loaded."""
    try:
        req = urllib.request.Request(
            'http://localhost:11434/api/ps',
            method='GET'
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            
            for model in models:
                if 'qwen' in model.get('name', '').lower():
                    print(f"[OK] Model already loaded: {model.get('name')}")
                    return True
            return False
            
    except:
        return False

if __name__ == "__main__":
    print(f"[{__import__('datetime').datetime.now().strftime('%H:%M:%S')}] Ollama Keep-Alive Check")
    
    # Check if already loaded
    if check_model_status():
        sys.exit(0)
    
    # Try to keep it alive
    success = keep_model_alive()
    sys.exit(0 if success else 1)
