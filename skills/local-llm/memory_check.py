#!/usr/bin/env python3
"""
Memory Check Reminder
Daily reminder to review memory files and maintain continuity
"""

import datetime
import os

def check_memory_files():
    """Check if memory files exist and are up to date"""
    workspace = r"C:\Users\Karen\.openclaw\workspace"
    memory_dir = os.path.join(workspace, "memory")
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_file = os.path.join(memory_dir, f"{today}.md")
    
    files_to_check = [
        ("SESSION-START-CHECKLIST.md", "Mandatory session checklist"),
        ("MEMORY.md", "Long-term memory"),
        ("SOUL.md", "Identity file"),
        ("USER.md", "User preferences"),
        (today_file, "Today's memory log")
    ]
    
    missing = []
    for file_path, description in files_to_check:
        if not os.path.exists(file_path):
            missing.append(f" {description}: {file_path}")
        else:
            print(f" {description}: Found")
    
    if missing:
        print("\n  Missing files:")
        for item in missing:
            print(f"   {item}")
    else:
        print("\n All memory files present")
    
    # Reminder to read checklist
    print("\n REMINDER: Read SESSION-START-CHECKLIST.md at every session start!")
    print(" REMINDER: Check memory files for continuity!")
    
    return len(missing) == 0

if __name__ == "__main__":
    print(f"Memory Check - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    check_memory_files()
