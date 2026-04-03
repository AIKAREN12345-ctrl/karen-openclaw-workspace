#!/usr/bin/env python3
"""
Kimi Research Runner - Spawns subagents with Kimi for automated research
Called by cron jobs to run research without requiring main agent online
"""

import subprocess
import sys
import os
from datetime import datetime

# Research topics configuration
RESEARCH_TOPICS = {
    "openclaw": {
        "queries": [
            "OpenClaw updates 2026",
            "OpenClaw new features",
            "OpenClaw changelog"
        ],
        "filename": "openclaw"
    },
    "ai_models": {
        "queries": [
            "AI model releases April 2026",
            "new LLM announcements 2026",
            "GPT-5 Claude 4 Gemini updates"
        ],
        "filename": "ai_models"
    },
    "philosophy": {
        "queries": [
            "John Demartini personal growth",
            "Eckhart Tolle teachings 2026",
            "David Deida masculine feminine",
            "Alan Watts philosophy",
            "Bruce Lee philosophy",
            "Sun Tzu Art of War modern",
            "Osho meditation techniques"
        ],
        "filename": "philosophy"
    },
    "income": {
        "queries": [
            "AI passive income opportunities 2026",
            "AI side hustle ideas",
            "make money with AI tools"
        ],
        "filename": "income"
    }
}

def spawn_kimi_research(topic):
    """Spawn a Kimi subagent for research"""
    if topic not in RESEARCH_TOPICS:
        print(f"Unknown topic: {topic}")
        return False
    
    config = RESEARCH_TOPICS[topic]
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_file = f"memory/research/{date_str}_{config['filename']}.md"
    
    # Build search queries string
    queries_text = "\n".join([f'{i+1}. "{q}"' for i, q in enumerate(config['queries'])])
    
    # Create the task for the subagent
    task = f"""Research {topic.replace('_', ' ').title()} for {date_str}.

Search DuckDuckGo for:
{queries_text}

Use web_fetch with format: https://duckduckgo.com/html?q={{query}}
Fetch 2-3 interesting result pages per query.
Compile findings into a markdown summary with sources.

Save to: {output_file}
Use ONLY web_fetch, NOT web_search."""

    # Use openclaw CLI to spawn subagent with Kimi
    cmd = [
        "openclaw", "sessions", "spawn",
        "--runtime", "subagent",
        "--model", "kimi-coding/k2p5",
        "--mode", "run",
        "--timeout", "300",
        "--task", task
    ]
    
    print(f"Spawning Kimi subagent for {topic} research...")
    print(f"Output will be saved to: {output_file}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=310)
        print(f"Subagent exit code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Subagent timed out after 310 seconds")
        return False
    except Exception as e:
        print(f"Error spawning subagent: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kimi_research_runner.py <topic>")
        print(f"Available topics: {', '.join(RESEARCH_TOPICS.keys())}")
        sys.exit(1)
    
    topic = sys.argv[1]
    success = spawn_kimi_research(topic)
    sys.exit(0 if success else 1)
