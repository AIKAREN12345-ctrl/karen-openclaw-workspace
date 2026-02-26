#!/usr/bin/env python3
"""
Karen Monitoring Agent
Autonomous monitoring and alerting system
"""

import time
import json
import urllib.request
import subprocess
import platform
import datetime
import os
import sys

# Config
CONFIG_FILE = "C:\\Users\\Karen\\.openclaw\\workspace\\monitoring\\config.json"
LOG_FILE = "C:\\Users\\Karen\\.openclaw\\workspace\\monitoring\\monitor.log"
ALERT_LOG = "C:\\Users\\Karen\\.openclaw\\workspace\\monitoring\\alerts.log"
CHECK_INTERVAL = 60  # Check every minute

# Telegram config (will be set by user)
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

def load_config():
    """Load monitoring config"""
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            TELEGRAM_BOT_TOKEN = config.get('telegram_bot_token')
            TELEGRAM_CHAT_ID = config.get('telegram_chat_id')
    except:
        pass

def log_message(msg, level="INFO"):
    """Log to file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {msg}\n"
    
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())

def send_telegram_alert(message):
    """Send alert via Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log_message("Telegram not configured, can't send alert", "WARNING")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }).encode()
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        log_message(f"Failed to send Telegram alert: {e}", "ERROR")
        return False

def check_ollama():
    """Check if Ollama is running"""
    try:
        req = urllib.request.Request('http://localhost:11434/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            return True, "Running"
    except:
        return False, "Not responding"

def check_openclaw():
    """Check if OpenClaw node is running"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq node.exe'], 
                              capture_output=True, text=True, timeout=5)
        if 'node.exe' in result.stdout:
            return True, "Running"
        return False, "Process not found"
    except Exception as e:
        return False, f"Check failed: {e}"

def check_vnc():
    """Check if VNC is running"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq tvnserver.exe'], 
                              capture_output=True, text=True, timeout=5)
        if 'tvnserver.exe' in result.stdout:
            return True, "Running"
        return False, "Process not found"
    except Exception as e:
        return False, f"Check failed: {e}"

def check_resources():
    """Check system resources"""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        alerts = []
        if cpu > 90:
            alerts.append(f"High CPU: {cpu}%")
        if mem.percent > 90:
            alerts.append(f"High RAM: {mem.percent}%")
        if disk.percent > 90:
            alerts.append(f"High Disk: {disk.percent}%")
        
        return len(alerts) == 0, alerts
    except:
        return True, []

def check_cron_jobs():
    """Check if recent cron jobs have run"""
    # This would check log timestamps
    # For now, simplified
    return True, []

def perform_checks():
    """Perform all monitoring checks"""
    issues = []
    
    # Check services
    ollama_ok, ollama_status = check_ollama()
    if not ollama_ok:
        issues.append(f"🚨 Ollama: {ollama_status}")
    
    openclaw_ok, openclaw_status = check_openclaw()
    if not openclaw_ok:
        issues.append(f"🚨 OpenClaw: {openclaw_status}")
    
    vnc_ok, vnc_status = check_vnc()
    if not vnc_ok:
        issues.append(f"⚠️ VNC: {vnc_status}")
    
    # Check resources
    resources_ok, resource_alerts = check_resources()
    if not resources_ok:
        issues.extend(resource_alerts)
    
    return issues

def handle_issues(issues):
    """Handle detected issues"""
    if not issues:
        return
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_msg = f"*Karen Alert - {timestamp}*\n\n" + "\n".join(issues)
    
    # Log alert
    with open(ALERT_LOG, 'a') as f:
        f.write(f"{timestamp}: {issues}\n")
    
    # Send Telegram alert
    send_telegram_alert(alert_msg)
    
    # TODO: Add auto-remediation logic here
    # - Try to restart services
    # - Spawn subagent to investigate
    # - Wake main agent for critical issues

def main():
    """Main monitoring loop"""
    load_config()
    
    log_message("Karen Monitoring Agent started")
    log_message(f"Check interval: {CHECK_INTERVAL} seconds")
    
    while True:
        try:
            issues = perform_checks()
            
            if issues:
                log_message(f"Issues detected: {issues}", "WARNING")
                handle_issues(issues)
            else:
                log_message("All systems healthy", "DEBUG")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log_message("Monitoring stopped by user")
            break
        except Exception as e:
            log_message(f"Error in monitoring loop: {e}", "ERROR")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
