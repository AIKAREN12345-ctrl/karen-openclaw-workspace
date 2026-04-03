#!/usr/bin/env python3
"""
LM Studio Research Runner - For OpenClaw Cron Jobs

This script is called by OpenClaw cron jobs to run automated research
using LM Studio's local API.

Usage: python lm_research_runner.py <topic>
Topics: openclaw, ai_models, philosophy, income
"""

import subprocess
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python lm_research_runner.py <topic>")
        sys.exit(1)
    
    topic = sys.argv[1]
    workspace = Path.home() / ".openclaw" / "workspace"
    script = workspace / "lm_studio_research.py"
    
    # Run the research script
    result = subprocess.run(
        ["python", str(script), topic],
        cwd=str(workspace),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
