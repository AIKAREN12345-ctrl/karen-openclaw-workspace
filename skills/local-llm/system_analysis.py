#!/usr/bin/env python3
"""
Detailed System Analysis
Comprehensive system check using actual data (no LLM)
"""

import datetime
import subprocess
import platform
import psutil
import json
import urllib.request

def get_system_info():
    """Get comprehensive system info"""
    info = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": platform.node(),
        "platform": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
    }
    
    # CPU info
    info['cpu_percent'] = psutil.cpu_percent(interval=1)
    info['cpu_count'] = psutil.cpu_count()
    
    # Memory info
    mem = psutil.virtual_memory()
    info['memory_total'] = f"{mem.total / (1024**3):.1f}GB"
    info['memory_used'] = f"{mem.used / (1024**3):.1f}GB"
    info['memory_percent'] = mem.percent
    
    # Disk info
    disk = psutil.disk_usage('/')
    info['disk_total'] = f"{disk.total / (1024**3):.1f}GB"
    info['disk_used'] = f"{disk.used / (1024**3):.1f}GB"
    info['disk_percent'] = disk.percent
    
    return info

def check_ollama_details():
    """Get Ollama details"""
    try:
        req = urllib.request.Request('http://localhost:11434/api/ps', method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            models = data.get('models', [])
            if models:
                return f"{len(models)} model(s) loaded: {', '.join(m['name'] for m in models)}"
            return "No models currently loaded"
    except:
        return "Ollama not responding"

def check_processes():
    """Check key processes"""
    processes = {}
    key_procs = ['node.exe', 'tvnserver.exe', 'ollama.exe']
    
    for proc in key_procs:
        try:
            result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {proc}'], 
                                  capture_output=True, text=True, timeout=5)
            if proc in result.stdout:
                processes[proc] = "running"
            else:
                processes[proc] = "not running"
        except:
            processes[proc] = "check failed"
    
    return processes

def main():
    """Main detailed analysis"""
    info = get_system_info()
    ollama_status = check_ollama_details()
    processes = check_processes()
    
    report = f"""Detailed System Analysis - {info['timestamp']}
================================================

SYSTEM INFO
-----------
Hostname: {info['hostname']}
Platform: {info['platform']} {info['release']} ({info['machine']})

RESOURCES
---------
CPU: {info['cpu_percent']}% used ({info['cpu_count']} cores)
Memory: {info['memory_used']} / {info['memory_total']} ({info['memory_percent']}%)
Disk: {info['disk_used']} / {info['disk_total']} ({info['disk_percent']}%)

SERVICES
--------
Ollama: {ollama_status}
Node.js (OpenClaw): {processes['node.exe']}
VNC Server: {processes['tvnserver.exe']}
Ollama Process: {processes['ollama.exe']}

OVERALL STATUS
--------------
{'System healthy' if info['memory_percent'] < 85 and info['disk_percent'] < 90 else 'Resource usage high'}
"""
    
    print(report)
    
    # Log to file
    with open('C:\\Users\\Karen\\.openclaw\\workspace\\logs\\system-analysis.log', 'a') as f:
        f.write(f"\n{report}\n{'='*60}\n")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
