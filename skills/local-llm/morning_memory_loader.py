#!/usr/bin/env python3
"""
Morning Memory Loader - Automated session startup
Reads all memory files and provides a summary without user prompting
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")
SESSIONS_DIR = Path("C:/Users/Karen/.openclaw/agents/main/sessions")

def get_recent_sessions(days=1):
    """Find session files from recent days"""
    cutoff = datetime.now() - timedelta(days=days)
    sessions = []
    
    for jsonl_file in SESSIONS_DIR.glob("*.jsonl"):
        if ".deleted." in jsonl_file.name:
            continue
        mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
        if mtime > cutoff:
            sessions.append((mtime, jsonl_file))
    
    return sorted(sessions, reverse=True)

def read_memory_summary():
    """Read and summarize recent memory files"""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    summary = []
    summary.append(f"# Morning Memory Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    summary.append("")
    
    # Read yesterday's memory
    yesterday_file = MEMORY_DIR / f"{yesterday}.md"
    if yesterday_file.exists():
        summary.append(f"## Yesterday ({yesterday})")
        with open(yesterday_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract conversation sections
            if "## Session Conversations" in content:
                conv_start = content.find("## Session Conversations")
                conv_section = content[conv_start:conv_start+2000]
                summary.append(conv_section)
            else:
                # Just show last few lines
                lines = content.split('\n')
                summary.append('\n'.join(lines[-30:]))
        summary.append("")
    
    # Read today's memory so far
    today_file = MEMORY_DIR / f"{today}.md"
    if today_file.exists():
        summary.append(f"## Today ({today}) - So far")
        with open(today_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            summary.append('\n'.join(lines[-20:]))
        summary.append("")
    
    # Count recent sessions
    recent_sessions = get_recent_sessions(2)
    summary.append(f"## Session Activity")
    summary.append(f"- Recent sessions (last 2 days): {len(recent_sessions)}")
    if recent_sessions:
        summary.append(f"- Last active: {recent_sessions[0][0].strftime('%Y-%m-%d %H:%M')}")
    summary.append("")
    
    return '\n'.join(summary)

def main():
    """Main entry point - print memory summary"""
    import sys
    summary = read_memory_summary()
    # Force UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    print(summary)

if __name__ == "__main__":
    main()
