#!/usr/bin/env python3
"""
Test script for Qwen2.5-14B model
"""
import json
import urllib.request

def test_model(model="qwen2.5:14b"):
    """Test if model responds correctly"""
    try:
        data = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "Say hello and confirm your model size"}],
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'http://localhost:11434/api/chat',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('message', {}).get('content', 'No response')
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Testing Qwen2.5-14B model...")
    result = test_model()
    print(f"Response: {result}")
