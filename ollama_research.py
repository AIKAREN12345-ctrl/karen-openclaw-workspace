#!/usr/bin/env python3
"""
Ollama Research Automation

This script is called by cron jobs to perform automated research
using Ollama with Qwen 3.5 via OpenClaw subagents.
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

def spawn_research_subagent(topic, query):
    """Spawn a research subagent with Ollama."""
    
    # Create the subagent spawn command
    task = f"""Research: {query}

Use web_search to find current information. Format your findings as:
- Bullet points with key information
- Include sources where available
- Be concise but informative

Save results to memory/research/YYYY-MM-DD_{topic}.md"""
    
    # Use PowerShell to spawn subagent via OpenClaw
    escaped_task = task.replace('"', '\\"').replace("\n", " ")
    ps_command = f'openclaw sessions spawn --mode run --model ollama/qwen3.5:9b --timeout 300 --task "{escaped_task}"'
    
    cmd = ["powershell.exe", "-Command", ps_command]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"Subagent spawned for {topic}")
        return True
    except Exception as e:
        print(f"Error spawning subagent: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python ollama_research.py <topic>")
        print("Topics: openclaw, ai_models, philosophy, income")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    queries = {
        "openclaw": "Latest OpenClaw updates, features, and news",
        "ai_models": "Latest AI model releases from OpenAI, Anthropic, Google, Meta",
        "philosophy": "Personal growth insights from Eckhart Tolle, Alan Watts, Osho",
        "income": "AI income opportunities and side hustle ideas"
    }
    
    if topic not in queries:
        print(f"Unknown topic: {topic}")
        print(f"Available: {', '.join(queries.keys())}")
        sys.exit(1)
    
    print(f"[{datetime.now()}] Starting research: {topic}")
    success = spawn_research_subagent(topic, queries[topic])
    
    if success:
        print(f"[{datetime.now()}] Research subagent spawned successfully")
    else:
        print(f"[{datetime.now()}] Failed to spawn research subagent")
        sys.exit(1)

if __name__ == "__main__":
    main()
