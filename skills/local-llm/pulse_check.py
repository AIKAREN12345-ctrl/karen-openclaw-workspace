#!/usr/bin/env python3
"""
System Pulse Check - Light Automation
Quick system status check using actual data (no LLM)
"""

import datetime
import subprocess
import platform
import urllib.request
import json

def check_services():
    """Check essential services"""
    services = {}
    
    # Check Ollama
    try:
        req = urllib.request.Request('http://localhost:11434/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            services['ollama'] = f"running ({len(data.get('models', []))} models)"
    except:
        services['ollama'] = "down"
    
    # Check OpenClaw (node process)
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq node.exe'], 
                              capture_output=True, text=True, timeout=5)
        if 'node.exe' in result.stdout:
            services['openclaw'] = "running"
        else:
            services['openclaw'] = "down"
    except:
        services['openclaw'] = "unknown"
    
    # Check VNC
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq tvnserver.exe'], 
                              capture_output=True, text=True, timeout=5)
        if 'tvnserver.exe' in result.stdout:
            services['vnc'] = "running"
        else:
            services['vnc'] = "down"
    except:
        services['vnc'] = "unknown"
    
    return services

def main():
    """Main pulse check"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    services = check_services()
    
    report = f"""System Pulse Check - {timestamp}

Services:
- Ollama: {services['ollama']}
- OpenClaw: {services['openclaw']}
- VNC: {services['vnc']}

Status: {'All systems operational' if all(s != 'down' for s in services.values()) else 'Some services down'}
"""
    
    print(report)
    
    # Log to file
    with open('C:\\Users\\Karen\\.openclaw\\workspace\\logs\\pulse-checks.log', 'a') as f:
        f.write(f"\n{report}\n{'='*50}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
