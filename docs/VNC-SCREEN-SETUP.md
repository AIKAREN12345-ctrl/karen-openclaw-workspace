# Enabling Node VNC Screen Recording

**Status:** Partially implemented — requires full node re-registration  
**Date:** 2026-03-21  
**Permission:** Granted by Ken

---

## Current State

✅ **VNC Server:** Running on localhost:5900  
✅ **VNC Password:** Set in VNC_PASS environment variable  
✅ **Screenshot Script:** `vnc-screenshot-robust.py` working  
✅ **Scheduled Task:** Modified with screen environment variables  
⏳ **Node Screen Capability:** Pending full re-registration

---

## What Was Done

1. Created `enable-vnc-screen.ps1` script
2. Modified the "OpenClaw Node" scheduled task to include:
   - `OPENCLAW_NODE_SCREEN_ENABLED=true`
   - `OPENCLAW_NODE_VNC_HOST=localhost`
   - `OPENCLAW_NODE_VNC_PORT=5900`
   - `OPENCLAW_NODE_VNC_PASSWORD` (from VNC_PASS)
3. Restarted the scheduled task

---

## Why It's Not Working Yet

The node capability list (`browser`, `system`, `screen`) is determined at **node registration time** when the node first connects to the gateway. The node needs to:
1. Fully disconnect from the gateway
2. Re-register with the new environment variables
3. Reconnect with the `screen` capability exposed

---

## To Complete

**Option 1: Full Restart (Recommended)**
```powershell
# Stop everything
openclaw gateway stop

# Wait 10 seconds

# Start with environment variables set
$env:OPENCLAW_NODE_SCREEN_ENABLED="true"
$env:OPENCLAW_NODE_VNC_HOST="localhost"
$env:OPENCLAW_NODE_VNC_PORT="5900"
$env:OPENCLAW_NODE_VNC_PASSWORD="Karen1234$"
openclaw gateway start
```

**Option 2: Wait for Next Reboot**
The scheduled task is now configured correctly. On next Windows login, the node should start with screen capability.

---

## Current Workaround

Until node screen is fully enabled, use:
- `vnc-screenshot-robust.py` for screenshots
- `vnc-recorder-robust.py` for screen recording

These work directly with the VNC server without needing the node capability.

---

## Verification

Once working, verify with:
```powershell
openclaw nodes describe DESKTOP-M8AO8LN
# Should show: caps: ["browser", "system", "screen"]

openclaw nodes screen_record --duration=5s
```