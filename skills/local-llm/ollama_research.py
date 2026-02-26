#!/usr/bin/env python3
"""
Ollama Research Assistant
Background research worker using Ollama
"""

import datetime
import os
import sys
import json
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "memory")
RESEARCH_DIR = os.path.join(MEMORY_DIR, "research")

def query_ollama(prompt, model="qwen2.5:7b", timeout=60):
    """Query Ollama for research"""
    try:
        data = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'http://localhost:11434/api/chat',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('message', {}).get('content', 'No response')
    except Exception as e:
        return f"Error: {str(e)}"

def get_research_queue():
    """Get pending research topics from queue file"""
    queue_file = os.path.join(RESEARCH_DIR, "queue.txt")
    
    if not os.path.exists(queue_file):
        return None
    
    with open(queue_file, 'r') as f:
        topics = [line.strip() for line in f if line.strip()]
    
    if not topics:
        return None
    
    # Get first topic and remove from queue
    topic = topics[0]
    remaining = topics[1:]
    
    with open(queue_file, 'w') as f:
        f.write('\n'.join(remaining))
    
    return topic

def do_research(topic):
    """Have Ollama research a topic"""
    prompt = f"""Research the following topic and provide a comprehensive summary:

Topic: {topic}

Please provide:
1. Key points (3-5 bullet points)
2. Brief explanation of each
3. Any relevant context or background

Keep it factual and concise."""
    
    return query_ollama(prompt, timeout=120)

def save_research(topic, content):
    """Save research results"""
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    
    # Create safe filename
    safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
    safe_topic = safe_topic[:50]  # Limit length
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filename = os.path.join(RESEARCH_DIR, f"{timestamp}_{safe_topic}.md")
    
    content = f"""# Research: {topic}

**Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
**Researcher:** Ollama (qwen2.5:7b)

## Findings

{content}

---
*This research was conducted by Ollama in the background*
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def log_activity(topic, status, filename=None):
    """Log research activity to memory"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    memory_file = os.path.join(MEMORY_DIR, f"{today}.md")
    
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    if filename:
        log_entry = f"\n## {timestamp} - Research Complete\n\n**Topic:** {topic}\n**Status:** {status}\n**File:** `{filename}`\n\n---\n"
    else:
        log_entry = f"\n## {timestamp} - Research Activity\n\n**Topic:** {topic}\n**Status:** {status}\n\n---\n"
    
    mode = 'a' if os.path.exists(memory_file) else 'w'
    with open(memory_file, mode, encoding='utf-8') as f:
        if mode == 'w':
            f.write(f"# Memory Log - {today}\n\n")
        f.write(log_entry)

def main():
    """Main entry point"""
    try:
        print("[INFO] Starting Ollama research assistant...")
        
        # Get topic from queue
        topic = get_research_queue()
        
        if not topic:
            print("[INFO] No research topics in queue")
            return 0
        
        print(f"[INFO] Researching: {topic}")
        
        # Do research
        content = do_research(topic)
        
        if content.startswith("Error:"):
            print(f"[ERROR] Research failed: {content}")
            log_activity(topic, f"failed - {content}")
            return 1
        
        # Save results
        filename = save_research(topic, content)
        print(f"[OK] Research saved to: {filename}")
        
        # Log activity
        log_activity(topic, "completed", filename)
        
        return 0
        
    except Exception as e:
        error_msg = f"[ERROR] Research assistant failed: {str(e)}"
        print(error_msg, file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
