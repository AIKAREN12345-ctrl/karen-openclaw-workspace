#!/usr/bin/env python3
"""
Ollama System Monitor - Enhanced Edition
Background worker that monitors system health using Ollama for intelligent analysis
Now with historical context and trend detection!
"""

import datetime
import os
import sys
import subprocess
import json
import urllib.request
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "memory")

def query_ollama(prompt, model="qwen2.5:14b", timeout=90):
    """Query Ollama for analysis"""
    try:
        data = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'http://localhost:11434/api/chat',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('message', {}).get('content', 'No response')
    except Exception as e:
        return f"Error: {str(e)}"

def get_system_metrics():
    """Get comprehensive system health metrics"""
    metrics = {
        "timestamp": datetime.datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check Ollama
    try:
        req = urllib.request.Request('http://localhost:11434/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            models = json.loads(response.read().decode('utf-8'))
            model_list = [m.get('name', 'unknown') for m in models.get('models', [])]
            metrics["checks"]["ollama"] = {
                "status": "running",
                "models_count": len(model_list),
                "models": model_list
            }
    except Exception as e:
        metrics["checks"]["ollama"] = {"status": "error", "error": str(e)}
    
    # Check OpenClaw gateway
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq node.exe'],
            capture_output=True, text=True, timeout=5
        )
        if 'node.exe' in result.stdout:
            metrics["checks"]["openclaw"] = {"status": "running"}
        else:
            metrics["checks"]["openclaw"] = {"status": "stopped"}
    except Exception as e:
        metrics["checks"]["openclaw"] = {"status": "error", "error": str(e)}
    
    # Check VNC
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq tvnserver.exe'],
            capture_output=True, text=True, timeout=5
        )
        if 'tvnserver.exe' in result.stdout:
            metrics["checks"]["vnc"] = {"status": "running"}
        else:
            metrics["checks"]["vnc"] = {"status": "stopped"}
    except Exception as e:
        metrics["checks"]["vnc"] = {"status": "error", "error": str(e)}
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:")
        metrics["checks"]["disk"] = {
            "status": "ok" if (free / total) > 0.1 else "low",
            "free_gb": round(free / (2**30), 1),
            "used_gb": round(used / (2**30), 1),
            "total_gb": round(total / (2**30), 1),
            "percent_used": round((used / total) * 100, 1)
        }
    except Exception as e:
        metrics["checks"]["disk"] = {"status": "error", "error": str(e)}
    
    # Get CPU and Memory info
    try:
        result = subprocess.run(
            ['wmic', 'cpu', 'get', 'loadpercentage', '/value'],
            capture_output=True, text=True, timeout=5
        )
        cpu_match = re.search(r'LoadPercentage=(\d+)', result.stdout)
        cpu_percent = int(cpu_match.group(1)) if cpu_match else None
        
        result = subprocess.run(
            ['wmic', 'computersystem', 'get', 'TotalPhysicalMemory', '/value'],
            capture_output=True, text=True, timeout=5
        )
        mem_match = re.search(r'TotalPhysicalMemory=(\d+)', result.stdout)
        total_mem = int(mem_match.group(1)) / (2**30) if mem_match else None
        
        metrics["checks"]["resources"] = {
            "cpu_percent": cpu_percent,
            "total_memory_gb": round(total_mem, 1) if total_mem else None
        }
    except Exception as e:
        metrics["checks"]["resources"] = {"status": "error", "error": str(e)}
    
    return metrics

def get_historical_context(num_entries=5):
    """Read previous monitoring entries for trend analysis"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(MEMORY_DIR, f"{today}.md")
    
    if not os.path.exists(filename):
        return "No previous entries today."
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all Ollama analysis entries
        entries = []
        pattern = r'## (\d{2}:\d{2}) - System Monitor.*?\*\*Ollama Analysis:\*\*\n(.*?)(?=\n\n---|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for time, analysis in matches[-num_entries:]:
            entries.append(f"[{time}] {analysis.strip()}")
        
        if not entries:
            return "No previous monitor entries found today."
        
        return "\n".join(entries)
    except Exception as e:
        return f"Could not read history: {str(e)}"

def analyze_with_ollama(metrics, history):
    """Have Ollama analyze metrics with historical context"""
    
    # Build comprehensive prompt
    prompt = f"""You are a system monitoring AI. Analyze the current system state and provide insights.

CURRENT SYSTEM METRICS:
{json.dumps(metrics['checks'], indent=2)}

PREVIOUS ANALYSES TODAY:
{history}

INSTRUCTIONS:
1. Compare current state to previous readings if available
2. Identify any trends (improving, stable, degrading)
3. Note any anomalies or concerns
4. Give specific recommendations if action is needed
5. Keep response to 3-4 sentences maximum
6. Be precise - avoid vague "monitoring recommended" statements

Provide your analysis:"""
    
    analysis = query_ollama(prompt, timeout=60)
    return analysis

def write_monitoring_log(metrics, analysis):
    """Write monitoring results to memory with enhanced formatting"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(MEMORY_DIR, f"{today}.md")
    
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # Build status indicators with emojis
    status_icons = []
    for check, data in metrics["checks"].items():
        if check == "resources":
            continue
        status = data.get("status", "unknown")
        if status == "running" or status == "ok":
            status_icons.append(f"OK {check}")
        elif status == "low":
            status_icons.append(f"WARN {check}")
        elif status == "stopped":
            status_icons.append(f"FAIL {check}")
        else:
            status_icons.append(f"WARN {check}")
    
    # Extract key metrics for summary
    disk_info = metrics["checks"].get("disk", {})
    ollama_info = metrics["checks"].get("ollama", {})
    
    log_entry = f"""
## {timestamp} - System Monitor (Ollama-Powered) 

**Status:** {' | '.join(status_icons)}

**Quick Stats:**
- Disk: {disk_info.get('free_gb', '?')}GB free / {disk_info.get('total_gb', '?')}GB total ({disk_info.get('percent_used', '?')}% used)
- Ollama: {ollama_info.get('models_count', '?')} models available

**Ollama Analysis:**
{analysis}

---
"""
    
    mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, mode, encoding='utf-8') as f:
        if mode == 'w':
            f.write(f"# Memory Log - {today}\n\n")
        f.write(log_entry)
    
    return filename

def main():
    """Main entry point"""
    try:
        print("[INFO] Starting enhanced Ollama system monitor...")
        
        # Get metrics
        metrics = get_system_metrics()
        print(f"[INFO] Collected metrics: {list(metrics['checks'].keys())}")
        
        # Get historical context
        print("[INFO] Reading historical context...")
        history = get_historical_context(num_entries=5)
        
        # Analyze with Ollama
        print("[INFO] Querying Ollama for intelligent analysis...")
        analysis = analyze_with_ollama(metrics, history)
        print(f"[INFO] Ollama analysis received ({len(analysis)} chars)")
        
        # Write to memory
        filename = write_monitoring_log(metrics, analysis)
        print(f"[OK] Enhanced monitoring log written to: {filename}")
        
        return 0
        
    except Exception as e:
        error_msg = f"[ERROR] Monitor failed: {str(e)}"
        print(error_msg, file=sys.stderr)
        
        # Write error to debug file
        try:
            debug_file = os.path.join(MEMORY_DIR, "monitor_errors.log")
            with open(debug_file, 'a') as f:
                f.write(f"{datetime.datetime.now()}: {error_msg}\n")
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

