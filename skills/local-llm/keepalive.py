# Local LLM Keepalive
# Keeps Ollama models loaded for faster responses

import requests
import time
import sys

def keepalive(model='qwen2.5:14b', duration_minutes=5):
    """Keep model loaded by sending periodic requests"""
    print(f"[INFO] Starting keepalive for {model} ({duration_minutes} min)")
    
    end_time = time.time() + (duration_minutes * 60)
    
    while time.time() < end_time:
        try:
            # Lightweight query to keep model loaded
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': 'Say "keepalive"',
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'num_predict': 5
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"[OK] Keepalive ping successful")
            else:
                print(f"[WARN] Keepalive failed: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] Keepalive error: {e}")
        
        # Wait 2 minutes between pings
        time.sleep(120)
    
    print("[INFO] Keepalive complete")

if __name__ == "__main__":
    keepalive()
