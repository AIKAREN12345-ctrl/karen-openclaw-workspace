#!/usr/bin/env python3
"""
Session Archive System - Archives session history before daily cleanup
Replaces PowerShell script for better compatibility
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

def main():
    # Paths
    archive_root = Path("C:/Users/Karen/.openclaw/workspace/memory/session-archive")
    sessions_dir = Path("C:/Users/Karen/.openclaw/agents/main/sessions")
    
    # Date components
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    year = today.strftime("%Y")
    month_name = today.strftime("%m-%B")
    
    # Create directory structure
    archive_dir = archive_root / year / month_name / date_str
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Archiving sessions for {date_str} to {archive_dir}")
    
    # Copy session files (.jsonl format)
    sessions_copied = 0
    sessions_size = 0
    if sessions_dir.exists():
        sessions_archive_dir = archive_dir / "sessions"
        sessions_archive_dir.mkdir(exist_ok=True)
        
        for jsonl_file in sessions_dir.glob("*.jsonl"):
            if ".deleted." in jsonl_file.name:
                continue
            target_file = sessions_archive_dir / jsonl_file.name
            shutil.copy2(jsonl_file, target_file)
            sessions_copied += 1
            sessions_size += jsonl_file.stat().st_size
        
        if sessions_copied > 0:
            print(f"  {sessions_copied} session files ({sessions_size / 1024:.2f} KB)")
        else:
            print("  No session files found")
    else:
        print("  Sessions directory not found")
    
    # Create human-readable summary
    summary_file = archive_dir / "conversations.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"""# Conversation Archive - {date_str}

**Generated:** {timestamp}
**System:** OpenClaw on DESKTOP-M8AO8LN
**Sessions archived:** {sessions_copied}

## Sessions Summary

"""
    
    summary_file.write_text(header, encoding='utf-8')
    
    # Extract session info from the copied files
    if sessions_copied > 0:
        try:
            for jsonl_file in sorted(sessions_archive_dir.glob("*.jsonl")):
                # Get file modification time as session time
                mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
                session_time = mtime.strftime("%H:%M")
                
                # Extract session ID from filename
                session_id = jsonl_file.stem
                short_id = session_id[:8] if len(session_id) > 8 else session_id
                
                with open(summary_file, 'a', encoding='utf-8') as f:
                    f.write(f"- **{session_time}** - Session {short_id}...\n")
        except Exception as e:
            with open(summary_file, 'a', encoding='utf-8') as f:
                f.write(f"- Error reading session data: {e}\n")
    
    with open(summary_file, 'a', encoding='utf-8') as f:
        f.write("\n---\n*Full session data in sessions/ directory*\n")
    
    print("  conversations.md created")
    
    # Create search index
    index_file = archive_dir / "search-index.json"
    index = {
        "date": date_str,
        "timestamp": datetime.now().isoformat(),
        "sessions_copied": sessions_copied,
        "sessions_size_kb": round(sessions_size / 1024, 2),
        "topics": [],
        "projects": [],
        "files_modified": [],
        "keywords": []
    }
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    print("  search-index.json created")
    
    # Calculate totals
    archive_size = sum(f.stat().st_size for f in archive_dir.rglob('*') if f.is_file())
    print(f"Archive complete: {archive_size / 1024:.2f} KB")
    
    # Show storage summary
    total_used = sum(f.stat().st_size for f in archive_root.rglob('*') if f.is_file())
    total_gb = total_used / (1024 ** 3)
    print(f"Total archive usage: {total_gb:.3f} GB / ~1000 GB available")

if __name__ == "__main__":
    main()
