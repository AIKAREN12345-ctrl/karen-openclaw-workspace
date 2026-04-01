#!/usr/bin/env python3
"""
Karen Research Scheduler

This script sends a message to Karen (Kimi) to perform research.
Karen will receive the request and use her tools to do the research.
"""

import subprocess
import sys
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python karen_research.py <topic>")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    queries = {
        "openclaw": "Research latest OpenClaw updates, features, and news",
        "ai_models": "Research latest AI model releases from OpenAI, Anthropic, Google, Meta",
        "philosophy": "Research personal growth insights from philosophers like Tolle, Watts, Osho",
        "income": "Research AI income opportunities and side hustle ideas"
    }
    
    if topic not in queries:
        print(f"Unknown topic: {topic}")
        sys.exit(1)
    
    # Send message to Karen via OpenClaw
    message = f"🔍 **Scheduled Research Task**: {topic}\n\n{queries[topic]}\n\nPlease use web_search to find current information and save results to memory/research/YYYY-MM-DD_{topic}.md"
    
    print(f"[{datetime.now()}] Sending research request to Karen: {topic}")
    
    # Use OpenClaw to send message
    ps_command = f'openclaw message send --text "{message}"'
    
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"✅ Request sent successfully")
        return True
    except Exception as e:
        print(f"❌ Error sending request: {e}")
        return False

if __name__ == "__main__":
    main()
