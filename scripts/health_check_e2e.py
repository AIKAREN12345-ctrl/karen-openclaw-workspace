#!/usr/bin/env python3
"""
End-to-End Health Check for OpenClaw
Run this OUTSIDE of OpenClaw (e.g., via Task Scheduler) since exec blocks interpreters
"""

import json
import os
import sys
import glob
import psutil
from datetime import datetime
from pathlib import Path

def test_exec_working():
    """Test if file write/read works (simulating what OpenClaw exec does)"""
    test_file = Path.home() / ".openclaw" / "workspace" / f".health-test-{os.urandom(4).hex()}.txt"
    test_content = f"health-check-test-{datetime.now().isoformat()}"
    
    try:
        test_file.write_text(test_content, encoding='utf-8')
        written = test_file.read_text(encoding='utf-8').strip()
        test_file.unlink()
        
        if written == test_content:
            return {"name": "exec_write", "status": "PASS", "detail": "File write/read working"}
        return {"name": "exec_write", "status": "FAIL", "detail": "Content mismatch"}
    except Exception as e:
        return {"name": "exec_write", "status": "FAIL", "detail": str(e)}

def test_python_security():
    """Python is running, so this is just a sanity check"""
    return {"name": "python_security", "status": "INFO", "detail": "Python execution allowed (running outside sandbox)"}

def test_node_connection():
    """Check node config exists and looks valid"""
    node_config = Path.home() / ".openclaw" / "node.json"
    
    try:
        if node_config.exists():
            config = json.loads(node_config.read_text())
            node_id = config.get('id', 'unknown')
            return {"name": "node_config", "status": "PASS", "detail": f"Node config present, ID: {node_id[:16]}..."}
        return {"name": "node_config", "status": "FAIL", "detail": "node.json not found"}
    except Exception as e:
        return {"name": "node_config", "status": "FAIL", "detail": f"Invalid node.json: {e}"}

def test_orphaned_sessions():
    """Check for excessive sessions that could indicate orphan issues"""
    sessions_dir = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
    
    try:
        if sessions_dir.exists():
            # Count non-deleted, non-lock jsonl files
            session_files = [
                f for f in sessions_dir.glob("*.jsonl")
                if ".deleted." not in f.name and ".lock" not in f.name
            ]
            count = len(session_files)
            
            if count > 100:
                return {"name": "orphan_sessions", "status": "WARN", "detail": f"High session count: {count} (potential orphans)"}
            return {"name": "orphan_sessions", "status": "PASS", "detail": f"Session count normal: {count}"}
        return {"name": "orphan_sessions", "status": "FAIL", "detail": "Sessions directory not found"}
    except Exception as e:
        return {"name": "orphan_sessions", "status": "FAIL", "detail": str(e)}

def test_disk_space():
    """Check disk space on C:"""
    try:
        disk = psutil.disk_usage('C:')
        free_percent = round((disk.free / disk.total) * 100, 1)
        
        if free_percent < 10:
            return {"name": "disk_space", "status": "FAIL", "detail": f"Critical: {free_percent}% free"}
        elif free_percent < 20:
            return {"name": "disk_space", "status": "WARN", "detail": f"Low: {free_percent}% free"}
        return {"name": "disk_space", "status": "PASS", "detail": f"OK: {free_percent}% free"}
    except Exception as e:
        return {"name": "disk_space", "status": "FAIL", "detail": str(e)}

def test_ollama_status():
    """Check if Ollama is running"""
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            model_count = len([l for l in lines if l.strip() and not l.startswith('NAME')])
            return {"name": "ollama", "status": "PASS", "detail": f"Running with {model_count} models"}
        return {"name": "ollama", "status": "WARN", "detail": "Ollama installed but not responding"}
    except FileNotFoundError:
        return {"name": "ollama", "status": "FAIL", "detail": "Ollama not installed or not in PATH"}
    except Exception as e:
        return {"name": "ollama", "status": "WARN", "detail": f"Check failed: {e}"}

def test_gateway_running():
    """Check if OpenClaw gateway process is running"""
    try:
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] and 'openclaw' in proc.info['name'].lower():
                return {"name": "gateway_process", "status": "PASS", "detail": "OpenClaw gateway process found"}
        return {"name": "gateway_process", "status": "FAIL", "detail": "No OpenClaw gateway process found"}
    except Exception as e:
        return {"name": "gateway_process", "status": "WARN", "detail": f"Check failed: {e}"}

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    results = {
        "timestamp": timestamp,
        "tests": [],
        "overall": "PASS"
    }
    
    # Run all tests
    results["tests"].append(test_exec_working())
    results["tests"].append(test_python_security())
    results["tests"].append(test_node_connection())
    results["tests"].append(test_orphaned_sessions())
    results["tests"].append(test_disk_space())
    results["tests"].append(test_ollama_status())
    results["tests"].append(test_gateway_running())
    
    # Determine overall status
    failures = [t for t in results["tests"] if t["status"] == "FAIL"]
    warnings = [t for t in results["tests"] if t["status"] == "WARN"]
    
    if failures:
        results["overall"] = "FAIL"
    elif warnings:
        results["overall"] = "WARN"
    
    # Format output
    output_lines = [
        f"## Health Check - {timestamp}",
        "",
        f"**Overall: {results['overall']}**",
        "",
        "| Test | Status | Detail |",
        "|------|--------|--------|"
    ]
    
    for test in results["tests"]:
        emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "INFO": "ℹ️"}.get(test["status"], "❓")
        output_lines.append(f"| {test['name']} | {emoji} {test['status']} | {test['detail']} |")
    
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    
    output = "\n".join(output_lines)
    
    # Write to log
    log_file = Path.home() / ".openclaw" / "workspace" / "memory" / "health-checks.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(output)
    
    # Write JSON status for programmatic access
    status_file = Path.home() / ".openclaw" / "workspace" / ".health-status.json"
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(output)
    
    # Return exit code
    return 1 if results["overall"] == "FAIL" else 0

if __name__ == "__main__":
    sys.exit(main())
