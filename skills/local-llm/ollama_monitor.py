#!/usr/bin/env python3
"""
Ollama System Monitor
Background worker that monitors system health using Ollama for analysis
"""

import datetime
import os
import sys
import subprocess
import json
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "memory")

def query_ollama(prompt, model="qwen2.5:7b", timeout=30):
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
    """Get system health metrics"""
    metrics = {
        "timestamp": datetime.datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check Ollama
    try:
        req = urllib.request.Request('http://localhost:11434/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            models = json.loads(response.read().decode('utf-8'))
            metrics["checks"]["ollama"] = {
                "status": "running",
                "models": len(models.get('models', []))
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
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:")
        metrics["checks"]["disk"] = {
            "status": "ok" if (free / total) > 0.1 else "low",
            "free_gb": free // (2**30),
            "percent_used": (used / total) * 100
        }
    except Exception as e:
        metrics["checks"]["disk"] = {"status": "error", "error": str(e)}
    
    return metrics

def analyze_with_ollama(metrics):
    """Have Ollama analyze the metrics and provide insights"""
    
    # Build prompt for Ollama
    prompt = f"""Analyze this system health report and provide a brief summary (2-3 sentences).
Focus on any issues or concerning trends.

System Metrics:
{json.dumps(metrics, indent=2)}

Provide a concise status summary:"""
    
    analysis = query_ollama(prompt, timeout=30)
    return analysis

def write_monitoring_log(metrics, analysis):
    """Write monitoring results to memory"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(MEMORY_DIR, f"{today}.md")
    
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # Build status indicators
    status_icons = []
    for check, data in metrics["checks"].items():
        if data.get("status") == "running" or data.get("status") == "ok":
            status_icons.append(f" {check}")
        elif data.get("status") == "low":
            status_icons.append(f" {check}")
        else:
            status_icons.append(f" {check}")
    
    log_entry = f"""\n## {timestamp} - System Monitor (Ollama-Powered)

**Status:** {' | '.join(status_icons)}

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
        print("[INFO] Starting Ollama-powered system monitor...")
        
        # Get metrics
        metrics = get_system_metrics()
        print(f"[INFO] Collected metrics: {list(metrics['checks'].keys())}")
        
        # Analyze with Ollama
        print("[INFO] Querying Ollama for analysis...")
        analysis = analyze_with_ollama(metrics)
        print(f"[INFO] Ollama analysis received ({len(analysis)} chars)")
        
        # Write to memory
        filename = write_monitoring_log(metrics, analysis)
        print(f"[OK] Monitoring log written to: {filename}")
        
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
