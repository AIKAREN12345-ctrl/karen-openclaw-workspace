#!/usr/bin/env python3
"""
Memory Maintenance Script - Runs via cron
Reviews daily logs and extracts important details for permanent memory
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

def extract_personal_details(log_content):
    """Extract personal details from daily log"""
    details = []
    
    # Look for personal information patterns
    patterns = [
        r'(?:Ken|you|your).{0,50}(?:said|mentioned|told me).{0,100}',
        r'(?:medical|health|diagnosis|medication).{0,100}',
        r'(?:family|wife|husband|partner|kids|children).{0,100}',
        r'(?:preference|likes|dislikes|hates|loves).{0,100}',
        r'(?:work|job|career|office).{0,100}',
        r'(?:home|house|living).{0,100}',
        r'(?:birthday|anniversary|important date).{0,100}',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, log_content, re.IGNORECASE)
        details.extend(matches)
    
    return list(set(details))  # Remove duplicates

def update_memory_md(new_details):
    """Append new details to MEMORY.md"""
    memory_path = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"
    
    if not memory_path.exists():
        return
    
    content = memory_path.read_text()
    
    # Add new details under User Profile section
    if "## User Profile - Ken" in content:
        # Find the section and append
        lines = content.split('\n')
        insert_idx = None
        for i, line in enumerate(lines):
            if line.startswith('## ') and 'User Profile' not in line and insert_idx is None:
                insert_idx = i
                break
        
        if insert_idx:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            new_section = f"\n### Auto-Extracted Details ({timestamp})\n"
            for detail in new_details[:10]:  # Limit to 10 items
                new_section += f"- {detail}\n"
            
            lines.insert(insert_idx, new_section)
            memory_path.write_text('\n'.join(lines))

def main():
    """Main maintenance routine"""
    # Get yesterday's log file
    yesterday = datetime.now() - timedelta(days=1)
    log_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{yesterday.strftime('%Y-%m-%d')}.md"
    
    if not log_file.exists():
        print(f"No log file for {yesterday.date()}")
        return
    
    log_content = log_file.read_text()
    personal_details = extract_personal_details(log_content)
    
    if personal_details:
        update_memory_md(personal_details)
        print(f"Updated MEMORY.md with {len(personal_details)} details")
    else:
        print("No new personal details found")

if __name__ == "__main__":
    main()
