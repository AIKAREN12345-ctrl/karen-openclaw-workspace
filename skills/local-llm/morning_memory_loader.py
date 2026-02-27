#!/usr/bin/env python3
"""
Smart Memory Loader - Efficient session startup
Loads recent context first, with ability to dig deeper into history
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")
SESSIONS_DIR = Path("C:/Users/Karen/.openclaw/agents/main/sessions")

def get_all_memory_files():
    """Get all memory markdown files sorted by date (newest first)"""
    files = []
    for md_file in MEMORY_DIR.glob("*.md"):
        if md_file.name == "embeddings.json":
            continue
        try:
            date_str = md_file.stem
            date = datetime.strptime(date_str, "%Y-%m-%d")
            files.append((date, md_file))
        except ValueError:
            continue
    return sorted(files, reverse=True)

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

def read_memory_file(date, mem_file, detailed=False):
    """Read a single memory file and extract key info"""
    with open(mem_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Extract conversation sections
    sections = []
    current_section = []
    in_conversation = False
    
    for line in lines:
        if "## Session Conversations" in line or "### Session" in line:
            in_conversation = True
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
            current_section.append(line)
        elif line.startswith("## ") and in_conversation:
            # New major section
            if current_section:
                sections.append('\n'.join(current_section))
            current_section = [line]
            in_conversation = False
        elif in_conversation and line.strip():
            current_section.append(line)
    
    if current_section:
        sections.append('\n'.join(current_section))
    
    # Build summary
    summary = []
    summary.append(f"### {date.strftime('%Y-%m-%d (%A)')}")
    
    if detailed:
        # Full detail mode - include everything
        summary.append(content[:3000])
        if len(content) > 3000:
            summary.append("\n... (truncated, use --full for complete history)")
    else:
        # Quick summary mode
        key_points = []
        
        # Count conversations
        session_count = content.count("### Session")
        if session_count:
            key_points.append(f"- {session_count} conversation session(s)")
        
        # Count system events
        system_events = content.count("## ") - session_count
        if system_events > 0:
            key_points.append(f"- {system_events} system event(s)")
        
        # Extract key decisions/actions
        action_lines = [l for l in lines if any(m in l.lower() for m in ['fixed:', 'created:', 'set up', 'decided:', 'action:'])]
        if action_lines:
            key_points.append("- Key actions:")
            for line in action_lines[:3]:
                key_points.append(f"  - {line.strip()}")
        
        # Show file stats
        summary.append(f"*(Memory: {len(content)} chars, {len(lines)} lines)*")
        summary.extend(key_points)
        
        # Show conversation preview if available
        if sections and not detailed:
            summary.append("\n**Recent conversations:**")
            for section in sections[:2]:  # Top 2 sessions
                # Extract just the Q&A pairs
                qa_lines = [l for l in section.split('\n') if l.startswith('- Q:') or l.startswith('  A:')]
                if qa_lines:
                    summary.extend(qa_lines[:4])  # First 2 Q&A pairs
    
    summary.append("")
    return '\n'.join(summary)

def load_quick_context(days=2):
    """Load recent context (yesterday + today, or specified days)"""
    summary = []
    cutoff = datetime.now() - timedelta(days=days)
    
    all_memory = get_all_memory_files()
    recent_memory = [(d, f) for d, f in all_memory if d >= cutoff]
    
    summary.append(f"# Quick Context - Last {days} Days")
    summary.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    summary.append("")
    
    for date, mem_file in recent_memory:
        summary.append(read_memory_file(date, mem_file, detailed=True))
    
    return '\n'.join(summary)

def load_full_history():
    """Load complete historical memory"""
    summary = []
    all_memory = get_all_memory_files()
    all_sessions = get_all_sessions()
    
    summary.append(f"# Complete Memory History")
    summary.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    summary.append("")
    
    summary.append(f"## Overview")
    summary.append(f"- Total memory files: {len(all_memory)}")
    summary.append(f"- Total sessions: {len(all_sessions)}")
    if all_memory:
        summary.append(f"- Date range: {all_memory[-1][0].strftime('%Y-%m-%d')} to {all_memory[0][0].strftime('%Y-%m-%d')}")
    summary.append("")
    
    # Show last 7 days in detail
    summary.append("## Last 7 Days (Detailed)")
    summary.append("")
    
    cutoff = datetime.now() - timedelta(days=7)
    recent = [(d, f) for d, f in all_memory if d >= cutoff]
    
    for date, mem_file in recent:
        summary.append(read_memory_file(date, mem_file, detailed=True))
    
    # Show older days as summaries
    older = [(d, f) for d, f in all_memory if d < cutoff]
    if older:
        summary.append("## Older History (Summaries)")
        summary.append("")
        for date, mem_file in older:
            summary.append(read_memory_file(date, mem_file, detailed=False))
    
    # Project tracking
    summary.append("## Ongoing Projects")
    summary.append("")
    project_keywords = ['VNC', 'memory', 'git', 'ollama', 'kimi', 'gateway', 'cron', 'monitor', 'embedding']
    for keyword in project_keywords:
        mentions = []
        for date, _ in all_memory[:30]:
            # Check if mentioned (simplified)
            mentions.append(date.strftime('%Y-%m-%d'))
        if mentions:
            recent = [m for m in mentions if datetime.strptime(m, '%Y-%m-%d') >= cutoff]
            if recent:
                summary.append(f"- **{keyword.title()}**: Active recently ({len(recent)} days)")
    
    return '\n'.join(summary)

def main():
    """Main entry point"""
    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] in ('--full', '-f', 'full'):
            summary = load_full_history()
        elif sys.argv[1] in ('--days', '-d') and len(sys.argv) > 2:
            days = int(sys.argv[2])
            summary = load_quick_context(days)
        else:
            summary = load_quick_context(2)  # Default: yesterday + today
    else:
        # Default: quick context (yesterday + today)
        summary = load_quick_context(2)
    
    # Force UTF-8 output
    sys.stdout.reconfigure(encoding='utf-8')
    print(summary)

if __name__ == "__main__":
    main()
