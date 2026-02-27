# Karen Monitoring Agent

Autonomous monitoring and alerting system for Karen AI.

## What It Does

- Monitors Ollama, OpenClaw, VNC services
- Checks CPU, RAM, disk usage
- Alerts via Telegram when issues detected
- Logs all activity
- Runs continuously (24/7)

## Files

- `karen_monitor.py` - Main monitoring script
- `config.json` - Configuration (Telegram, thresholds)
- `setup_scheduled_task.ps1` - Install as Windows scheduled task
- `monitor.log` - Activity log
- `alerts.log` - Alert history

## Setup

1. **Configure Telegram:**
   Edit `config.json` with your bot token and chat ID

2. **Install:**
   ```powershell
   # Run as Administrator
   .\setup_scheduled_task.ps1
   ```

3. **Verify:**
   Check `monitor.log` for "Karen Monitoring Agent started"

## How It Works

Every 5 minutes:
1. Checks if Ollama is responding
2. Checks if OpenClaw node is running
3. Checks if VNC is running
4. Checks CPU/RAM/disk usage
5. Logs status
6. Sends Telegram alert if issues found

## Alerts

You'll get Telegram messages like:
```
 Ollama: Not responding
 OpenClaw: Process not found
 High RAM: 95%
```

## Autonomy Level

With this running, Karen can:
-  Detect issues automatically
-  Alert you immediately
-  Log everything for review
- ⏳ Auto-remediate (coming soon)
- ⏳ Spawn subagents to investigate (coming soon)

## Next Steps

1. Configure Telegram
2. Install scheduled task
3. Test by stopping a service
4. Verify alerts work

---
*This gives Karen true awareness - she'll know when things break and tell you.*
