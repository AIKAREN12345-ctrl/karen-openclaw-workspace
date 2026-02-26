#!/usr/bin/env python3
"""
Local Memory Log Generator
Creates hourly memory logs using local LLM (phi3:mini)
Optimized for 24GB RAM - uses small model, unloads immediately
"""

import json
import urllib.request
import datetime
import os
import sys

# Config
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"  # 4.7GB - best accuracy for critical memory system
KEEP_ALIVE = "5m"  # Keep loaded for 5 minutes to handle bursts
MEMORY_DIR = "C:\\Users\\Karen\\.openclaw\\workspace\\memory"

def get_system_info():
    """Get basic system info for the log"""
    import platform
    import subprocess
    
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }
    
    # Get OpenClaw status (simple check)
    try:
        result = subprocess.run(["openclaw", "status"], capture_output=True, text=True, timeout=10)
        info["openclaw_status"] = "running" if "OpenClaw" in result.stdout else "unknown"
    except:
        info["openclaw_status"] = "check_failed"
    
    return info

def generate_log_content(system_info):
    """Use local LLM to generate memory log content"""
    
    prompt = f"""You are a system monitoring agent. Create a concise hourly log entry based on this system info:

Timestamp: {system_info['timestamp']}
Platform: {system_info['platform']}
Machine: {system_info['machine']}
Hostname: {system_info['hostname']}
OpenClaw: {system_info['openclaw_status']}

Write a brief status report (3-5 sentences) covering:
1. System is operational
2. Platform details
3. Any notable observations

Keep it factual and concise."""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": KEEP_ALIVE  # Keep loaded for consistency
    }
    
    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    
    try:
        req = urllib.request.Request(OLLAMA_URL, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', 'No response generated')
    except Exception as e:
        return f"Error generating log: {str(e)}"

def write_memory_log(content):
    """Write to daily memory file"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(MEMORY_DIR, f"{today}.md")
    
    # Ensure directory exists
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    log_entry = f"\n## {timestamp} - Hourly Memory Log\n\n{content}\n\n---\n"
    
    # Append to file (create if doesn't exist)
    mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, mode, encoding='utf-8') as f:
        if mode == 'w':
            f.write(f"# Memory Log - {today}\n\n")
        f.write(log_entry)
    
    return filename

def main():
    """Main entry point"""
    try:
        # Get system info
        sys_info = get_system_info()
        
        # Generate log content with local LLM
        content = generate_log_content(sys_info)
        
        # Write to memory file
        filename = write_memory_log(content)
        
        print(f"[OK] Memory log written to: {filename}")
        print(f"Model: {MODEL} (4.7GB, kept alive for {KEEP_ALIVE})")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Failed to create memory log: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
