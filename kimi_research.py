#!/usr/bin/env python3
"""
Kimi Research Automation - Spawns Kimi subagents for research

This script spawns Kimi (K2.5) subagents that have full tool access
for web search, browsing, and research tasks.
"""

import subprocess
import sys
from datetime import datetime

def spawn_kimi_research(topic, query):
    """Spawn a Kimi subagent for research with full tool access."""
    
    task = f"""Research Task: {query}

Instructions:
1. Use web_search to find current information
2. Browse relevant websites if needed
3. Compile key findings with sources
4. Save results to: memory/research/YYYY-MM-DD_{topic}.md

Format:
- Bullet points with key information
- Include sources/URLs
- Be thorough but concise"""
    
    # Spawn Kimi subagent with full tool access
    ps_command = f'openclaw sessions spawn --mode run --model kimi-coding/k2p5 --timeout 300 --task "{task}"'
    
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"✅ Kimi subagent spawned for {topic}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python kimi_research.py <topic>")
        print("Topics: openclaw, ai_models, philosophy, income")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    queries = {
        "openclaw": "Latest OpenClaw updates, features, and news",
        "ai_models": "Latest AI model releases from OpenAI, Anthropic, Google, Meta",
        "philosophy": "Personal growth insights from philosophers like Tolle, Watts, Osho",
        "income": "AI income opportunities and side hustle ideas"
    }
    
    if topic not in queries:
        print(f"Unknown topic: {topic}")
        sys.exit(1)
    
    print(f"[{datetime.now()}] Spawning Kimi research subagent: {topic}")
    success = spawn_kimi_research(topic, queries[topic])
    
    if success:
        print(f"[{datetime.now()}] Subagent spawned - will auto-announce results")
    else:
        print(f"[{datetime.now()}] Failed to spawn subagent")
        sys.exit(1)

if __name__ == "__main__":
    main()
