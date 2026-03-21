# Enabling Node VNC Screen Recording

**Status:** Pending node restart with screen capability enabled  
**Date:** 2026-03-21  
**Permission:** Granted by Ken

---

## Current State

✅ **VNC Server:** Running on localhost:5900  
✅ **VNC Password:** Set in VNC_PASS environment variable  
✅ **Screenshot Script:** `vnc-screenshot-robust.py` working  
❌ **Node Screen Capability:** Not exposed (can't use `nodes screen_record`)

---

## The Problem

OpenClaw nodes expose capabilities like `browser`, `system`, `screen`, etc. Currently our node only shows:
- `browser`
- `system`

The `screen` capability (which enables `nodes screen_record`, `nodes camera_snap`, etc.) is not enabled.

---

## Solution

The node needs to be started with screen recording enabled. This typically requires:

### Option 1: Environment Variables (Recommended)

Set these before starting the OpenClaw node:

```powershell
$env:OPENCLAW_NODE_SCREEN_ENABLED = "true"
$env:OPENCLAW_NODE_VNC_HOST = "localhost"
$env:OPENCLAW_NODE_VNC_PORT = "5900"
$env:OPENCLAW_NODE_VNC_PASSWORD = $env:VNC_PASS
```

Then restart the OpenClaw node/gateway.

### Option 2: Node Config File

Add to `node.json`:

```json
{
  "capabilities": {
    "screen": {
      "enabled": true,
      "vnc": {
        "host": "localhost",
        "port": 5900,
        "password": "${VNC_PASS}"
      }
    }
  }
}
```

### Option 3: Command Line Flags

If starting OpenClaw manually:

```powershell
openclaw node --screen --vnc-host=localhost --vnc-port=5900
```

---

## Verification Steps

After restart, verify with:

```powershell
# Check node capabilities
openclaw nodes describe DESKTOP-M8AO8LN

# Should show: caps: ["browser", "system", "screen"]

# Test screen recording
openclaw nodes screen_record --duration=5s
```

---

## Current Workaround

Until node screen is enabled, use:
- `vnc-screenshot-robust.py` for screenshots
- `vnc-recorder-robust.py` for screen recording

These work directly with the VNC server without needing the node capability.

---

## Next Steps

1. **Choose method** (environment variables recommended)
2. **Restart OpenClaw node/gateway**
3. **Verify screen capability appears**
4. **Test screen_record command**
5. **Update MEMORY.md** to mark complete

---

## Notes

- VNC server must be running before node starts
- Password should match VNC_PASS environment variable
- Screen recording requires sufficient disk space
- Recordings are temporary unless saved to workspace
