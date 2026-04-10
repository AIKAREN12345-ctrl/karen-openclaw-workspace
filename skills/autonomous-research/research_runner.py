#!/usr/bin/env python3
"""
Karen Research Runner - Manual research execution
Uses Kimi subagents instead of Ollama (sandboxed in 2026.4.x)
"""

import subprocess
import sys
from datetime import datetime

def run_research(topic, query):
    """Run a research task using Kimi subagent"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"memory/research/{timestamp}_{topic.replace(' ', '_').lower()}.md"
    
    # Create research prompt
    prompt = f"""Research the topic: {topic}

Search query: {query}

Instructions:
1. Search the web for current information on this topic
2. Fetch 2-3 relevant pages
3. Compile key findings with sources
4. Save to {filename}

Format:
## {topic} Research - {datetime.now().strftime("%Y-%m-%d %H:%M")}

### Key Findings
- Finding 1 (with source)
- Finding 2 (with source)
- Finding 3 (with source)

### Sources
- [Title](URL)
- [Title](URL)
"""
    
    print(f"Starting research: {topic}")
    print(f"Output: {filename}")
    
    # Spawn subagent via OpenClaw
    result = subprocess.run(
        ["openclaw", "sessions", "spawn", 
         "--model", "kimi-coding/k2p5",
         "--timeout", "300",
         "--", prompt],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Research complete: {filename}")
    else:
        print(f"❌ Research failed: {result.stderr}")
    
    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python research_runner.py <topic> <query>")
        print("Example: python research_runner.py 'AI Models' 'latest AI model releases 2026'")
        sys.exit(1)
    
    topic = sys.argv[1]
    query = sys.argv[2]
    
    success = run_research(topic, query)
    sys.exit(0 if success else 1)
