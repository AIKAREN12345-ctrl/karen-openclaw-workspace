#!/usr/bin/env python3
"""
Ollama Research Script
Performs periodic research tasks using local Ollama models.
Runs via cron job every 4 hours.
"""

import json
import urllib.request
import urllib.error
import sys
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")

def log(message):
    """Print with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def ollama_generate(prompt, model="qwen2.5:7b", stream=False):
    """Generate text using Ollama API"""
    data = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            full_response = ""
            for line in response:
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            full_response += chunk['response']
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            return full_response.strip()
    except urllib.error.URLError as e:
        log(f"Error connecting to Ollama: {e}")
        return None
    except Exception as e:
        log(f"Unexpected error: {e}")
        return None

def check_ollama_status():
    """Check if Ollama is running"""
    try:
        req = urllib.request.Request("http://localhost:11434", method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except:
        return False

def get_local_models():
    """Get list of available models"""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", method='GET')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return [m['name'] for m in data.get('models', [])]
    except Exception as e:
        log(f"Could not fetch models: {e}")
        return []

def research_task():
    """Main research task - analyze recent memory and provide insights"""
    log("Starting Ollama research task...")
    
    # Check Ollama status
    if not check_ollama_status():
        log("ERROR: Ollama is not running on localhost:11434")
        return 1
    
    log("Ollama is running")
    
    # Get available models
    models = get_local_models()
    log(f"Available models: {', '.join(models) if models else 'None'}")
    
    # Prefer qwen2.5:7b, fallback to qwen2.5:14b or first available
    model = None
    if "qwen2.5:7b" in models:
        model = "qwen2.5:7b"
    elif "qwen2.5:14b" in models:
        model = "qwen2.5:14b"
    elif models:
        model = models[0]
    if not model:
        log("ERROR: No models available")
        return 1
    
    log(f"Using model: {model}")
    
    # Research: Analyze recent activity and suggest improvements
    prompt = """You are a system optimization assistant. Given the current time is 
""" + datetime.now().strftime("%A, %B %d, %Y at %H:%M") + """, provide:

1. A brief system health check summary (2-3 sentences)
2. One actionable suggestion for improving productivity or system performance
3. A quick tip for Windows 11 optimization

Keep your response concise (under 150 words) and practical."""

    log("Generating research insights...")
    result = ollama_generate(prompt, model=model)
    
    if result:
        log("Research complete!")
        print("\n" + "="*60)
        print("OLLAMA RESEARCH REPORT")
        print("="*60)
        print(result)
        print("="*60)
        
        # Save to memory file
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        report_file = MEMORY_DIR / f"research-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        with open(report_file, 'w') as f:
            f.write(f"# Ollama Research Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {model}\n\n")
            f.write(result)
        
        log(f"Report saved to: {report_file}")
        return 0
    else:
        log("ERROR: Failed to generate research")
        return 1

if __name__ == "__main__":
    sys.exit(research_task())
