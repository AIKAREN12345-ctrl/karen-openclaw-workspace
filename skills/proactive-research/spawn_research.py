#!/usr/bin/env python3
"""
OpenClaw Research Subagent Spawner
Spawns isolated research subagents to continuously learn and populate memory.
Uses sessions_spawn via OpenClaw CLI tool.
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
AGENT_ID = "main"
MODEL = "ollama/qwen2.5:14b"
RESEARCH_TIMEOUT = 1800  # 30 minutes per research topic

# Research topics to cycle through
RESEARCH_TOPICS = [
    {
        "name": "system_improvements",
        "prompt": """Research the latest OpenClaw features, local LLM optimizations, 
        and system automation improvements. Focus on:
        - New OpenClaw capabilities and best practices
        - Local LLM performance tuning (Ollama, llama.cpp)
        - Windows automation and scripting improvements
        - Security hardening for personal AI systems
        
        Write findings to memory/research/system/{date}.md with actionable insights."""
    },
    {
        "name": "ai_developments", 
        "prompt": """Research latest AI/LLM developments and breakthroughs. Focus on:
        - New model releases and capabilities
        - AI agent frameworks and architectures
        - Local vs cloud AI tradeoffs
        - Emerging AI applications for personal use
        
        Write findings to memory/research/ai/{date}.md with summaries and implications."""
    },
    {
        "name": "passive_income",
        "prompt": """Research AI-powered passive income opportunities. Focus on:
        - AI content creation and monetization
        - Automation for service businesses
        - Niche AI tools and micro-SaaS ideas
        - Practical implementations for solo operators
        
        Write findings to memory/research/income/{date}.md with specific actionable ideas."""
    }
]

def spawn_research_subagent(topic):
    """Spawn a research subagent using openclaw CLI"""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    prompt = topic['prompt'].format(date=date_str)
    
    task = f"""You are a research subagent. Your task:

{prompt}

Rules:
1. Use web_search and web_fetch tools to find current information
2. Focus on practical, actionable insights
3. Write findings to the specified memory file
4. Be thorough but concise - quality over quantity
5. Cite sources where possible
6. Complete within 30 minutes

Start now."""

    # Build the openclaw command
    cmd = [
        "openclaw", "agent",
        "--agent", AGENT_ID,
        "--message", task,
        "--timeout", str(RESEARCH_TIMEOUT),
        "--thinking", "medium"
    ]
    
    try:
        print(f"Spawning research subagent: {topic['name']}")
        
        # Run the command - this creates a new session
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=RESEARCH_TIMEOUT + 60  # Add buffer
        )
        
        if result.returncode == 0:
            print(f"  ✓ {topic['name']} completed")
            return True
        else:
            print(f"  ✗ {topic['name']} failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ {topic['name']} timed out")
        return False
    except Exception as e:
        print(f"  ✗ {topic['name']} error: {e}")
        return False

def ensure_directories():
    """Ensure research memory directories exist"""
    base_path = Path.home() / ".openclaw" / "workspace" / "memory" / "research"
    for topic in RESEARCH_TOPICS:
        topic_path = base_path / topic["name"]
        topic_path.mkdir(parents=True, exist_ok=True)

def main():
    """Main entry point - spawn all research subagents sequentially"""
    print(f"=== Research Subagent Spawner ===")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    # Ensure directories exist
    ensure_directories()
    
    # Spawn all research subagents sequentially (to avoid overwhelming the system)
    results = []
    for topic in RESEARCH_TOPICS:
        success = spawn_research_subagent(topic)
        results.append(success)
        print()
    
    # Report results
    success_count = sum(results)
    print(f"Results: {success_count}/{len(RESEARCH_TOPICS)} research tasks completed")
    
    if success_count < len(RESEARCH_TOPICS):
        sys.exit(1)

if __name__ == "__main__":
    main()
