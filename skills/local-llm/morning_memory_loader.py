#!/usr/bin/env python3
"""
Morning Memory Loader - Automated session startup
Reads ALL memory files and provides comprehensive summary
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")
SESSIONS_DIR = Path("C:/Users/Karen/.openclaw/agents/main/sessions")

def get_all_memory_files():
    """Get all memory markdown files sorted by date"""
    files = []
    for md_file in MEMORY_DIR.glob("*.md"):
        if md_file.name == "embeddings.json":
            continue
        try:
            # Extract date from filename (YYYY-MM-DD.md)
            date_str = md_file.stem
            date = datetime.strptime(date_str, "%Y-%m-%d")
            files.append((date, md_file))
        except ValueError:
            continue
    return sorted(files, reverse=True)  # Most recent first

def get_all_sessions():
    """Get all session files with metadata"""
    sessions = []
    for jsonl_file in SESSIONS_DIR.glob("*.jsonl"):
        if ".deleted." in jsonl_file.name:
            continue
        try:
            mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            sessions.append((mtime, jsonl_file))
        except:
            continue
    return sorted(sessions, reverse=True)

def extract_key_topics(content, max_lines=50):
    """Extract key topics and decisions from memory content"""
    lines = content.split('\n')
    
    # Look for important markers
    key_sections = []
    current_section = []
    
    for line in lines:
        # Capture section headers
        if line.startswith('##') or line.startswith('###'):
            if current_section:
                key_sections.append('\n'.join(current_section))
                current_section = []
            current_section.append(line)
        # Capture action items
        elif any(marker in line.lower() for marker in ['action:', 'decided:', 'fixed:', 'created:', 'set up']):
            current_section.append(line)
        # Capture key exchanges
        elif line.startswith('- Q:') or line.startswith('  A:'):
            current_section.append(line)
    
    if current_section:
        key_sections.append('\n'.join(current_section))
    
    # Return truncated summary
    summary = '\n\n'.join(key_sections[:5])  # Top 5 sections
    if len(summary) > 3000:
        summary = summary[:3000] + "\n\n... (truncated)"
    return summary

def read_full_memory_summary():
    """Read and summarize ALL memory files"""
    summary = []
    summary.append(f"# Complete Memory Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    summary.append("")
    
    # Get all memory files
    all_memory = get_all_memory_files()
    all_sessions = get_all_sessions()
    
    summary.append(f"## Overview")
    summary.append(f"- Total memory files: {len(all_memory)}")
    summary.append(f"- Total sessions: {len(all_sessions)}")
    summary.append(f"- Memory date range: {all_memory[-1][0].strftime('%Y-%m-%d')} to {all_memory[0][0].strftime('%Y-%m-%d')}" if all_memory else "- No memory files")
    summary.append("")
    
    # Read last 7 days in detail
    summary.append(f"## Recent Activity (Last 7 Days)")
    summary.append("")
    
    cutoff_date = datetime.now() - timedelta(days=7)
    recent_memories = [(d, f) for d, f in all_memory if d >= cutoff_date]
    
    for date, mem_file in recent_memories[:7]:  # Last 7 days max
        summary.append(f"### {date.strftime('%Y-%m-%d (%A)')}")
        
        with open(mem_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key topics
        key_content = extract_key_topics(content)
        if key_content:
            summary.append(key_content)
        else:
            # Fallback: show file size and last lines
            lines = content.split('\n')
            summary.append(f"*(File: {len(content)} chars, {len(lines)} lines)*")
            if len(lines) > 10:
                summary.append("Last entries:")
                summary.append('\n'.join(lines[-10:]))
        
        summary.append("")
    
    # Key projects and ongoing work
    summary.append("## Key Projects & Ongoing Work")
    summary.append("")
    
    # Scan all memory for project mentions
    project_keywords = ['VNC', 'memory', 'git', 'ollama', 'kimi', 'gateway', 'cron', 'monitor']
    project_mentions = {k: [] for k in project_keywords}
    
    for date, mem_file in all_memory[:30]:  # Check last 30 days
        with open(mem_file, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        for keyword in project_keywords:
            if keyword in content:
                project_mentions[keyword].append(date.strftime('%Y-%m-%d'))
    
    for keyword, dates in project_mentions.items():
        if dates:
            recent_dates = dates[:5]  # Last 5 mentions
            summary.append(f"- **{keyword.title()}**: Active on {', '.join(recent_dates)}")
    
    summary.append("")
    
    # Session activity summary
    summary.append("## Session Statistics")
    recent_sessions = [s for s in all_sessions if s[0] >= cutoff_date]
    summary.append(f"- Sessions in last 7 days: {len(recent_sessions)}")
    if all_sessions:
        summary.append(f"- First session: {all_sessions[-1][0].strftime('%Y-%m-%d')}")
        summary.append(f"- Most recent: {all_sessions[0][0].strftime('%Y-%m-%d %H:%M')}")
    summary.append("")
    
    return '\n'.join(summary)

def main():
    """Main entry point - print comprehensive memory summary"""
    import sys
    summary = read_full_memory_summary()
    # Force UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    print(summary)

if __name__ == "__main__":
    main()
