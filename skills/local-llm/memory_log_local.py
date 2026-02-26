#!/usr/bin/env python3
"""
Local Memory Log Generator
Creates hourly memory logs using actual system data
No LLM generation - just factual reporting
"""

import datetime
import os
import sys
import subprocess
import platform

MEMORY_DIR = "C:\\Users\\Karen\\.openclaw\\workspace\\memory"

def get_system_info():
    """Get actual system info"""
    
    # Get Windows version properly
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
        winreg.CloseKey(key)
        windows_version = f"Windows 11 ({display_version})"
    except:
        windows_version = f"Windows {platform.release()}"
    
    info = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": platform.node(),
        "platform": windows_version,
        "machine": platform.machine(),
    }
    
    # Check Ollama status
    try:
        import urllib.request
        req = urllib.request.Request('http://localhost:11434/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            info["ollama_status"] = "running"
    except:
        info["ollama_status"] = "not responding"
    
    # Check OpenClaw node status (via process check)
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq node.exe'], 
                              capture_output=True, text=True, timeout=5)
        if 'node.exe' in result.stdout:
            info["openclaw_status"] = "running"
        else:
            info["openclaw_status"] = "no process found"
    except:
        info["openclaw_status"] = "check failed"
    
    return info

def format_log_entry(info):
    """Format system info into log entry - NO LLM, just facts"""
    
    lines = [
        f"**Timestamp:** {info['timestamp']}",
        f"**Hostname:** {info['hostname']}",
        f"**Platform:** {info['platform']} ({info['machine']})",
        f"**Ollama:** {info['ollama_status']}",
        f"**OpenClaw:** {info['openclaw_status']}",
        "",
        "System operational."
    ]
    
    return "\n".join(lines)

def write_memory_log(content):
    """Write to daily memory file"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(MEMORY_DIR, f"{today}.md")
    
    # Ensure directory exists
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    log_entry = f"\n## {timestamp} - Hourly Memory Log\n\n{content}\n\n---\n"
    
    # Append to file (create if doesn't exist)
    mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, mode, encoding='utf-8') as f:
        if mode == 'w':
            f.write(f"# Memory Log - {today}\n\n")
        f.write(log_entry)
    
    return filename

def main():
    """Main entry point"""
    try:
        # Get actual system info
        sys_info = get_system_info()
        
        # Format log entry (no LLM, just facts)
        content = format_log_entry(sys_info)
        
        # Write to memory file
        filename = write_memory_log(content)
        
        print(f"[OK] Memory log written to: {filename}")
        print(f"Method: Direct system data (no LLM generation)")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Failed to create memory log: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
