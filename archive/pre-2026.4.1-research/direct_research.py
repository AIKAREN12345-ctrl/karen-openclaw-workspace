#!/usr/bin/env python3
"""
Direct Research Script - Uses Karen's tools instead of subagents

This script has Karen (Kimi) perform research directly using web_search,
then saves results to the research folder.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python direct_research.py <topic>")
        print("Topics: openclaw, ai_models, philosophy, income")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    queries = {
        "openclaw": "Latest OpenClaw updates features news 2026",
        "ai_models": "Latest AI model releases OpenAI Anthropic Google Meta April 2026",
        "philosophy": "Eckhart Tolle Alan Watts Osho personal growth teachings",
        "income": "AI side hustle opportunities make money 2026"
    }
    
    if topic not in queries:
        print(f"Unknown topic: {topic}")
        sys.exit(1)
    
    print(f"[{datetime.now()}] Requesting research: {topic}")
    print(f"Query: {queries[topic]}")
    print("\nNote: This script signals Karen to perform research.")
    print("Karen will use web_search and save results manually.")

if __name__ == "__main__":
    main()
